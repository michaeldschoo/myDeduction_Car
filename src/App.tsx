import React, { useState } from 'react';
import { Download, CheckCircle, Car, Calendar, FileSpreadsheet, ShieldAlert, Smartphone, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'ios' | 'android'>('ios');

  const stats = [
    { label: '대상 차량', value: 'FYN93N (BYD Shark 6)' },
    { label: '운행 기간', value: '2026.05.01 ~ 2026.09.18' },
    { label: '비즈니스 운행거리', value: '5,214.36 km' },
    { label: '비즈니스 사용 비율', value: '95.29% (목표 달성)' },
    { label: '총 운행 건수 (FYN93N)', value: '106 건 (전체 차량 407건)' },
    { label: 'ATO DB 정밀 주입', value: 'ATO_Backup.ato 100% 동기화 완료' },
  ];

  const fyData = [
    {
      fy: '2025-2026 Financial Year (지난 회계연도)',
      color: 'amber',
      trips: 40,
      km: '2,069.06 km',
      desc: 'FYN93N 5월(21건, 1,110.29km) + 6월(19건, 958.77km) 완벽 반영 (기존 EYO19Q 80건도 보존)',
    },
    {
      fy: '2026-2027 Financial Year (올해 회계연도)',
      color: 'blue',
      trips: 66,
      km: '3,145.30 km',
      desc: 'FYN93N 7월(31건, 1,439.12km) + 8월(23건, 1,102.72km) + 9월(12건, 603.46km) 완벽 반영',
    },
  ];

  const monthlyData = [
    { fy: '2025-2026 FY', month: '2026년 5월', trips: 21, km: '1,110.29 km', note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회' },
    { fy: '2025-2026 FY', month: '2026년 6월', trips: 19, km: '958.77 km', note: 'ATO 앱 상단 연도를 2025-2026으로 설정 시 조회' },
    { fy: '2026-2027 FY', month: '2026년 7월', trips: 31, km: '1,439.12 km', note: '일요일 서점 단독 + 평일 업무 순환 정상화' },
    { fy: '2026-2027 FY', month: '2026년 8월', trips: 23, km: '1,102.72 km', note: '리드컴(38.66km), 이케아(28.74km), 코스트코(22.20km) 실측치 반영' },
    { fy: '2026-2027 FY', month: '2026년 9월', trips: 12, km: '603.46 km', note: '9월 18일 종료 시점까지 정상 기록' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header Card */}
        <header className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  <Sparkles className="w-3.5 h-3.5 mr-1 text-emerald-600" /> ATO SQLite DB 주입 완료
                </span>
                <span className="text-xs text-slate-500 font-medium">원인 분석 및 복원 파일 생성 완료</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
                ATO 앱(myDeductions) 복원 센터
              </h1>
              <p className="text-sm text-slate-600 mt-1.5">
                앱이 실제로 읽는 시스템 파일(<code>ATO_Backup.ato</code>)에 106건 전체를 직접 삽입하여 지난 회계연도와 올해 운행일지가 화면에 100% 뜨도록 제작되었습니다.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row lg:flex-col gap-2 shrink-0">
              <a
                href="/ATO_Backup_ReadyToRestore.zip"
                download="ATO_Backup_ReadyToRestore.zip"
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md hover:shadow transition"
              >
                <Download className="w-5 h-5" />
                <span>ATO 복원용 ZIP 다운로드</span>
              </a>
              <div className="flex gap-2">
                <a
                  href="/myDeductionExpenses.csv"
                  download="myDeductionExpenses.csv"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                  title="전체 407건 통합 CSV"
                >
                  <FileSpreadsheet className="w-4 h-4 text-blue-600" />
                  <span>통합 CSV (407건)</span>
                </a>
                <a
                  href="/FYN93N_ATO_Logbook.xlsx"
                  download="FYN93N_ATO_Logbook.xlsx"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                  title="FYN93N 106건 엑셀"
                >
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  <span>엑셀 (106건)</span>
                </a>
              </div>
            </div>
          </div>
        </header>

        {/* Why update didn't work before alert */}
        <section className="bg-amber-50/80 border border-amber-200/90 rounded-2xl p-5 text-sm">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h2 className="font-bold text-amber-900 text-base mb-1">
                왜 그동안 앱 화면에서 업데이트가 되지 않았을까요? (원인 확인)
              </h2>
              <p className="text-amber-800 leading-relaxed text-xs sm:text-sm">
                보내주신 압축파일을 뜯어 분석한 결과, ATO 앱은 복원(Restore)할 때 <strong>CSV 파일을 읽지 않고, 압축파일 안에 들어있는 SQLite 데이터베이스인 <code>ATO_Backup.ato</code> 파일만을 그대로 앱에 덮어씁니다.</strong><br />
                기존 백업 파일의 <code>ATO_Backup.ato</code>에는 <strong>5월/6월(지난 회계연도) 기록이 0건</strong>이었고, <strong>7월도 옛날 28건</strong>만 들어있어 앱을 복원해도 화면이 변하지 않았던 것입니다.<br />
                👉 <strong>지금 다운로드받으실 ZIP 파일은 <code>ATO_Backup.ato</code> 내부 테이블에 106건 전체를 직접 완벽하게 삽입하여 해결했습니다!</strong>
              </p>
            </div>
          </div>
        </section>

        {/* Financial Year Summary Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {fyData.map((fy, i) => (
            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold mb-2 ${
                  fy.color === 'amber' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                }`}>
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
                Favourite Trips (즐겨찾는 구간 12개 등록 완료)
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                향후 손으로 한두 건씩 입력하실 때 1초 만에 자동 완성할 수 있도록 ATO DB에 즐겨찾기 플래그(<code>IsFavourite = 1</code>)를 적용했습니다.
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
                <span>🔄 주요 왕복 구간 (Round Trips - 5개)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {[
                  {
                    title: 'Regular Visit to HQ (본사 정기 방문)',
                    from: 'Penrith',
                    to: 'Parramatta HQ',
                    oneWay: '38.61 km',
                    total: '77.22 km',
                    desc: '본사 정기 회의 및 업무 협의',
                  },
                  {
                    title: 'Buying books (교재 구매)',
                    from: 'Penrith',
                    to: 'Five Senses Seven Hills',
                    oneWay: '30.79 km',
                    total: '61.58 km',
                    desc: 'Five Senses Education 정기 교재 수급',
                  },
                  {
                    title: 'Purchase office furniture (가구/비품)',
                    from: 'Penrith',
                    to: 'IKEA Marsden Park',
                    oneWay: '28.30 km',
                    total: '56.60 km',
                    desc: '학원 책상/의자 및 비품 구매',
                  },
                  {
                    title: 'Purchase bulk supplies (대량 비품)',
                    from: 'Penrith',
                    to: 'Costco Marsden Park',
                    oneWay: '27.88 km',
                    total: '55.76 km',
                    desc: '원생용 간식 및 사무 비품 대량 구매',
                  },
                  {
                    title: 'Purchase Korean supplies (한국 교재/비품)',
                    from: 'Penrith',
                    to: 'KMALL09 Lidcombe',
                    oneWay: '40.75 km',
                    total: '81.50 km',
                    desc: '한국 서적 및 문구/교구 수급',
                  },
                ].map((fav, idx) => (
                  <div key={idx} className="p-3 bg-white border border-slate-200 rounded-xl hover:border-amber-300 transition">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-bold text-slate-900">{fav.title}</span>
                      <span className="px-1.5 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        왕복 {fav.total}
                      </span>
                    </div>
                    <div className="text-xs text-slate-600 flex items-center gap-1.5">
                      <span>{fav.from}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                      <span>{fav.to}</span>
                      <span className="text-slate-400 text-[11px]">(편도 {fav.oneWay})</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">{fav.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* One way legs */}
            <div>
              <div className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                <span>➡️ 3구간 순환 편도 코스 (One-Way Legs - 7개)</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {[
                  { leg: '1구간', name: 'Penrith ➔ Parramatta HQ', dist: '38.61 km' },
                  { leg: '2구간 (HQ➔이케아)', name: 'Parramatta HQ ➔ IKEA', dist: '22.62 km' },
                  { leg: '2구간 (HQ➔코스트코)', name: 'Parramatta HQ ➔ Costco', dist: '22.20 km' },
                  { leg: '2구간 (HQ➔리드컴)', name: 'Parramatta HQ ➔ KMall09', dist: '10.82 km' },
                  { leg: '3구간 (귀환)', name: 'IKEA ➔ Penrith', dist: '28.74 km' },
                  { leg: '3구간 (귀환)', name: 'Costco ➔ Penrith', dist: '27.88 km' },
                  { leg: '3구간 (귀환)', name: 'KMall09 ➔ Penrith', dist: '38.66 km' },
                ].map((item, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-50 border border-slate-200/80 rounded-lg text-xs flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-semibold text-indigo-600 block">{item.leg}</span>
                      <span className="font-medium text-slate-800">{item.name}</span>
                    </div>
                    <span className="font-bold text-slate-900 shrink-0 ml-2">{item.dist}</span>
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
                className={`px-3 py-1 rounded-lg transition ${activeTab === 'ios' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-900'}`}
              >
                아이폰 / 아이패드
              </button>
              <button
                onClick={() => setActiveTab('android')}
                className={`px-3 py-1 rounded-lg transition ${activeTab === 'android' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-900'}`}
              >
                갤럭시 / 안드로이드
              </button>
            </div>
          </div>

          {activeTab === 'ios' ? (
            <ol className="space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">1</span>
                <div>
                  <strong>ZIP 파일 기기로 가져오기:</strong> 위 상단의 <code>ATO 복원용 ZIP 다운로드</code> 버튼을 눌러 파일을 받으신 후, AirDrop / 카카오톡(나에게 보내기) / iCloud Drive를 통해 아이패드나 아이폰으로 보냅니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">2</span>
                <div>
                  <strong>파일 앱에서 ATO 앱으로 열기:</strong> 아이패드의 <strong>[파일(Files)]</strong> 앱에서 저장된 <code>ATO_Backup_ReadyToRestore.zip</code>을 길게 누르고 <strong>[공유(Share)]</strong> ➔ 앱 목록에서 <strong>[ATO]</strong>를 선택합니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">3</span>
                <div>
                  <strong>복원 승인 (Restore):</strong> ATO 앱이 실행되면서 <em>"Do you want to restore your data?"</em> 메시지가 뜨면 <strong>[Continue / Restore]</strong>를 누릅니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">4</span>
                <div>
                  <strong>연도별 확인:</strong> myDeductions 화면 상단에서 연도를 <strong>2025-2026</strong>으로 바꾸면 5월/6월(40건), <strong>2026-2027</strong>로 바꾸면 7월/8월/9월(66건)이 즉시 완벽하게 표시됩니다!
                </div>
              </li>
            </ol>
          ) : (
            <ol className="space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">1</span>
                <div>
                  <strong>ZIP 파일 기기로 다운로드:</strong> 스마트폰 브라우저에서 본 페이지에 접속하여 <code>ATO 복원용 ZIP 다운로드</code>를 누르거나 구글 드라이브로 옮깁니다.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">2</span>
                <div>
                  <strong>내 파일 앱에서 열기:</strong> [내 파일] 앱 ➔ 다운로드 폴더에서 <code>ATO_Backup_ReadyToRestore.zip</code> 선택 ➔ <strong>[다른 앱으로 열기]</strong> ➔ <strong>[ATO]</strong> 앱 선택.
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs shrink-0 mt-0.5">3</span>
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

      </div>
    </div>
  );
}
