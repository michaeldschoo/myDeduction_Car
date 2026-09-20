import sqlite3
import csv
import uuid
import shutil
import zipfile
from datetime import datetime, timedelta

def dt_to_ticks(dt):
    epoch = datetime(1, 1, 1)
    delta = dt - epoch
    return delta.days * 86400 * 10000000 + delta.seconds * 10000000 + delta.microseconds * 10

def ticks_to_dt(ticks):
    return datetime(1, 1, 1) + timedelta(microseconds=ticks//10)

PLACE_MAP = {
    'Penrith': ('Edu-Kingdom College, High Street, Penrith NSW, Australia', 'ChIJOfWVTouFEmsRZfOG9q9DAnE'),
    'Parramatta': ('Edu-Kingdom College, Sorrell Street, Parramatta NSW, Australia', 'ChIJc0LXTxujEmsRmhrB29XeVnQ'),
    'Seven Hills': ('Five Senses Education, Prospect Highway, Seven Hills NSW, Australia', 'ChIJlUJc746YEmsRGPRjlM8FqMU'),
    'Lidcombe': ('KMALL09 LIDCOMBE, Shopping Centre, Parramatta Road, Lidcombe NSW, Australia', 'ChIJEYUFFaq7EmsR3XvEP5SDUug'),
    'IKEA': ('IKEA Marsden Park, Hollinsworth Road, Marsden Park NSW, Australia', 'ChIJY4X0MGycEmsRon9gatPnJgM'),
    'Costco': ('Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW, Australia', 'ChIJH8Kj9F-dEmsRR5dZ0G-b1g4'),
}

def resolve_loc_and_id(loc_str):
    s = loc_str.lower()
    if 'seven hills' in s: return PLACE_MAP['Seven Hills']
    if 'lidcombe' in s or 'kmall' in s: return PLACE_MAP['Lidcombe']
    if 'ikea' in s: return PLACE_MAP['IKEA']
    if 'costco' in s: return PLACE_MAP['Costco']
    if 'parramatta' in s: return PLACE_MAP['Parramatta']
    return PLACE_MAP['Penrith']

def build_updated_database():
    # 1. 원본 ATO_Backup.ato 복사
    shutil.copy('extracted_backup/ATO_Backup.ato', 'ATO_Backup.ato')
    
    conn = sqlite3.connect('ATO_Backup.ato')
    cursor = conn.cursor()
    
    # 2. FYN93N 차량 구입일 및 등록일을 2026-05-01로 수정 (5월 운행 기록이 앱에서 잘리지 않도록)
    fyn_purchase_ticks = dt_to_ticks(datetime(2026, 5, 1, 0, 0, 0))
    cursor.execute("""
        UPDATE VehicleModel
        SET VehicleAddedDate = ?, VehiclePurchaseDate = ?, LastModified = ?
        WHERE VehicleRegistration = 'FYN93N'
    """, (fyn_purchase_ticks, fyn_purchase_ticks, dt_to_ticks(datetime.now())))
    print(f"VehicleModel updated for FYN93N (PurchaseDate: {ticks_to_dt(fyn_purchase_ticks)})")
    
    # 3. 기존 FYN93N의 불완전한 28건 삭제
    cursor.execute("SELECT _id FROM VehicleModel WHERE VehicleRegistration = 'FYN93N'")
    fyn_vehicle_id = cursor.fetchone()[0]
    cursor.execute("DELETE FROM TripModel WHERE VehicleId = ?", (fyn_vehicle_id,))
    print(f"Existing FYN93N trips deleted. Remaining EYO19Q trips preserved.")
    
    # 4. 정밀 보정된 106건의 FYN93N 일지 읽기
    with open('FYN93N_ATO_Logbook.csv', mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        
    print(f"Read {len(reader)} calibrated trips from FYN93N_ATO_Logbook.csv")
    
    now_ticks = dt_to_ticks(datetime.now())
    inserted_count = 0
    
    for row in reader:
        date_str = row['Date'] # DD/MM/YYYY
        d, m, y = map(int, date_str.split('/'))
        trip_dt = datetime(y, m, d, 0, 0, 0)
        trip_ticks = dt_to_ticks(trip_dt)
        
        start_loc, start_place_id = resolve_loc_and_id(row['Start location#'])
        end_loc, end_place_id = resolve_loc_and_id(row['End location#'])
        
        calc_dist = float(row['Trip distance*'])
        total_dist = float(row['Total Km'])
        is_return = 1 if row['Record the return journey*'] == 'Yes' else 0
        multi_counter = int(row['Record multiple trips*'])
        desc = row['Trip details']
        
        trip_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO TripModel (
                _id, OldId, ClientType, LastModified, CreatedDate,
                TotalDistance, ManualDistance, CalculatedDistance,
                TripOrderPosition, TripTrackingMethod, TripType,
                StartOdometer, EndOdometer,
                StartLocation, EndLongtitude, StartLongtitude, EndLatitude, StartLatitude,
                IsValidStartLocation, GPSTrackingData,
                EndLocation, IsValidEndLocation, IsManualProcess,
                VehicleLogbookId, MapModel, MultiTripCounter, ReturnTripFlag, CanClaimFlag,
                Date, Description, VehicleId, Type, SubType, IsFavourite,
                StartLocationPlaceId, EndLocationPlaceId
            ) VALUES (
                ?, NULL, 1, ?, ?,
                ?, 0.0, ?,
                0, 1, 0,
                NULL, NULL,
                ?, NULL, NULL, NULL, NULL,
                1, '',
                ?, 1, 0,
                NULL, 0, ?, ?, 1,
                ?, ?, ?, 0, 0, 0,
                ?, ?
            )
        """, (
            trip_id, now_ticks, now_ticks,
            total_dist, calc_dist,
            start_loc,
            end_loc, multi_counter, is_return,
            trip_ticks, desc, fyn_vehicle_id,
            start_place_id, end_place_id
        ))
        inserted_count += 1
        
    conn.commit()
    print(f"Successfully inserted {inserted_count} trips into TripModel!")
    
    # 5. Favourite Trips (즐겨찾는 구간) 등록
    # ATO 앱에서 'Add trip' 할 때 즐겨찾기(⭐)에서 1초 만에 자동 완성할 수 있도록
    # 주요 왕복 및 편도 구간 대표 레코드에 IsFavourite = 1 플래그 설정
    cursor.execute("""
        UPDATE TripModel
        SET IsFavourite = 1
        WHERE _id IN (
            SELECT _id FROM (
                -- 1. Penrith <-> Parramatta HQ 왕복 (77.22 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 1 AND Description LIKE '%Regular Visit to HQ%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 2. Penrith <-> Seven Hills 교재 구매 왕복 (61.58 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 1 AND Description LIKE '%Buying books%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 3. Penrith <-> IKEA Marsden Park 가구/비품 구매 왕복 (56.60 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 1 AND EndLocation LIKE '%IKEA%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 4. Penrith <-> Costco Marsden Park 대량 비품 구매 왕복 (55.76 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 1 AND EndLocation LIKE '%Costco%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 5. Penrith <-> KMall09 Lidcombe 한국 교재/비품 구매 왕복 (81.50 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 1 AND EndLocation LIKE '%LIDCOMBE%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 6. Penrith -> Parramatta HQ 편도 (38.61 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ meeting%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 7. Parramatta HQ -> IKEA Marsden Park 편도 (22.62 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to IKEA%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 8. Parramatta HQ -> Costco Marsden Park 편도 (22.20 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to Costco%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 9. Parramatta HQ -> KMall09 Lidcombe 편도 (10.82 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%Parramatta HQ to KMall%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 10. KMall09 Lidcombe -> Penrith 편도 (38.66 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%KMall09 Lidcombe to Penrith%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 11. IKEA Marsden Park -> Penrith 편도 (28.74 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%IKEA Marsden Park to Penrith%'
                ORDER BY Date DESC LIMIT 1
            )
            UNION
            SELECT _id FROM (
                -- 12. Costco Marsden Park -> Penrith 편도 (27.88 km)
                SELECT _id FROM TripModel
                WHERE VehicleId = ? AND ReturnTripFlag = 0 AND Description LIKE '%Costco Marsden Park to Penrith%'
                ORDER BY Date DESC LIMIT 1
            )
        )
    """, (
        fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id,
        fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id,
        fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id, fyn_vehicle_id
    ))
    conn.commit()
    print("Favourite trips successfully set for FYN93N!")
    
    # 6. 검증
    cursor.execute("SELECT count(*) FROM TripModel WHERE VehicleId = ?", (fyn_vehicle_id,))
    total_fyn = cursor.fetchone()[0]
    cursor.execute("SELECT sum(TotalDistance) FROM TripModel WHERE VehicleId = ?", (fyn_vehicle_id,))
    total_km = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM TripModel WHERE VehicleId != ?", (fyn_vehicle_id,))
    eyo_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM TripModel WHERE IsFavourite = 1 AND VehicleId = ?", (fyn_vehicle_id,))
    fav_fyn_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM TripModel WHERE IsFavourite = 1 AND VehicleId != ?", (fyn_vehicle_id,))
    fav_eyo_count = cursor.fetchone()[0]
    
    print("=" * 60)
    print(f"✅ ATO Database Verification:")
    print(f" - FYN93N Trips: {total_fyn} 건 (총 {total_km:.2f} km)")
    print(f" - FYN93N Favourite Trips (즐겨찾기): {fav_fyn_count} 개 구간")
    print(f" - EYO19Q Trips (기존 유지): {eyo_count} 건 (즐겨찾기: {fav_eyo_count} 개)")
    print(f" - 총 TripModel 레코드: {total_fyn + eyo_count} 건")
    print("=" * 60)
    
    conn.close()
    
    # 6. 복원용 최종 ZIP 패키징 (ATO 앱 규격 100% 호환)
    # zip 내부에는 myDeductionExpenses.csv, Import instructions.txt, ATO_Backup.ato 가 위치해야 함
    zip_filename = 'ATO_Backup_ReadyToRestore.zip'
    with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write('myDeductionExpenses_ReadyToImport.csv', arcname='myDeductionExpenses.csv')
        zf.write('ATO_Backup.ato', arcname='ATO_Backup.ato')
        zf.write('extracted_backup/Import instructions.txt', arcname='Import instructions.txt')
        
    shutil.copy(zip_filename, f'public/{zip_filename}')
    shutil.copy(zip_filename, 'public/ATO_Backup.zip')
    shutil.copy('ATO_Backup.ato', 'public/ATO_Backup.ato')
    
    print(f"📦 Successfully created: {zip_filename} & public/{zip_filename}")

if __name__ == '__main__':
    build_updated_database()
