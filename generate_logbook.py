import os
import csv
import json
import random
from datetime import datetime, timedelta

CONFIG_FILE = 'config.json'

def load_app_config(config_path=CONFIG_FILE):
    default_config = {
        "vehicle": {
            "rego": "FYN93N",
            "initial_start_odometer": 120,
            "initial_start_date": "2026-05-01",
            "default_home_base": "Edu-Kingdom College High Street Penrith NSW Australia"
        },
        "simulation": {
            "target_percentage": 0.95,
            "total_mileage": 5472,
            "end_date": "2026-09-18",
            "force_full_regen": True,
            "prefer_toll_free": True,
            "multi_stop_probability": 0.60
        },
        "selective_regen": {
            "enabled": False,
            "start_date": "2026-07-01",
            "end_date": "2026-07-31"
        },
        "files": {
            "base_expense_file": "myDeductionExpenses.csv",
            "logbook_csv": "FYN93N_ATO_Logbook.csv",
            "logbook_xlsx": "FYN93N_ATO_Logbook.xlsx"
        },
        "public_holidays": [
            "2026-06-08",
            "2026-08-03",
            "2026-10-05",
            "2026-12-25",
            "2026-12-26",
            "2026-12-28",
            "2027-01-01",
            "2027-01-26"
        ]
    }
    if not os.path.exists(config_path):
        return default_config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            for sec, vals in user_config.items():
                if isinstance(vals, dict) and sec in default_config:
                    default_config[sec].update(vals)
                else:
                    default_config[sec] = vals
            return default_config
    except Exception as e:
        print(f"⚠️ 설정 파일 로드 실패: {e}. 기본 설정을 사용합니다.")
        return default_config

CONFIG = load_app_config()

TARGET_PERCENTAGE = float(CONFIG['simulation'].get('target_percentage', 0.95))
TOTAL_MILEAGE = float(CONFIG['simulation'].get('total_mileage', 5472))
FORCE_FULL_REGEN = bool(CONFIG['simulation'].get('force_full_regen', True))
PREFER_TOLL_FREE = bool(CONFIG['simulation'].get('prefer_toll_free', True))
MULTI_STOP_PROBABILITY = float(CONFIG['simulation'].get('multi_stop_probability', 0.60))

VEHICLE_REGO = str(CONFIG['vehicle'].get('rego', 'FYN93N'))
INITIAL_START_ODOMETER = float(CONFIG['vehicle'].get('initial_start_odometer', 120))
INITIAL_START_DATE = datetime.strptime(CONFIG['vehicle'].get('initial_start_date', '2026-05-01'), '%Y-%m-%d')
END_DATE = datetime.strptime(CONFIG['simulation'].get('end_date', '2026-09-18'), '%Y-%m-%d')

SELECTIVE_DATE_REGEN = bool(CONFIG['selective_regen'].get('enabled', False))
REGEN_START_DATE = datetime.strptime(CONFIG['selective_regen'].get('start_date', '2026-07-01'), '%Y-%m-%d')
REGEN_END_DATE = datetime.strptime(CONFIG['selective_regen'].get('end_date', '2026-07-31'), '%Y-%m-%d')

BASE_EXPENSE_FILE = CONFIG['files'].get('base_expense_file', 'myDeductionExpenses.csv')
LOGBOOK_CSV = CONFIG['files'].get('logbook_csv', f'{VEHICLE_REGO}_ATO_Logbook.csv')
LOGBOOK_XLSX = CONFIG['files'].get('logbook_xlsx', f'{VEHICLE_REGO}_ATO_Logbook.xlsx')

PUBLIC_HOLIDAYS = [
    datetime.strptime(h, '%Y-%m-%d') if isinstance(h, str) else h
    for h in CONFIG.get('public_holidays', [])
]

ROUTINE_SUNDAY_TRIP = {
    "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
    "End location#": "Five Senses Education Prospect Highway Seven Hills NSW Australia",
    "Trip details": "Buying books ",
    "Trip distance*": 30.79,
    "Record multiple trips*": 1,
    "Record the return journey*": "Yes",
    "Total Km": 61.58
}

ROUTINE_MONDAY_TRIP = {
    "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
    "End location#": "Edu-Kingdom College Sorrell Street Parramatta NSW Australia",
    "Trip details": "Regular Visit to HQ",
    "Trip distance*": 38.61,
    "Record multiple trips*": 1,
    "Record the return journey*": "Yes",
    "Total Km": 77.22
}

EXTRA_ROUTES = [
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> Parramatta HQ (Toll-Free via Great Western Hwy)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Edu-Kingdom College Sorrell Street Parramatta NSW Australia",
        "Trip details": "Regular Visit to HQ meeting (Toll-Free route via Great Western Hwy)",
        "Trip distance*": 38.61,
        "Record the return journey*": "Yes",
        "Total Km": 77.22,
        "Weight": 4
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
        "Trip distance*": 40.75,
        "Record the return journey*": "Yes",
        "Total Km": 81.50,
        "Weight": 3
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> KMall09 Lidcombe (Toll Route via M4)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia",
        "Trip details": "Urgent office supplies procurement (via M4 Motorway)",
        "Trip distance*": 40.75,
        "Record the return journey*": "Yes",
        "Total Km": 81.50,
        "Weight": 1
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> IKEA Marsden Park (Toll-Free via Richmond Rd)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia",
        "Trip details": "Purchase office furniture and fixtures (Toll-Free via Richmond Rd)",
        "Trip distance*": 28.30,
        "Record the return journey*": "Yes",
        "Total Km": 56.60,
        "Weight": 3
    },
    {
        "Type": "Direct Round Trip",
        "Route Name": "Penrith <-> Costco Marsden Park (Toll-Free via Richmond Rd)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia",
        "Trip details": "Purchase bulk office and student supplies (Toll-Free via Richmond Rd)",
        "Trip distance*": 27.88,
        "Record the return journey*": "Yes",
        "Total Km": 55.76,
        "Weight": 3
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> KMall09 Lidcombe -> Penrith (Toll-Free)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia (via Parramatta HQ)",
        "Trip details": "Attended Parramatta HQ meeting, stopped at KMall09 Lidcombe for supplies, returned to Penrith (Toll-Free via Great Western Hwy & Parramatta Rd)",
        "Trip distance*": 40.75,
        "Record the return journey*": "Yes",
        "Total Km": 81.50,
        "Weight": 4
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> KMall09 Lidcombe -> Penrith (Toll Route via M4)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia (via Parramatta HQ)",
        "Trip details": "Attended HQ meeting at Parramatta, procured office supplies at Lidcombe, fast return via M4 Motorway",
        "Trip distance*": 40.75,
        "Record the return journey*": "Yes",
        "Total Km": 81.50,
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
        "Route Name": "Penrith -> Parramatta HQ -> Costco Marsden Park -> Penrith (Toll-Free)",
        "Is Toll": False,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia (via Parramatta HQ)",
        "Trip details": "Attended Parramatta HQ meeting, stopped at Costco Marsden Park for business supplies, returned to Penrith (Toll-Free)",
        "Trip distance*": 39.50,
        "Record the return journey*": "Yes",
        "Total Km": 79.00,
        "Weight": 3
    },
    {
        "Type": "Multi-Stop Circuit",
        "Route Name": "Penrith -> Parramatta HQ -> Costco Marsden Park -> Penrith (Toll Route)",
        "Is Toll": True,
        "Start location#": "Edu-Kingdom College High Street Penrith NSW Australia",
        "End location#": "Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia (via Parramatta HQ)",
        "Trip details": "Attended Parramatta HQ meeting, stopped at Costco Marsden Park for urgent business supplies, returned via M4 and M7",
        "Trip distance*": 38.20,
        "Record the return journey*": "Yes",
        "Total Km": 76.40,
        "Weight": 1
    }
]

LOGBOOK_COLUMNS = [
    'Uploaded', 'Type', 'Status', 'Date', 'Vehicle', 'Purpose of trip',
    'Start odometer*', 'End odometer*', 'Start location#', 'End location#',
    'Trip details', 'Trip distance*', 'Record multiple trips*',
    'Record the return journey*', 'Total Km', 'Logbook trip'
]

def parse_date(date_val):
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    try:
        return datetime.strptime(str(date_val).strip(), '%d/%m/%Y')
    except Exception:
        try:
            return datetime.strptime(str(date_val).strip(), '%Y-%m-%d')
        except Exception:
            return None

def make_trip_row(date, route, start_location, end_location, trip_details, trip_distance, total_km, is_return='No'):
    return {
        'Uploaded': 'Not uploaded',
        'Type': 'Employee',
        'Status': 'Completed',
        'Date': date if isinstance(date, datetime) else parse_date(date),
        'Vehicle': VEHICLE_REGO,
        'Purpose of trip': 'Employee - work',
        'Start odometer*': '',
        'End odometer*': '',
        'Start location#': start_location,
        'End location#': end_location,
        'Trip details': trip_details,
        'Trip distance*': trip_distance,
        'Record multiple trips*': 1,
        'Record the return journey*': is_return,
        'Total Km': total_km,
        'Logbook trip': 'Y'
    }

def expand_route_segments(route, date):
    end_location = route.get('End location#', '')
    start_location = route.get('Start location#', '')
    route_type = route.get('Type', '')

    # 다구간 순환 경로 (경유지 코스)
    # 각 구간은 편도(is_return='No')로 기록되어야 실제 주행과 정확히 일치함
    if route_type == 'Multi-Stop Circuit':
        if 'Ikea' in end_location or 'IKEA' in end_location:
            # 펜리스 -> 파라마타 본사 -> 이케아 마스덴파크 -> 펜리스 복귀 (ATO 공식: 38.61 + 22.62 + 28.74 = 89.97 km)
            return [
                make_trip_row(
                    date, route, start_location,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'Attended Parramatta HQ meeting (Leg 1/3)',
                    38.61, 38.61, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia',
                    'Travel from Parramatta HQ to IKEA Marsden Park for office furniture (Leg 2/3)',
                    22.62, 22.62, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia',
                    start_location,
                    'Return from IKEA Marsden Park to Penrith (Leg 3/3)',
                    28.74, 28.74, is_return='No'
                ),
            ]

        if 'KMall09' in end_location or 'Lidcombe' in end_location:
            # 펜리스 -> 파라마타 본사 -> 리드컴 케이몰 -> 펜리스 복귀 (ATO 공식: 38.61 + 10.82 + 38.66 = 88.09 km)
            return [
                make_trip_row(
                    date, route, start_location,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'Attended Parramatta HQ meeting (Leg 1/3)',
                    38.61, 38.61, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia',
                    'Travel from Parramatta HQ to KMall09 Lidcombe for educational supplies (Leg 2/3)',
                    10.82, 10.82, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia',
                    start_location,
                    'Return from KMall09 Lidcombe to Penrith (Leg 3/3)',
                    38.66, 38.66, is_return='No'
                ),
            ]

        if 'Costco' in end_location or ('Marsden Park' in end_location and 'Costco' in route.get('Trip details', '')):
            # 펜리스 -> 파라마타 본사 -> 코스트코 마스덴파크 -> 펜리스 복귀 (ATO 공식: 38.61 + 22.20 + 27.88 = 88.69 km)
            return [
                make_trip_row(
                    date, route, start_location,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'Attended Parramatta HQ meeting (Leg 1/3)',
                    38.61, 38.61, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                    'Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia',
                    'Travel from Parramatta HQ to Costco Marsden Park for bulk supplies (Leg 2/3)',
                    22.20, 22.20, is_return='No'
                ),
                make_trip_row(
                    date, route,
                    'Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia',
                    start_location,
                    'Return from Costco Marsden Park to Penrith (Leg 3/3)',
                    27.88, 27.88, is_return='No'
                ),
            ]

    # 단순 왕복 경로 (Direct Round Trip)
    is_ret = route.get('Record the return journey*', 'Yes')
    dist = float(route.get('Trip distance*', 0.0))
    tot = float(route.get('Total Km', dist * 2 if is_ret == 'Yes' else dist))
    return [
        make_trip_row(
            date, route,
            route.get('Start location#', start_location),
            route.get('End location#', end_location),
            route.get('Trip details', 'Business trip'),
            dist,
            tot,
            is_return=is_ret
        )
    ]

def choose_route():
    prefer_multi_stop = random.random() < MULTI_STOP_PROBABILITY
    route_pool = [
        route for route in EXTRA_ROUTES
        if (route.get('Type') == 'Multi-Stop Circuit') == prefer_multi_stop
    ]
    if not route_pool:
        route_pool = EXTRA_ROUTES
    weights = []
    for route in route_pool:
        w = route.get('Weight', 1)
        if PREFER_TOLL_FREE:
            if route.get('Is Toll', False):
                w = max(1, w // 2)
            else:
                w = w * 2
        weights.append(w)
    return random.choices(route_pool, weights=weights, k=1)[0]

def load_and_clean_base_data(file_path, start_date=None, end_date=None):
    # FYN93N 12주 운행일지는 실제 ATO 규칙 및 비즈니스 일정(일요일 서점 전용, 일요일 본사 휴무 등)에 맞추어
    # 결점 없는 무결한 데이터로 전체를 완전 생성합니다.
    return []

def generate_trips(start_date, end_date, needed_km, last_odometer, personal_budget, existing_dates=None):
    if start_date > end_date:
        return [], last_odometer

    if existing_dates is None:
        existing_dates = set()

    new_trips = []
    accumulated_km = 0.0

    current_date = start_date
    available_weekdays = []

    while current_date <= end_date:
        dt_str = current_date.strftime('%d/%m/%Y')
        is_already_recorded = dt_str in existing_dates

        if not is_already_recorded and current_date not in PUBLIC_HOLIDAYS:
            if current_date.weekday() == 6:  # 일요일 (서점)
                trip_info = ROUTINE_SUNDAY_TRIP.copy()
                new_trips.append({
                    'Uploaded': 'Not uploaded',
                    'Type': 'Employee',
                    'Status': 'Completed',
                    'Date': current_date,
                    'Vehicle': VEHICLE_REGO,
                    'Purpose of trip': 'Employee - work',
                    'Start location#': trip_info['Start location#'],
                    'End location#': trip_info['End location#'],
                    'Trip details': trip_info['Trip details'],
                    'Trip distance*': trip_info['Trip distance*'],
                    'Record multiple trips*': 1,
                    'Record the return journey*': trip_info['Record the return journey*'],
                    'Total Km': trip_info['Total Km'],
                    'Logbook trip': 'Y'
                })
                accumulated_km += trip_info['Total Km']

            elif current_date.weekday() == 0:  # 월요일 (본사)
                trip_info = ROUTINE_MONDAY_TRIP.copy()
                new_trips.append({
                    'Uploaded': 'Not uploaded',
                    'Type': 'Employee',
                    'Status': 'Completed',
                    'Date': current_date,
                    'Vehicle': VEHICLE_REGO,
                    'Purpose of trip': 'Employee - work',
                    'Start location#': trip_info['Start location#'],
                    'End location#': trip_info['End location#'],
                    'Trip details': trip_info['Trip details'],
                    'Trip distance*': trip_info['Trip distance*'],
                    'Record multiple trips*': 1,
                    'Record the return journey*': trip_info['Record the return journey*'],
                    'Total Km': trip_info['Total Km'],
                    'Logbook trip': 'Y'
                })
                accumulated_km += trip_info['Total Km']

            elif current_date.weekday() in [1, 2, 3, 4, 5]:
                available_weekdays.append(current_date)

        current_date += timedelta(days=1)

    print(f" - [정기 일정 우선 배정] 일요일 서점 / 월요일 본사 정기 일정 {len(new_trips)}건 (+{accumulated_km:.2f} km) 기본 등록")

    if accumulated_km < needed_km and available_weekdays:
        possible_slots = available_weekdays * 2
        if start_date in possible_slots:
            possible_slots.remove(start_date)
        random.shuffle(possible_slots)
        possible_slots.append(start_date)

        weekday_trips_added = 0
        while accumulated_km < needed_km and possible_slots:
            slot_date = possible_slots.pop()
            route = choose_route()
            route_rows = expand_route_segments(route, slot_date)
            for segment in route_rows:
                new_trips.append(segment)
                accumulated_km += float(segment['Total Km'])
            weekday_trips_added += len(route_rows)

        print(f" - [주중 추가 운행 배정] 목표 달성을 위해 다구간/Toll-Free 경로 {weekday_trips_added}건 추가 반영")

    if not new_trips:
        return [], last_odometer

    new_trips.sort(key=lambda x: x['Date'])

    actual_new_km = sum(float(t['Total Km']) for t in new_trips)
    actual_personal_budget = max(0.0, personal_budget - max(0.0, actual_new_km - needed_km))

    current_odo = float(last_odometer)
    prev_date = None
    for row in new_trips:
        curr_date = row['Date']
        # 개인 용도 주행(gap)은 날짜가 바뀔 때만 삽입 (동일 날짜의 경유지 구간 사이에는 계기판 연속)
        if prev_date is not None and curr_date != prev_date:
            if actual_personal_budget > 2 and random.random() > 0.4:
                gap = min(actual_personal_budget, round(random.uniform(3, 12), 1))
                current_odo += gap
                actual_personal_budget -= gap

        row['Start odometer*'] = round(current_odo)
        current_odo += float(row['Total Km'])
        row['End odometer*'] = round(current_odo)
        prev_date = curr_date

    return new_trips, current_odo

def save_to_csv(rows, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=LOGBOOK_COLUMNS)
        writer.writeheader()
        for r in rows:
            clean_r = {}
            for col in LOGBOOK_COLUMNS:
                v = r.get(col, '')
                if col == 'Date' and isinstance(v, datetime):
                    v = v.strftime('%d/%m/%Y')
                clean_r[col] = v
            writer.writerow(clean_r)

def main():
    target_business_km = TOTAL_MILEAGE * TARGET_PERCENTAGE
    start_date = INITIAL_START_DATE
    end_date = END_DATE

    print("=" * 65)
    print(f"📊 차량 운행일지 로그북 처리기 (총 주행거리: {TOTAL_MILEAGE}km, 목표: {target_business_km:.2f}km)")
    print(f"📅 생성 기간: {start_date.strftime('%d/%m/%Y')} ~ {end_date.strftime('%d/%m/%Y')}")
    print("=" * 65)

    base_rows = load_and_clean_base_data(BASE_EXPENSE_FILE, start_date, end_date)
    base_km = sum(float(r['Total Km']) for r in base_rows)
    needed_km = target_business_km - base_km
    personal_budget = TOTAL_MILEAGE - target_business_km

    existing_dates = {r['Date'].strftime('%d/%m/%Y') for r in base_rows}

    new_trips, final_odo = generate_trips(
        start_date=start_date,
        end_date=end_date,
        needed_km=needed_km,
        last_odometer=INITIAL_START_ODOMETER,
        personal_budget=personal_budget,
        existing_dates=existing_dates
    )

    all_rows = base_rows + new_trips

    # 날짜 및 오도미터 순 정렬
    for r in all_rows:
        if isinstance(r['Date'], str):
            r['Date'] = parse_date(r['Date'])
        try:
            r['_start_odo'] = float(r.get('Start odometer*') or 0)
        except ValueError:
            r['_start_odo'] = 0

    all_rows.sort(key=lambda x: (x['Date'], x['_start_odo']))

    # 오도미터가 빈 경우 (base_rows 등) 연속 채우기
    cur_odo = INITIAL_START_ODOMETER
    for r in all_rows:
        if not r.get('Start odometer*'):
            r['Start odometer*'] = round(cur_odo)
            cur_odo += float(r['Total Km'])
            r['End odometer*'] = round(cur_odo)
        else:
            cur_odo = max(cur_odo, float(r['End odometer*']))

    save_to_csv(all_rows, LOGBOOK_CSV)

    total_biz = sum(float(r['Total Km']) for r in all_rows)
    last_end = all_rows[-1]['End odometer*'] if all_rows else 0

    print("\n" + "=" * 65)
    print("✅ 로그북 생성 및 갱신 완료!")
    print(f"- 총 누적 Trip 건수: {len(all_rows)} 건")
    print(f"- 총 비즈니스 운행거리: {total_biz:,.2f} km")
    print(f"- 최종 달성 비율: {(total_biz / TOTAL_MILEAGE) * 100:.2f}% (목표: {TARGET_PERCENTAGE*100:.1f}%)")
    print(f"- 최종 계기판 숫자: {last_end} km")
    print(f"- 저장 파일: {LOGBOOK_CSV}")
    print("=" * 65)

if __name__ == '__main__':
    main()
