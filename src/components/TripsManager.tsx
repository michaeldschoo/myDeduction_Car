import React, { useState, useMemo } from 'react';
import {
  Plus,
  Search,
  Filter,
  Edit2,
  Trash2,
  Download,
  FileSpreadsheet,
  RotateCcw,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { TripRecord, INITIAL_TRIPS } from '../data/initialTrips';
import { TripEditorModal } from './TripEditorModal';
import { downloadCSV, downloadExcel, generateUpdatedAtoZip } from '../utils/exportUtils';

interface TripsManagerProps {
  trips: TripRecord[];
  setTrips: React.Dispatch<React.SetStateAction<TripRecord[]>>;
}

export const TripsManager: React.FC<TripsManagerProps> = ({ trips, setTrips }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFY, setSelectedFY] = useState<'all' | '2025-2026' | '2026-2027' | '05' | '06' | '07' | '08' | '09'>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tripToEdit, setTripToEdit] = useState<TripRecord | null>(null);
  const [isPackagingZip, setIsPackagingZip] = useState(false);
  const [packagingStatus, setPackagingStatus] = useState('');

  // Filtered trips
  const filteredTrips = useMemo(() => {
    return trips.filter((t) => {
      // Month & FY filtering
      const [, mm] = t.date.split('/');
      if (selectedFY === '2025-2026' && !(mm === '05' || mm === '06')) return false;
      if (selectedFY === '2026-2027' && !(mm === '07' || mm === '08' || mm === '09')) return false;
      if (['05', '06', '07', '08', '09'].includes(selectedFY) && mm !== selectedFY) return false;

      // Text search
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const match =
          t.date.toLowerCase().includes(q) ||
          t.startLocation.toLowerCase().includes(q) ||
          t.endLocation.toLowerCase().includes(q) ||
          t.tripDetails.toLowerCase().includes(q) ||
          t.totalKm.toString().includes(q);
        if (!match) return false;
      }
      return true;
    });
  }, [trips, selectedFY, searchQuery]);

  const filteredDistance = useMemo(() => {
    return filteredTrips.reduce((acc, t) => acc + t.totalKm, 0);
  }, [filteredTrips]);

  const handleOpenAddModal = () => {
    setTripToEdit(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (trip: TripRecord) => {
    setTripToEdit(trip);
    setIsModalOpen(true);
  };

  const handleSaveTrip = (savedTrip: TripRecord) => {
    if (tripToEdit) {
      setTrips((prev) => prev.map((t) => (t.id === savedTrip.id ? savedTrip : t)));
    } else {
      setTrips((prev) => [savedTrip, ...prev]);
    }
  };

  const handleDeleteTrip = (tripId: string) => {
    if (window.confirm('이 운행 기록을 삭제하시겠습니까?')) {
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
    }
  };

  const handleResetToInitial = () => {
    if (window.confirm('모든 수정을 취소하고 초기 106건 상태로 되돌리시겠습니까?')) {
      setTrips(INITIAL_TRIPS);
    }
  };

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

  return (
    <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-5">
      {/* Top Action Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700">
              <Sparkles className="w-4 h-4" />
            </span>
            <h2 className="text-base font-bold text-slate-900">
              운행일지 실시간 편집 및 데이터 내보내기
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            여기서 운행일지를 추가, 삭제, 수정하면 실시간으로 계기판 계산기와 다운로드용 파일이 즉시 갱신됩니다.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleOpenAddModal}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>새 운행일지 추가</span>
          </button>

          <button
            onClick={handleDownloadZip}
            disabled={isPackagingZip}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition disabled:opacity-50"
            title="현재 수정된 전체 일지가 주입된 ATO_Backup_ReadyToRestore.zip을 새로 패키징하여 다운로드"
          >
            {isPackagingZip ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{packagingStatus || '패키징 중...'}</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>최신 복원 ZIP 다운로드</span>
              </>
            )}
          </button>

          <button
            onClick={() => downloadExcel(trips)}
            className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
            title="수정된 엑셀(.xlsx) 다운로드"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
            <span>엑셀</span>
          </button>

          <button
            onClick={() => downloadCSV(trips)}
            className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
            title="수정된 CSV 다운로드"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-blue-600" />
            <span>CSV</span>
          </button>

          <button
            onClick={handleResetToInitial}
            className="inline-flex items-center gap-1 px-2.5 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
            title="초기 106건 상태로 초기화"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>초기화</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
        {/* Search */}
        <div className="relative flex-1 max-w-xs">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="출발지, 목적지, 날짜, 목적 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1 text-xs">
          <span className="text-[11px] text-slate-400 mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> 필터:
          </span>
          {[
            { id: 'all', label: `전체 (${trips.length})` },
            { id: '2025-2026', label: '지난 FY (5-6월)' },
            { id: '2026-2027', label: '올해 FY (7-9월)' },
            { id: '05', label: '5월' },
            { id: '06', label: '6월' },
            { id: '07', label: '7월' },
            { id: '08', label: '8월' },
            { id: '09', label: '9월' },
          ].map((pill) => (
            <button
              key={pill.id}
              onClick={() => setSelectedFY(pill.id as any)}
              className={`px-2.5 py-1 rounded-lg font-medium transition ${
                selectedFY === pill.id
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Result Summary */}
      <div className="flex items-center justify-between text-xs text-slate-500 bg-slate-50 px-4 py-2 rounded-xl border border-slate-200/60">
        <span>
          조회 결과: <strong className="text-slate-800">{filteredTrips.length}</strong> 건
        </span>
        <span>
          해당 구간 합계: <strong className="text-indigo-700 font-bold">{filteredDistance.toFixed(2)} km</strong>
        </span>
      </div>

      {/* Trips Table */}
      <div className="border border-slate-200 rounded-xl overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="bg-slate-100/80 sticky top-0 z-10 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3 w-12 text-center">#</th>
                <th className="py-2.5 px-3 w-24">운행일</th>
                <th className="py-2.5 px-3">운행 코스 (출발 ➔ 도착)</th>
                <th className="py-2.5 px-3">상세 업무 목적</th>
                <th className="py-2.5 px-3 w-18 text-center">왕복</th>
                <th className="py-2.5 px-3 w-24 text-right">총 거리</th>
                <th className="py-2.5 px-3 w-20 text-center">관리</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTrips.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    검색 조건에 일치하는 운행일지가 없습니다.
                  </td>
                </tr>
              ) : (
                filteredTrips.map((trip, idx) => {
                  const startShort = trip.startLocation.split(',')[0];
                  const endShort = trip.endLocation.split(',')[0];
                  return (
                    <tr key={trip.id} className="hover:bg-slate-50 transition group">
                      <td className="py-2.5 px-3 text-center text-slate-400 font-mono text-[11px]">
                        {idx + 1}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900 whitespace-nowrap">
                        {trip.date}
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-1 text-slate-800 font-medium">
                          <span className="truncate max-w-[140px]" title={trip.startLocation}>
                            {startShort}
                          </span>
                          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                          <span className="truncate max-w-[140px]" title={trip.endLocation}>
                            {endShort}
                          </span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-slate-600 max-w-[200px] truncate" title={trip.tripDetails}>
                        {trip.tripDetails}
                      </td>
                      <td className="py-2.5 px-3 text-center whitespace-nowrap">
                        {trip.returnJourney ? (
                          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                            왕복
                          </span>
                        ) : (
                          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-500">
                            편도
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-900 whitespace-nowrap">
                        {trip.totalKm.toFixed(2)} <span className="text-[10px] font-normal text-slate-400">km</span>
                      </td>
                      <td className="py-2.5 px-3 text-center whitespace-nowrap">
                        <div className="flex items-center justify-center gap-1 opacity-80 group-hover:opacity-100">
                          <button
                            onClick={() => handleOpenEditModal(trip)}
                            className="p-1 rounded text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition"
                            title="수정"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteTrip(trip.id)}
                            className="p-1 rounded text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition"
                            title="삭제"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit/Add Modal */}
      <TripEditorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveTrip}
        tripToEdit={tripToEdit}
      />
    </section>
  );
};
