import JSZip from 'jszip';
import * as XLSX from 'xlsx';
import initSqlJs from 'sql.js';
import { TripRecord } from '../data/initialTrips';

const FYN_VEHICLE_ID = 'cf8b32c2-de2b-4d81-b025-601c4b1ca8f8';

const PLACE_MAP: Record<string, { full: string; placeId: string }> = {
  SevenHills: {
    full: 'Five Senses Education, Prospect Highway, Seven Hills NSW, Australia',
    placeId: 'ChIJlUJc746YEmsRGPRjlM8FqMU',
  },
  Lidcombe: {
    full: 'KMALL09 LIDCOMBE, Shopping Centre, Parramatta Road, Lidcombe NSW, Australia',
    placeId: 'ChIJEYUFFaq7EmsR3XvEP5SDUug',
  },
  IKEA: {
    full: 'IKEA Marsden Park, Hollinsworth Road, Marsden Park NSW, Australia',
    placeId: 'ChIJY4X0MGycEmsRon9gatPnJgM',
  },
  Costco: {
    full: 'Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW, Australia',
    placeId: 'ChIJH8Kj9F-dEmsRR5dZ0G-b1g4',
  },
  Parramatta: {
    full: 'Edu-Kingdom College, Sorrell Street, Parramatta NSW, Australia',
    placeId: 'ChIJc0LXTxujEmsRmhrB29XeVnQ',
  },
  Penrith: {
    full: 'Edu-Kingdom College, High Street, Penrith NSW, Australia',
    placeId: 'ChIJOfWVTouFEmsRZfOG9q9DAnE',
  },
};

function resolvePlace(locStr: string) {
  const s = locStr.toLowerCase();
  if (s.includes('seven hills')) return PLACE_MAP.SevenHills;
  if (s.includes('lidcombe') || s.includes('kmall')) return PLACE_MAP.Lidcombe;
  if (s.includes('ikea')) return PLACE_MAP.IKEA;
  if (s.includes('costco')) return PLACE_MAP.Costco;
  if (s.includes('parramatta')) return PLACE_MAP.Parramatta;
  return PLACE_MAP.Penrith;
}

// Convert DD/MM/YYYY to .NET ticks
function dateToTicks(dateStr: string): string {
  try {
    const [day, month, year] = dateStr.split('/').map(Number);
    const dt = new Date(Date.UTC(year, month - 1, day, 0, 0, 0));
    // .NET epoch is 0001-01-01 00:00:00 UTC
    // JS epoch is 1970-01-01 00:00:00 UTC (difference is 62,135,596,800 seconds)
    const epochOffsetSeconds = 62135596800n;
    const jsSeconds = BigInt(Math.floor(dt.getTime() / 1000));
    const ticks = (jsSeconds + epochOffsetSeconds) * 10000000n;
    return ticks.toString();
  } catch {
    return '639131904000000000';
  }
}

// Generate CSV and trigger browser download
export function downloadCSV(trips: TripRecord[], filename = 'FYN93N_ATO_Logbook.csv') {
  const headers = [
    'Uploaded',
    'Type',
    'Status',
    'Date',
    'Vehicle',
    'Purpose of trip',
    'Start odometer*',
    'End odometer*',
    'Start location#',
    'End location#',
    'Trip details',
    'Trip distance*',
    'Record multiple trips*',
    'Record the return journey*',
    'Total Km',
    'Logbook trip',
  ];

  const rows = trips.map((t) => [
    'Not uploaded',
    'Employee',
    'Completed',
    t.date,
    'FYN93N',
    'Employee - work',
    t.startOdometer ? String(t.startOdometer) : '',
    t.endOdometer ? String(t.endOdometer) : '',
    `"${t.startLocation.replace(/"/g, '""')}"`,
    `"${t.endLocation.replace(/"/g, '""')}"`,
    `"${t.tripDetails.replace(/"/g, '""')}"`,
    t.tripDistance.toFixed(2),
    '1',
    t.returnJourney ? 'Yes' : 'No',
    t.totalKm.toFixed(2),
    'Y',
  ]);

  const csvContent = '\uFEFF' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// Generate Excel and trigger browser download
export function downloadExcel(trips: TripRecord[], filename = 'FYN93N_ATO_Logbook.xlsx') {
  const data = trips.map((t, idx) => ({
    'No.': idx + 1,
    'Date': t.date,
    'Vehicle': 'FYN93N',
    'Start Location': t.startLocation,
    'End Location': t.endLocation,
    'Trip Details': t.tripDetails,
    'Distance (km)': t.tripDistance,
    'Return Trip': t.returnJourney ? 'Yes' : 'No',
    'Total Distance (km)': t.totalKm,
    'Start Odometer': t.startOdometer || '',
    'End Odometer': t.endOdometer || '',
    'Purpose': 'Employee - work',
  }));

  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'FYN93N Logbook');
  XLSX.writeFile(workbook, filename);
}

// Generate updated ATO_Backup.ato SQLite DB & Package into ReadyToRestore.zip
export async function generateUpdatedAtoZip(
  trips: TripRecord[],
  onProgress?: (status: string) => void
): Promise<void> {
  if (onProgress) onProgress('SQLite 엔진 초기화 중...');

  const SQL = await initSqlJs({
    locateFile: () => '/sql-wasm.wasm',
  });

  if (onProgress) onProgress('기존 ATO 데이터베이스 템플릿 로딩 중...');
  const response = await fetch('/ATO_Backup.ato');
  if (!response.ok) {
    throw new Error('ATO_Backup.ato 템플릿을 불러올 수 없습니다.');
  }
  const buf = await response.arrayBuffer();
  const db = new SQL.Database(new Uint8Array(buf));

  if (onProgress) onProgress('차량 정보 및 기존 기록 동기화 중...');
  // Ensure FYN93N purchase date is 2026-05-01
  const purchaseTicks = '639131904000000000';
  db.run(
    `UPDATE VehicleModel 
     SET VehicleAddedDate = ?, VehiclePurchaseDate = ?, LastModified = ? 
     WHERE _id = ?`,
    [purchaseTicks, purchaseTicks, purchaseTicks, FYN_VEHICLE_ID]
  );

  // Delete previous FYN93N trips
  db.run(`DELETE FROM TripModel WHERE VehicleId = ?`, [FYN_VEHICLE_ID]);

  if (onProgress) onProgress(`신규 운행 기록 ${trips.length}건 주입 중...`);

  // Insert all trips
  const insertStmt = db.prepare(`
    INSERT INTO TripModel (
      _id, OldId, ClientType, LastModified, CreatedDate,
      TotalDistance, ManualDistance, CalculatedDistance,
      TripOrderPosition, TripTrackingMethod, TripType,
      StartOdometer, EndOdometer,
      StartLocation, EndLongtitude, StartLongtitude, EndLatitude, StartLatitude,
      IsValidStartLocation, GPSTrackingData, EndLocation, IsValidEndLocation,
      IsManualProcess, VehicleLogbookId, MapModel, MultiTripCounter,
      ReturnTripFlag, CanClaimFlag, Date, Description, VehicleId,
      Type, SubType, IsFavourite, StartLocationPlaceId, EndLocationPlaceId
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?,
      ?, ?, ?,
      ?, ?,
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?,
      ?, ?, ?, ?,
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?
    )
  `);

  for (let i = 0; i < trips.length; i++) {
    const t = trips[i];
    const tripId = crypto.randomUUID();
    const dateTicks = dateToTicks(t.date);
    const startObj = resolvePlace(t.startLocation);
    const endObj = resolvePlace(t.endLocation);

    insertStmt.run([
      tripId,
      null, // OldId
      1, // ClientType
      dateTicks, // LastModified
      dateTicks, // CreatedDate
      t.totalKm,
      0.0, // ManualDistance
      t.tripDistance,
      i, // TripOrderPosition
      1, // TripTrackingMethod
      0, // TripType
      t.startOdometer || null,
      t.endOdometer || null,
      startObj.full,
      null,
      null,
      null,
      null,
      1, // IsValidStartLocation
      '', // GPSTrackingData
      endObj.full,
      1, // IsValidEndLocation
      0, // IsManualProcess
      null, // VehicleLogbookId
      0, // MapModel
      1, // MultiTripCounter
      t.returnJourney ? 1 : 0,
      1, // CanClaimFlag
      dateTicks,
      t.tripDetails,
      FYN_VEHICLE_ID,
      0, // Type
      0, // SubType
      0, // IsFavourite (will set top 12 below)
      startObj.placeId,
      endObj.placeId,
    ]);
  }
  insertStmt.free();

  if (onProgress) onProgress('즐겨찾기(⭐ Favourite Trips) 12개 자동 지정 중...');
  // Mark representative favourite trips as IsFavourite = 1
  db.run(`
    UPDATE TripModel
    SET IsFavourite = 1
    WHERE _id IN (
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 1 AND Description LIKE '%Regular Visit to HQ%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 1 AND Description LIKE '%Buying books%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 1 AND EndLocation LIKE '%IKEA%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 1 AND EndLocation LIKE '%Costco%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 1 AND EndLocation LIKE '%LIDCOMBE%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ meeting%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to IKEA%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to Costco%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to KMall%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%KMall09 Lidcombe to Penrith%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%IKEA Marsden Park to Penrith%' ORDER BY Date DESC LIMIT 1
      )
      UNION
      SELECT _id FROM (
        SELECT _id FROM TripModel WHERE VehicleId = '${FYN_VEHICLE_ID}' AND ReturnTripFlag = 0 AND Description LIKE '%Costco Marsden Park to Penrith%' ORDER BY Date DESC LIMIT 1
      )
    )
  `);

  if (onProgress) onProgress('ATO_Backup_ReadyToRestore.zip 패키징 중...');
  const updatedDbData = db.export();
  db.close();

  const zip = new JSZip();
  zip.file('ATO_Backup.ato', updatedDbData);

  const zipBlob = await zip.generateAsync({
    type: 'blob',
    compression: 'DEFLATE',
    compressionOptions: { level: 9 },
  });

  const downloadUrl = URL.createObjectURL(zipBlob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = 'ATO_Backup_ReadyToRestore.zip';
  a.click();
  URL.revokeObjectURL(downloadUrl);

  if (onProgress) onProgress('다운로드 완료!');
}
