import os
import csv
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# ==============================================================================
# [설정 영역] 추후 데이터 생성 시 아래 값들만 수정하세요!
# ==============================================================================
# 1. 목표치 및 총 주행거리 설정
TARGET_PERCENTAGE = 0.95            # 비즈니스 사용 비율 (95% -> 0.95)
TOTAL_MILEAGE = 4425                # 현재 차량의 총 누적 주행거리 (추가 주행 발생 시 이 값을 증가)

# 2. 시작 계기판 숫자 및 날짜 범위 설정
INITIAL_START_ODOMETER = 120        # 최초 시작 계기판 숫자 (기존 로그북이 없을 때만 사용)
INITIAL_START_DATE = datetime(2026, 5, 1)  # 최초 기록 시작 날짜
END_DATE = datetime(2026, 8, 24)   # 기록 종료 날짜 (추가 기간 설정 시 수정)

# 3. 파일 경로
BASE_EXPENSE_FILE = 'myDeductionExpenses.csv'
LOGBOOK_CSV = 'FYN93N_ATO_Logbook.csv'
LOGBOOK_XLSX = 'FYN93N_ATO_Logbook.xlsx'

# 4. 공휴일 설정 (제외할 날짜)
PUBLIC_HOLIDAYS = [
    datetime(2026, 6, 8),   # King's Birthday
    datetime(2026, 8, 3),   # Bank Holiday
]

# 5. 주중 추가 목적지 및 다구간 경유(Multi-stop) 경로 목록
# Toll 옵션: Toll-Free (무료 도로 / Great Western Hwy 등) vs Toll Road (M4 / WestConnex / M7 유료 도로)
# 기본적으로 Toll-Free 경로 우선(가중치 높음), 경우에 따라 Toll 경로도 선택 가능하도록 구성

PREFER_TOLL_FREE = True  # True: 무료도로 우선 배정 (약 75% 확률), False: 유료/무료 균등

EXTRA_ROUTES = [
    # -------------------------------------------------------------
    # [1] 단일 왕복 경로 (Single Point-to-Point Round Trips)
    # -------------------------------------------------------------
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> Parramatta HQ (Toll-Free via Great Western Hwy)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Edu-Kingdom College Sorrell Street Parramatta NSW Australia",
        "Trip details": "Regular Visit to HQ meeting (Toll-Free route via Great Western Hwy)",
        "Trip distance*": 38.61, # 편도
        "Record the return journey*": "Yes",
        "Total Km": 77.22,
        "Weight": 4  # 선택 가중치
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> Parramatta HQ (Toll Route via M4 Motorway)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Edu-Kingdom College Sorrell Street Parramatta NSW Australia",
        "Trip details": "Urgent executive meeting at HQ (via M4 Motorway)",
        "Trip distance*": 36.80,
        "Record the return journey*": "Yes",
        "Total Km": 73.60,
        "Weight": 2
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> KMall09 Lidcombe (Toll-Free via Parramatta Rd / Great Western Hwy)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia",
        "Trip details": "Purchase Korean educational & office supplies (Toll-Free route)",
        "Trip distance*": 39.40,
        "Record the return journey*": "Yes",
        "Total Km": 78.80,
        "Weight": 3
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> KMall09 Lidcombe (Toll Route via M4)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia",
        "Trip details": "Urgent office supplies procurement (via M4 Motorway)",
        "Trip distance*": 37.90,
        "Record the return journey*": "Yes",
        "Total Km": 75.80,
        "Weight": 1
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> IKEA Marsden Park (Toll-Free via Richmond Rd)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia",
        "Trip details": "Purchase office furniture and fixtures (Toll-Free via Richmond Rd)",
        "Trip distance*": 22.62,
        "Record the return journey*": "Yes",
        "Total Km": 45.24,
        "Weight": 4
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> Five Senses Seven Hills (Toll-Free via Great Western Hwy)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Five Senses Education Prospect Highway Seven Hills NSW Australia",
        "Trip details": "Curriculum books and teaching materials purchase (Toll-Free)",
        "Trip distance*": 30.79,
        "Record the return journey*": "Yes",
        "Total Km": 61.58,
        "Weight": 3
    },

    # -------------------------------------------------------------
    # [2] 다구간 경유 경로 (Multi-Stop Circuit Trips - 효율적인 연계 경로)
    # -------------------------------------------------------------
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> KMall09 Lidcombe -> Penrith (Toll-Free)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia (via Parramatta HQ)",
        "Trip details": "Attended Parramatta HQ meeting, stopped at KMall09 Lidcombe for supplies, returned to Penrith (Toll-Free via Great Western Hwy & Parramatta Rd)",
        "Trip distance*": 45.20,
        "Record the return journey*": "Yes",
        "Total Km": 90.40, # Penrith(0) -> Parramatta(38.6km) -> Lidcombe(9.2km) -> Penrith return(42.6km)
        "Weight": 4
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> KMall09 Lidcombe -> Penrith (Toll Route via M4)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia (via Parramatta HQ)",
        "Trip details": "Attended HQ meeting at Parramatta, procured office supplies at Lidcombe, fast return via M4 Motorway",
        "Trip distance*": 43.10,
        "Record the return journey*": "Yes",
        "Total Km": 86.20,
        "Weight": 2
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> IKEA Marsden Park -> Penrith (Toll-Free via Blacktown / Richmond Rd)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia (via Parramatta HQ)",
        "Trip details": "HQ consultation at Parramatta, visited IKEA Marsden Park for office furniture on return loop (Toll-Free route)",
        "Trip distance*": 41.30,
        "Record the return journey*": "Yes",
        "Total Km": 82.60,
        "Weight": 3
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> IKEA Marsden Park -> Penrith (Toll Route via M4 & Westlink M7)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia (via Parramatta HQ)",
        "Trip details": "HQ consultation at Parramatta, express visit to IKEA Marsden Park for urgent fixtures via M7 Motorway",
        "Trip distance*": 39.80,
        "Record the return journey*": "Yes",
        "Total Km": 79.60,
        "Weight": 1
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Five Senses Seven Hills -> Parramatta HQ -> Penrith (Toll-Free)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Edu-Kingdom College Sorrell Street Parramatta NSW Australia (via Seven Hills)",
        "Trip details": "Collected trial exam papers at Five Senses Seven Hills, delivered to Parramatta HQ, returned to Penrith (Toll-Free)",
        "Trip distance*": 42.50,
        "Record the return journey*": "Yes",
        "Total Km": 85.00,
        "Weight": 3
    }
]
# ==============================================================================

def parse_date(date_val):
    if pd.isna(date_val):
        return None
    if isinstance(date_val, datetime):
        return date_val
    try:
        return datetime.strptime(str(date_val).strip(), '%d/%m/%Y')
    except Exception:
        try:
            return pd.to_datetime(date_val).to_pydatetime()
        except Exception:
            return None

def load_existing_logbook(file_path):
    """기존 생성된 로그북이 있는지 확인하고 로드합니다."""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path, quoting=csv.QUOTE_MINIMAL)
        if df.empty or 'Date' not in df.columns or 'End odometer*' not in df.columns:
            return None
        return df
    except Exception as e:
        print(f"기존 로그북 로드 중 오류: {e}")
        return None

def load_and_clean_base_data(file_path):
    """최초 생성 시 myDeductionExpenses.csv 파일에서 기본 데이터를 추출합니다."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('Uploaded,Type,Status,Date'):
            start_idx = i
        elif line.startswith('Logbooks') and start_idx != -1:
            end_idx = i - 1
            break
            
    if start_idx == -1:
        return pd.DataFrame()
        
    import io
    csv_data = "".join(lines[start_idx:end_idx])
    df = pd.read_csv(io.StringIO(csv_data), index_col=False, on_bad_lines='skip', quoting=csv.QUOTE_MINIMAL)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['Date'])
    
    mask = (df['Date'] >= INITIAL_START_DATE) & (df['Date'] <= END_DATE)
    df = df[mask].copy()
    df['Vehicle'] = 'FYN93N'
    df = df.drop_duplicates(subset=['Date', 'End location#', 'Total Km'])
    return df

def choose_route():
    """가중치 및 Toll-Free 선호도에 따라 경로를 선택합니다."""
    weights = []
    for route in EXTRA_ROUTES:
        w = route.get('Weight', 1)
        if PREFER_TOLL_FREE:
            # 무료 도로 선호 시: 무료도로 가중치는 유지, 유료도로 가중치는 감소
            if route.get('Is Toll', False):
                w = max(1, w // 2)
            else:
                w = w * 2
        weights.append(w)
    return random.choices(EXTRA_ROUTES, weights=weights, k=1)[0]

def generate_incremental_trips(start_date, end_date, needed_km, last_odometer, personal_budget):
    """지정된 기간과 목표 km에 맞춰 기존 마지막 오도미터부터 이어서 Trip을 생성합니다."""
    if needed_km <= 0 or start_date > end_date:
        return pd.DataFrame(), last_odometer

    possible_dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() not in [0, 6]:  # 월(0), 일(6) 제외 (화~토 운행)
            if current_date not in PUBLIC_HOLIDAYS:
                possible_dates.append(current_date)
        current_date += timedelta(days=1)
        
    if not possible_dates:
        print("⚠️ 추가 생성 가능한 영업일이 없습니다.")
        return pd.DataFrame(), last_odometer

    possible_slots = possible_dates * 2
    random.shuffle(possible_slots)

    new_trips = []
    accumulated_km = 0.0

    while accumulated_km < needed_km and possible_slots:
        date = possible_slots.pop()
        route = choose_route()
        
        new_trips.append({
            'Uploaded': 'Not uploaded',
            'Type': 'Employee',
            'Status': 'Completed',
            'Date': date,
            'Vehicle': 'FYN93N',
            'Purpose of trip': 'Employee - work',
            'Start location#': route['Start location#'],
            'End location#': route['End location#'],
            'Trip details': route['Trip details'],
            'Trip distance*': route['Trip distance*'],
            'Record multiple trips*': 1,
            'Record the return journey*': route.get('Record the return journey*', 'Yes'),
            'Total Km': route['Total Km'],
            'Logbook trip': 'Y'
        })
        accumulated_km += route['Total Km']

    if not new_trips:
        return pd.DataFrame(), last_odometer

    new_df = pd.DataFrame(new_trips)
    new_df = new_df.sort_values(by='Date').reset_index(drop=True)

    current_odo = float(last_odometer)
    start_odos = []
    end_odos = []

    for _, row in new_df.iterrows():
        if personal_budget > 0 and random.random() > 0.6:
            gap = min(personal_budget, random.uniform(5, 20))
            current_odo += gap
            personal_budget -= gap
            
        start_odos.append(round(current_odo))
        current_odo += row['Total Km']
        end_odos.append(round(current_odo))

    new_df['Start odometer*'] = start_odos
    new_df['End odometer*'] = end_odos
    new_df['Date'] = new_df['Date'].apply(lambda d: d.strftime('%d/%m/%Y'))

    return new_df, current_odo

def main():
    target_business_km = TOTAL_MILEAGE * TARGET_PERCENTAGE
    print("=" * 65)
    print(f"📊 차량 운행일지 로그북 처리기 (총 주행거리: {TOTAL_MILEAGE}km, 목표: {target_business_km:.2f}km)")
    print("=" * 65)

    existing_df = load_existing_logbook(LOGBOOK_CSV)

    if existing_df is not None and not existing_df.empty:
        print(f"✅ 기존 로그북({LOGBOOK_CSV}) 발견: 기존 {len(existing_df)}건 기록 보존")
        
        parsed_dates = existing_df['Date'].apply(parse_date)
        last_date = parsed_dates.max()
        last_end_odo = float(existing_df['End odometer*'].iloc[-1])
        existing_business_km = float(existing_df['Total Km'].sum())
        
        print(f" - 기존 마지막 운행일: {last_date.strftime('%d/%m/%Y')}")
        print(f" - 기존 최종 계기판(End Odometer): {last_end_odo:,.0f} km")
        print(f" - 기존 누적 비즈니스 주행거리: {existing_business_km:.2f} km")

        needed_km = target_business_km - existing_business_km
        next_start_date = last_date + timedelta(days=1)
        
        if needed_km <= 0:
            print(f"\n🎉 이미 목표 비즈니스 주행거리({target_business_km:.2f}km)를 달성하였습니다. 추가 생성이 불필요합니다.")
            final_df = existing_df
        elif next_start_date > END_DATE:
            print(f"\n⚠️ 종료 날짜({END_DATE.strftime('%d/%m/%Y')})가 기존 마지막 기록일({last_date.strftime('%d/%m/%Y')}) 이전이거나 같습니다.")
            print("   새로운 운행 기간을 생성하려면 END_DATE를 늘려주세요.")
            final_df = existing_df
        else:
            print(f"\n🚀 [증분 생성 시작] 기간: {next_start_date.strftime('%d/%m/%Y')} ~ {END_DATE.strftime('%d/%m/%Y')}")
            print(f" - 추가 필요 비즈니스 주행거리: {needed_km:.2f} km")
            
            remaining_total_km = max(0, TOTAL_MILEAGE - last_end_odo)
            personal_budget = max(0, remaining_total_km - needed_km)

            new_df, final_odo = generate_incremental_trips(
                start_date=next_start_date,
                end_date=END_DATE,
                needed_km=needed_km,
                last_odometer=last_end_odo,
                personal_budget=personal_budget
            )

            print(f" - 신규 생성된 추가 Trip 수: {len(new_df)}건 (+{new_df['Total Km'].sum():.2f} km)")
            final_df = pd.concat([existing_df, new_df], ignore_index=True)

    else:
        print("ℹ️ 기존 로그북 파일이 없어 최초 신규 생성을 진행합니다.")
        base_df = load_and_clean_base_data(BASE_EXPENSE_FILE)
        current_km = base_df['Total Km'].sum() if not base_df.empty else 0.0
        needed_km = target_business_km - current_km
        
        personal_budget = TOTAL_MILEAGE - target_business_km
        new_df, _ = generate_incremental_trips(
            start_date=INITIAL_START_DATE,
            end_date=END_DATE,
            needed_km=needed_km,
            last_odometer=INITIAL_START_ODOMETER,
            personal_budget=personal_budget
        )
        
        if not base_df.empty:
            base_df['Date'] = base_df['Date'].dt.strftime('%d/%m/%Y')
            final_df = pd.concat([base_df, new_df], ignore_index=True)
        else:
            final_df = new_df

    cols = [
        'Uploaded', 'Type', 'Status', 'Date', 'Vehicle', 'Purpose of trip',
        'Start odometer*', 'End odometer*', 'Start location#', 'End location#',
        'Trip details', 'Trip distance*', 'Record multiple trips*',
        'Record the return journey*', 'Total Km', 'Logbook trip'
    ]
    for col in cols:
        if col not in final_df.columns:
            final_df[col] = ''
    final_df = final_df[cols]

    final_df.to_csv(LOGBOOK_CSV, index=False)
    final_df.to_excel(LOGBOOK_XLSX, index=False)

    total_biz = final_df['Total Km'].sum()
    print("\n" + "=" * 65)
    print("✅ 로그북 생성 및 갱신 완료!")
    print(f"- 총 누적 Trip 건수: {len(final_df)} 건")
    print(f"- 총 비즈니스 운행거리: {total_biz:,.2f} km")
    print(f"- 최종 달성 비율: {(total_biz / TOTAL_MILEAGE) * 100:.2f}% (목표: {TARGET_PERCENTAGE*100:.1f}%)")
    print(f"- 최종 계기판 숫자: {final_df['End odometer*'].iloc[-1]} km")
    print(f"- 저장 파일: {LOGBOOK_CSV}, {LOGBOOK_XLSX}")
    print("=" * 65)

if __name__ == '__main__':
    main()
