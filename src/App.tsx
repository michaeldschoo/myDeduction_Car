import React, { useState, useMemo } from 'react';
import {
  Download,
  CheckCircle,
  Car,
  Calendar,
  FileSpreadsheet,
  Smartphone,
  ArrowRight,
  Sparkles,
  AlertCircle,
  Loader2,
  Plus,
} from 'lucide-react';
import { INITIAL_TRIPS, TripRecord } from './data/initialTrips';
import { FAVOURITE_PRESETS, FavouritePreset } from './data/favoritePresets';
import { OdometerCalculator } from './components/OdometerCalculator';
import { TripsManager } from './components/TripsManager';
import { TripEditorModal } from './components/TripEditorModal';
import { generateUpdatedAtoZip, downloadExcel, downloadCSV } from './utils/exportUtils';

export default function App() {
  const [activeTab, setActiveTab] = useState<'ios' | 'android'>('ios');
  const [trips, setTrips] = useState<TripRecord[]>(INITIAL_TRIPS);
  const [startOdometer, setStartOdometer] = useState<number>(120);
  const [endOdometer, setEndOdometer] = useState<number>(5472);

  const [isPackagingZip, setIsPackagingZip] = useState(false);
  const [packagingStatus, setPackagingStatus] = useState('');

  // Quick preset modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalInitialTrip, setModalInitialTrip] = useState<TripRecord | null>(null);

  // Dynamic calculations
  const totalBusinessKm = useMemo(() => {
    return trips.reduce((sum, t) => sum + t.totalKm, 0);
  }, [trips]);

  const totalVehicleKm = Math.max(0, endOdometer - startOdometer);
  const businessRatio = totalVehicleKm > 0 ? (totalBusinessKm / totalVehicleKm) * 100 : 95.29;

  // FY breakdowns
  const fyBreakdown = useMemo(() => {
    const fy2526 = trips.filter((t) => {
      const mm = t.date.split('/')[1];
      return mm === '05' || mm === '06';
    });
    const fy2526Km = fy2526.reduce((sum, t) => sum + t.totalKm, 0);

    const fy2627 = trips.filter((t) => {
      const mm = t.date.split('/')[1];
      return mm === '07' || mm === '08' || mm === '09';
    });
    const fy2627Km = fy2627.reduce((sum, t) => sum + t.totalKm, 0);

    return [
      {
        fy: '2025-2026 Financial Year (지난 회계연도)',
        color: 'amber',
        trips: fy2526.length,
        km: `${fy2526Km.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} km`,
        desc: `FYN93N 5월/6월 합산 ${fy2526.length}건, ${fy2526Km.toFixed(2)}km 완벽 반영 (기존 EYO19Q 80건도 보존)`,
      },
      {
        fy: '2026-2027 Financial Year (올해 회계연도)',
        color: 'blue',
        trips: fy2627.length,
        km: `${fy2627Km.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} km`,
        desc: `FYN93N 7월/8월/9월 합산 ${fy2627.length}건, ${fy2627Km.toFixed(2)}km 완벽 반영`,
      },
    ];
  }, [trips]);

  // Monthly breakdown
  const monthlyBreakdown = useMemo(() => {
    const months = [
      {
        monthNum: '05',
        fy: '2025-2026 FY',
        month: '2026년 5월',
        note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회',
      },
      {
        monthNum: '06',
        fy: '2025-2026 FY',
        month: '2026년 6월',
        note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회',
      },
      {
        monthNum: '07',
        fy: '2026-2027 FY',
        month: '2026년 7월',
        note: '일요일 서점 단독 + 평일 업무 순환 정상화',
      },
      {
        monthNum: '08',
        fy: '2026-2027 FY',
        month: '2026년 8월',
        note: '리드컴(38.66km), 이케아(28.74km), 코스트코(22.20km) 실측치 반영',
      },
      {
        monthNum: '09',
        fy: '2026-2027 FY',
        month: '2026년 9월',
        note: '9월 18일 종료 시점까지 정상 기록',
      },
    ];

    return months.map((m) => {
      const monthTrips = trips.filter((t) => t.date.split('/')[1] === m.monthNum);
      const km = monthTrips.reduce((sum, t) => sum + t.totalKm, 0);
      return {
        ...m,
        trips: monthTrips.length,
        km: `${km.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} km`,
      };
    });
  }, [trips]);

  const handleDownloadZip = async () => {
    try {
      setIsPackagingZip(true);
      await generateUpdatedAtoZip(trips, (status) => setPackagingStatus(status));
    } catch (err: any) {
      alert('ZIP 파일 생성 중 오류가 발생했습니다: ' + (err?.message || err));
    } finally {
      setIsPackagingZip(false);
      setPackagingStatus('');
    }
  };

  const handleAddFromPreset = (preset: FavouritePreset) => {
    const now = new Date();
    const dd = String(now.getDate()).padStart(2, '0');
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const yyyy = now.getFullYear();
    setModalInitialTrip({
      id: `trip-${Date.now()}`,
      date: `${dd}/${mm}/${yyyy}`,
      startLocation: preset.startLocation,
      endLocation: preset.endLocation,
      tripDetails: preset.tripDetails,
      tripDistance: preset.tripDistance,
      returnJourney: preset.returnJourney,
      totalKm: preset.totalKm,
    });
    setIsModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header Card */}
        <header className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  <Sparkles className="w-3.5 h-3.5 mr-1 text-emerald-600" /> 실시간 편집 & ATO DB 엔진 탑재
                </span>
                <span className="text-xs text-slate-500 font-medium">원인 분석 및 복원 파일 완비</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
                ATO 앱(myDeductions) 복원 & 운행 관리 센터
              </h1>
              <p className="text-sm text-slate-600 mt-1.5">
                운행거리와 계기판을 실시간으로 확인/수정하고, 최신 데이터가 주입된 복원 파일(<code>ATO_Backup.ato</code>)을 즉시 다운로드할 수 있습니다.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row lg:flex-col gap-2 shrink-0">
              <button
                onClick={handleDownloadZip}
                disabled={isPackagingZip}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md hover:shadow transition disabled:opacity-60"
              >
                {isPackagingZip ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{packagingStatus || 'SQLite 패키징 중...'}</span>
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    <span>최신 ATO 복원용 ZIP 다운로드</span>
                  </>
                )}
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => downloadCSV(trips)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                  title="현재 수정된 일지 CSV 다운로드"
                >
                  <FileSpreadsheet className="w-4 h-4 text-blue-600" />
                  <span>최신 CSV ({trips.length}건)</span>
                </button>
                <button
                  onClick={() => downloadExcel(trips)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                  title="현재 수정된 일지 엑셀 다운로드"
                >
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  <span>최신 엑셀</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Live Odometer & Business Ratio Calculator */}
        <OdometerCalculator
          startOdometer={startOdometer}
          setStartOdometer={setStartOdometer}
          endOdometer={endOdometer}
          setEndOdometer={setEndOdometer}
          totalBusinessKm={totalBusinessKm}
          tripCount={trips.length}
        />

        {/* Interactive Trips Table & Manager */}
        <TripsManager trips={trips} setTrips={setTrips} />

        {/* Financial Year Summary Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {fyBreakdown.map((fy, i) => (
            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <span
                  className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold mb-2 ${
                    fy.color === 'amber' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {fy.fy}
                </span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {fy.km} <span className="text-sm font-normal text-slate-500">({fy.trips} Trips)</span>
                </div>
              </div>
              <p className="text-xs text-slate-600 mt-3 pt-3 border-t border-slate-100 leading-relaxed">
                {fy.desc}
              </p>
            </div>
          ))}
        </section>

        {/* Favourite Trips Section */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-amber-100 text-amber-700 text-sm">⭐</span>
                Favourite Trips (즐겨찾는 12개 대표 구간)
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                아래 카드 중 하나를 클릭하시면 즉시 날짜만 정하여 새 운행일지로 등록하거나, ATO 앱에서 1초 만에 불러오실 수 있습니다.
              </p>
            </div>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 self-start sm:self-auto">
              <CheckCircle className="w-3.5 h-3.5 mr-1 text-emerald-600" /> FYN93N 12개 구간 완비
            </span>
          </div>

          <div className="space-y-4">
            {/* How to use tip */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80 text-xs sm:text-sm text-slate-700">
              <div className="font-bold text-slate-900 mb-1.5 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-amber-600" />
                ATO 앱에서 즐겨찾기로 1초 만에 입력하는 방법:
              </div>
              <p className="text-xs leading-relaxed text-slate-600">
                ATO 앱에서 <strong>[Add trip]</strong> ➔ 차량을 <strong>[FYN93N]</strong>으로 선택 ➔ 상단 또는 화면의 <strong>[Choose from favourites (즐겨찾기 ⭐)]</strong> 선택 ➔ 아래 등록된 구간 중 하나를 터치하시면 <strong>출발지, 도착지, 실측 거리, 왕복 여부, 업무 목적이 즉시 자동 입력</strong>됩니다. 날짜만 지정하고 [Save]를 누르시면 완료됩니다!
              </p>
            </div>

            {/* Round trip favourites */}
            <div>
              <div className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                <span>🔄 주요 왕복 구간 (Round Trips - 5개) — 클릭 시 바로 추가</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {FAVOURITE_PRESETS.filter((p) => p.category === 'round').map((fav) => (
                  <div
                    key={fav.id}
                    onClick={() => handleAddFromPreset(fav)}
                    className="p-3 bg-white border border-slate-200 rounded-xl hover:border-amber-400 hover:shadow-xs cursor-pointer transition group"
                  >
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-bold text-slate-900 group-hover:text-amber-800 transition">
                        {fav.name}
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        왕복 {fav.totalKm} km
                      </span>
                    </div>
                    <div className="text-xs text-slate-600 flex items-center gap-1.5">
                      <span className="truncate max-w-[130px]">{fav.startLocation.split(',')[0]}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                      <span className="truncate max-w-[130px]">{fav.endLocation.split(',')[0]}</span>
                      <span className="text-slate-400 text-[11px]">(편도 {fav.tripDistance} km)</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                      <span className="truncate max-w-[240px]">{fav.tripDetails}</span>
                      <span className="text-indigo-600 font-semibold group-hover:underline flex items-center gap-0.5">
                        <Plus className="w-3 h-3" /> 추가
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* One way legs */}
            <div>
              <div className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                <span>➡️ 3구간 순환 편도 코스 (One-Way Legs - 7개) — 클릭 시 바로 추가</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {FAVOURITE_PRESETS.filter((p) => p.category === 'leg').map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleAddFromPreset(item)}
                    className="p-2.5 bg-slate-50 border border-slate-200/80 rounded-lg text-xs flex items-center justify-between hover:bg-white hover:border-indigo-300 cursor-pointer transition group"
                  >
                    <div className="truncate mr-2">
                      <span className="text-[10px] font-semibold text-indigo-600 block truncate">
                        {item.name}
                      </span>
                      <span className="font-medium text-slate-800 truncate block">
                        {item.startLocation.split(',')[0]} ➔ {item.endLocation.split(',')[0]}
                      </span>
                    </div>
                    <span className="font-bold text-slate-900 shrink-0">{item.tripDistance} km</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Step-by-Step Restoration Guide */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Smartphone className="w-5 h-5 text-indigo-600" />
              스마트폰 / 아이패드 ATO 앱 복원 가이드 (3분 완성)
            </h2>
            <div className="flex gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
              <button
                onClick={() => setActiveTab('ios')}
                className={`px-3 py-1 rounded-lg transition ${
                  activeTab === 'ios' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                아이폰 / 아이패드
              </button>
              <button
                onClick={() => setActiveTab('android')}
                className={`px-3 py-1 rounded-lg transition ${
                  activeTab === 'android' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                갤럭시 / 안드로이드
              </button>
            </div>
          </div>

          {activeTab === 'ios' ? (
            <ol className="space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  1
                </span>
                <div>
                  <strong>ZIP 파일 기기로 가져오기:</strong> 위 상단의 <code>ATO 복원용 ZIP 다운로드</code> 버튼을 눌러 PC에서 파일을 받으신 후, <strong>이메일(웹메일 본인에게 보내기 첨부)</strong> / AirDrop / 카카오톡(나에게 보내기) / iCloud Drive를 통해 아이패드나 아이폰으로 전달합니다. (아이패드 메일 앱이나 사파리 웹메일에서 첨부파일을 바로 다운로드하여 저장할 수 있어 매우 편리합니다.)
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  2
                </span>
                <div>
                  <strong>파일 앱에서 ATO 앱으로 열기:</strong> 아이패드의 <strong>[파일(Files)]</strong> 앱에서 저장된 <code>ATO_Backup_ReadyToRestore.zip</code>을 길게 누르고 <strong>[공유(Share)]</strong> ➔ 앱 목록에서 <strong>[ATO]</strong>를 선택합니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  3
                </span>
                <div>
                  <strong>복원 승인 (Restore):</strong> ATO 앱이 실행되면서 <em>"Do you want to restore your data?"</em> 메시지가 뜨면 <strong>[Continue / Restore]</strong>를 누릅니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  4
                </span>
                <div>
                  <strong>연도별 확인:</strong> myDeductions 화면 상단에서 연도를 <strong>2025-2026</strong>으로 바꾸면 5월/6월, <strong>2026-2027</strong>로 바꾸면 7월/8월/9월 기록이 완벽하게 표시됩니다!
                </div>
              </li>
            </ol>
          ) : (
            <ol className="space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  1
                </span>
                <div>
                  <strong>ZIP 파일 기기로 다운로드:</strong> 스마트폰 브라우저에서 본 페이지에 접속하여 <code>ATO 복원용 ZIP 다운로드</code>를 누르거나 구글 드라이브로 옮깁니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  2
                </span>
                <div>
                  <strong>내 파일 앱에서 열기:</strong> [내 파일] 앱 ➔ 다운로드 폴더에서 <code>ATO_Backup_ReadyToRestore.zip</code> 선택 ➔ <strong>[다른 앱으로 열기]</strong> ➔ <strong>[ATO]</strong> 앱 선택.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">
                  3
                </span>
                <div>
                  <strong>복원 승인:</strong> 안내 팝업에서 [Restore]를 누르면 즉시 전체 데이터베이스가 동기화됩니다.
                </div>
              </li>
            </ol>
          )}
        </section>

        {/* Monthly Breakdown Table */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            월별 운행 기록 상세 (회계연도 구분 - 실시간 연동)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider">
                  <th className="pb-3 font-semibold">호주 회계연도 (FY)</th>
                  <th className="pb-3 font-semibold">운행 월</th>
                  <th className="pb-3 font-semibold">운행 건수</th>
                  <th className="pb-3 font-semibold">비즈니스 거리</th>
                  <th className="pb-3 font-semibold">비고 / ATO 앱 확인 팁</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {monthlyBreakdown.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50/50">
                    <td className="py-3 font-medium text-slate-700">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs ${
                          row.fy.includes('2025-2026')
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}
                      >
                        {row.fy}
                      </span>
                    </td>
                    <td className="py-3 font-medium text-slate-900">{row.month}</td>
                    <td className="py-3 text-slate-600">{row.trips} 건</td>
                    <td className="py-3 font-semibold text-slate-900">{row.km}</td>
                    <td className="py-3 text-xs text-slate-500">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {/* Quick Preset Modal */}
      <TripEditorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={(newTrip) => setTrips((prev) => [newTrip, ...prev])}
        tripToEdit={modalInitialTrip}
      />
    </div>
  );
}
