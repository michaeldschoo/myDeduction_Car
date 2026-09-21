import React from 'react';
import { Gauge, ShieldCheck, AlertTriangle, Calculator, Sparkles } from 'lucide-react';

interface OdometerCalculatorProps {
  startOdometer: number;
  setStartOdometer: (val: number) => void;
  endOdometer: number;
  setEndOdometer: (val: number) => void;
  totalBusinessKm: number;
  tripCount: number;
}

export const OdometerCalculator: React.FC<OdometerCalculatorProps> = ({
  startOdometer,
  setStartOdometer,
  endOdometer,
  setEndOdometer,
  totalBusinessKm,
  tripCount,
}) => {
  const totalVehicleKm = Math.max(0, endOdometer - startOdometer);
  const privateKm = Math.max(0, totalVehicleKm - totalBusinessKm);
  const businessRatio = totalVehicleKm > 0 ? (totalBusinessKm / totalVehicleKm) * 100 : 0;

  // ATO Safe Harbour evaluation
  const isOptimal = businessRatio >= 85;
  const isGood = businessRatio >= 80 && businessRatio < 85;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700">
              <Gauge className="w-4 h-4" />
            </span>
            <h2 className="text-base font-bold text-slate-900">
              계기판(Odometer) 및 최종 운행거리 실시간 계산기
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            차량 실제 계기판(오도미터) 누적거리를 입력하시면 비즈니스 사용 비율(%)과 사적 이용거리가 실시간 계산됩니다.
          </p>
        </div>

        <div className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold self-start sm:self-auto border bg-slate-50 border-slate-200">
          {isOptimal ? (
            <span className="flex items-center text-emerald-700 font-bold">
              <ShieldCheck className="w-4 h-4 mr-1 text-emerald-600" /> ATO 세무 안전 권장 기준 충족 (≥ 85%)
            </span>
          ) : isGood ? (
            <span className="flex items-center text-blue-700 font-bold">
              <ShieldCheck className="w-4 h-4 mr-1 text-blue-600" /> 양호 기준 (80% ~ 85%)
            </span>
          ) : (
            <span className="flex items-center text-amber-700 font-bold">
              <AlertTriangle className="w-4 h-4 mr-1 text-amber-600" /> 주의 필요 (80% 미만)
            </span>
          )}
        </div>
      </div>

      {/* Input controls & Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-5">
        {/* Start Odometer */}
        <div className="bg-slate-50/80 rounded-xl p-3.5 border border-slate-200">
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            인수 시 시작 계기판 (km)
          </label>
          <div className="relative">
            <input
              type="number"
              min="0"
              value={startOdometer}
              onChange={(e) => setStartOdometer(Number(e.target.value) || 0)}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <span className="absolute right-3 top-2.5 text-xs text-slate-400">km</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">2026-05-01 기준</span>
        </div>

        {/* End Odometer */}
        <div className="bg-slate-50/80 rounded-xl p-3.5 border border-slate-200">
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            최종 계기판 거리 (km)
          </label>
          <div className="relative">
            <input
              type="number"
              min={startOdometer}
              value={endOdometer}
              onChange={(e) => setEndOdometer(Number(e.target.value) || 0)}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <span className="absolute right-3 top-2.5 text-xs text-slate-400">km</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">현재 실제 계기판 수치</span>
        </div>

        {/* Total Vehicle Travelled */}
        <div className="bg-slate-50/80 rounded-xl p-3.5 border border-slate-200 flex flex-col justify-between">
          <div>
            <span className="block text-xs font-semibold text-slate-600 mb-1">차량 총 주행거리</span>
            <div className="text-xl font-bold text-slate-900">
              {totalVehicleKm.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}{' '}
              <span className="text-xs font-normal text-slate-500">km</span>
            </div>
          </div>
          <span className="text-[11px] text-slate-500">계기판 차이 (End - Start)</span>
        </div>

        {/* Business Ratio Result */}
        <div className={`rounded-xl p-3.5 border flex flex-col justify-between ${
          isOptimal ? 'bg-emerald-50 border-emerald-200' : 'bg-blue-50 border-blue-200'
        }`}>
          <div>
            <span className="block text-xs font-semibold text-slate-700 mb-1">비즈니스 사용 비율 (%)</span>
            <div className={`text-2xl font-black ${
              isOptimal ? 'text-emerald-700' : 'text-blue-700'
            }`}>
              {businessRatio.toFixed(2)}%
            </div>
          </div>
          <span className="text-[11px] text-slate-600 font-medium">
            비즈니스 {totalBusinessKm.toFixed(1)} km / 사적 {privateKm.toFixed(1)} km
          </span>
        </div>
      </div>

      {/* Progress visual bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-600">
          <span className="font-semibold flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            비즈니스 운행 비율 게이지 ({businessRatio.toFixed(1)}%)
          </span>
          <span>
            총 {tripCount}회 운행 / {totalBusinessKm.toFixed(2)} km
          </span>
        </div>
        <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex">
          <div
            className="h-full bg-emerald-500 transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(0, businessRatio))}%` }}
            title={`비즈니스: ${businessRatio.toFixed(2)}%`}
          />
          <div
            className="h-full bg-slate-300 transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(0, 100 - businessRatio))}%` }}
            title={`개인 용도: ${(100 - businessRatio).toFixed(2)}%`}
          />
        </div>
        <div className="flex justify-between text-[11px] text-slate-400">
          <span>0%</span>
          <span className="text-slate-500 font-medium">85% ATO 안전 기준선</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
};
