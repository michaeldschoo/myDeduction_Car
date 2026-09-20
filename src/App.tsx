import React from 'react';
import { Download, CheckCircle, Car, Calendar, FileSpreadsheet, ShieldAlert, ArrowRight } from 'lucide-react';

export default function App() {
  const stats = [
    { label: '대상 차량', value: 'FYN93N (BYD Shark 6)' },
    { label: '운행 기간', value: '2026.05.01 ~ 2026.09.18' },
    { label: '비즈니스 운행거리', value: '5,260.68 km' },
    { label: '비즈니스 사용 비율', value: '96.14% (목표 95% 달성)' },
    { label: '총 운행 건수 (FYN93N)', value: '66 건' },
    { label: '계기판(Odometer) 범위', value: '120 km → 2,714 km' },
  ];

  const monthlyData = [
    { fy: '2025-2026 FY', month: '2026년 5월', trips: 19, km: '1,451.34 km', note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회' },
    { fy: '2025-2026 FY', month: '2026년 6월', trips: 19, km: '1,720.22 km', note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회' },
    { fy: '2026-2027 FY', month: '2026년 7월', trips: 13, km: '1,095.74 km', note: 'Fyn93n(2) 중복 삭제 완료, 단일 FYN93N 정상 반영' },
    { fy: '2026-2027 FY', month: '2026년 8월', trips: 11, km: '715.78 km', note: 'IKEA / 서점 정기 루틴 및 본사 방문' },
    { fy: '2026-2027 FY', month: '2026년 9월', trips: 4, km: '277.60 km', note: '9월 18일 종료 시점까지 정상 기록' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header Card */}
        <header className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  <CheckCircle className="w-3 h-3 mr-1" /> 최신 검증 완료
                </span>
                <span className="text-xs text-slate-500">차량 단일화 및 회계연도 분리 적용됨</span>
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                ATO 차량 운행일지 데이터 센터
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                FYN93N 단일 등록 및 ATO myDeductions 규격 완벽 호환 파일
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <a
                href="/myDeductionExpenses.csv"
                download="myDeductionExpenses.csv"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition"
              >
                <Download className="w-4 h-4" />
                myDeductionExpenses.csv 다운로드
              </a>
              <a
                href="/FYN93N_ATO_Logbook.csv"
                download="FYN93N_ATO_Logbook.csv"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
              >
                <FileSpreadsheet className="w-4 h-4" />
                단독 Logbook.csv
              </a>
            </div>
          </div>
        </header>

        {/* Overview Stats */}
        <section className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {stats.map((item, idx) => (
            <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-medium text-slate-500 block mb-1">{item.label}</span>
              <span className="text-base font-semibold text-slate-900">{item.value}</span>
            </div>
          ))}
        </section>

        {/* Monthly Breakdown Table */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            월별 운행 기록 상세 (회계연도 구분)
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
                {monthlyData.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50/50">
                    <td className="py-3 font-medium text-slate-700">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs ${
                        row.fy.includes('2025-2026') ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}>
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

        {/* Guidance Section */}
        <section className="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-sm text-blue-900">
          <h3 className="font-bold text-base mb-2 flex items-center gap-2 text-blue-900">
            <CheckCircle className="w-5 h-5 text-blue-600" />
            아이패드 ATO myDeductions 가져오기 안내
          </h3>
          <p className="mb-3 text-blue-800">
            우측 상단의 <strong>[myDeductionExpenses.csv 다운로드]</strong> 버튼을 누르면, 아이패드 ATO 앱으로 즉시 Import할 수 있는 최신 파일이 다운로드됩니다.
          </p>
          <ul className="space-y-1.5 text-blue-800 list-disc list-inside">
            <li><strong>Fyn93n(2) 중복 삭제 완료:</strong> 오직 실제 등록번호인 <code>FYN93N</code> 하나만 남겨 7월 중복을 해소했습니다.</li>
            <li><strong>5월/6월 기록 확인:</strong> 호주 회계연도 기준(7월 1일 시작)에 따라 ATO 앱 상단의 연도를 <code>2025-2026</code>으로 변경하시면 5월/6월 운행기록을 확인하실 수 있습니다.</li>
            <li><strong>7월/8월/9월 기록 확인:</strong> 상단 연도를 <code>2026-2027</code>로 두시면 7월(1,095.74 km), 8월(715.78 km), 9월(277.60 km)이 정상 표시됩니다.</li>
          </ul>
        </section>

      </div>
    </div>
  );
}
