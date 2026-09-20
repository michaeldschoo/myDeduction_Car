import csv
import io
import os
import json
from datetime import datetime

CONFIG_FILE = 'config.json'
ORIGINAL_FILE = 'myDeductionExpenses.csv'
GENERATED_FILE = 'FYN93N_ATO_Logbook.csv'
OUTPUT_FILE = 'myDeductionExpenses_ReadyToImport.csv'

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            files_cfg = cfg.get('files', {})
            ORIGINAL_FILE = files_cfg.get('base_expense_file', ORIGINAL_FILE)
            GENERATED_FILE = files_cfg.get('logbook_csv', GENERATED_FILE)
    except Exception as e:
        print(f"⚠️ {CONFIG_FILE} 로드 중 오류: {e}")

LOGBOOK_COLUMNS = [
    'Uploaded', 'Type', 'Status', 'Date', 'Vehicle', 'Purpose of trip',
    'Start odometer*', 'End odometer*', 'Start location#', 'End location#',
    'Trip details', 'Trip distance*', 'Record multiple trips*',
    'Record the return journey*', 'Total Km', 'Logbook trip'
]

def parse_date(date_str):
    if not date_str:
        return datetime.min
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except Exception:
        return datetime.min

def merge():
    if not os.path.exists(ORIGINAL_FILE):
        print(f"❌ 원본 파일 없음: {ORIGINAL_FILE}")
        return

    with open(ORIGINAL_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = content.split('\n\n')
    if len(sections) < 4:
        print("❌ 원본 CSV 포맷이 올바르지 않습니다.")
        return

    # Section 0: App header (Date, ATO app - myDeductions)
    # Section 1: Trips
    # Section 2: Logbooks
    # Section 3: Vehicles
    # Section 4: Footnote (optional)

    trips_raw = sections[1].strip().split('\n')
    header_line = trips_raw[1]
    data_lines = trips_raw[2:]

    reader = csv.DictReader(io.StringIO('\n'.join([header_line] + data_lines)))
    original_trips = list(reader)

    # 이전 FYN93N 또는 Fyn93n(2) 중복 데이터 제거 (완전한 최신 일지로 교체)
    clean_base_trips = [
        t for t in original_trips
        if t.get('Vehicle') not in ['FYN93N', 'Fyn93n(2)']
    ]

    print(f"기존 기록(EYO19Q 등) 유지: {len(clean_base_trips)}건")

    if not os.path.exists(GENERATED_FILE):
        print(f"❌ 생성된 로그북 파일 없음: {GENERATED_FILE}")
        return

    with open(GENERATED_FILE, 'r', encoding='utf-8') as f:
        new_trips = list(csv.DictReader(f))

    print(f"새로운 FYN93N 일지 추가: {len(new_trips)}건 (5월~9월 전체)")

    all_trips = clean_base_trips + new_trips
    all_trips.sort(key=lambda t: parse_date(t.get('Date', '')))

    out = io.StringIO()
    # 1. 헤더 섹션
    out.write(sections[0].strip() + '\n\n')

    # 2. Trips 섹션
    out.write('Trips\n')
    writer = csv.DictWriter(
        out,
        fieldnames=LOGBOOK_COLUMNS,
        extrasaction='ignore',
        lineterminator='\n'
    )
    writer.writeheader()
    for trip in all_trips:
        # None 키나 비정상 필드 제거 후 기록
        clean_trip = {col: trip.get(col, '') for col in LOGBOOK_COLUMNS}
        writer.writerow(clean_trip)

    out.write('\n')

    # 3. Logbooks 섹션
    # Logbook 기간을 2026-05-01 ~ 2026-09-18, 시작 120km, 종료 2714km로 최신화
    logbook_section_text = (
        "Logbooks\n"
        'Uploaded,Vehicle,Start date,End date,Starting odometer,Ending odometer,"Employee - work use %*","Employee - self education use %*",Start of year odometer reading*,End of year odometer reading,Purchase date*,Odometer reading on purchase*\n'
        'Not uploaded,FYN93N,01/05/2026,18/09/2026,120.00,2714.00,96%,0%,,,20/04/2026,120,\n'
    )
    out.write(logbook_section_text + '\n')

    # 4. Vehicles 섹션 (중복 Fyn93n(2) 정리)
    vehicles_section_text = (
        "Vehicles\n"
        'Registration,Description,Ownership,Vehicle type\n'
        'EYO19Q,"Ssangyong musso Xavier Ute trade-in 30/04/2026",I own lease or hire-purchase,Carrying capacity over 1 tonne,\n'
        'FYN93N,"BYD Shark 6 PHEV UTE",I own lease or hire-purchase,Carrying capacity over 1 tonne,\n'
    )
    out.write(vehicles_section_text + '\n')

    # 5. 각주
    if len(sections) > 4 and sections[4].strip():
        out.write(sections[4].strip() + '\n')
    else:
        out.write('"* If applicable to expense or trip type."\n')

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        f.write(out.getvalue())

    print(f"✅ 병합 완료 → {OUTPUT_FILE}")
    print(f"총 Trip 건수: {len(all_trips)} 건 (FYN93N: {len(new_trips)}건, 이전 차량: {len(clean_base_trips)}건)")

if __name__ == '__main__':
    merge()
