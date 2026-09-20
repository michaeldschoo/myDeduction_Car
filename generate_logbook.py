import os
import csv
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# ==============================================================================
# [설정 로더] config.json이 있으면 우선 로드하고, 없을 경우 아래 기본값들을 사용합니다.
# ==============================================================================
CONFIG_FILE = 'config.json'

def load_app_config(config_path=CONFIG_FILE):
    """config.json 파일에서 설정을 안전하게 읽어오며, 오류 시 친절한 안내를 제공합니다."""
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
            "enabled": True,
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
        print(f"ℹ️ 설정 파일({config_path})이 없어 기본 내장 설정을 사용합니다.")
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            # 딕셔너리 재귀 병합
            for sec, vals in user_config.items():
                if isinstance(vals, dict) and sec in default_config:
                    default_config[sec].update(vals)
                else:
                    default_config[sec] = vals
            print(f"⚙️ 설정 파일({config_path})을 성공적으로 로드했습니다.")
            return default_config
    except Exception as e:
        print(f"⚠️ 설정 파일({config_path}) 파싱 중 오류 발생 ({e}). 기본 설정을 사용합니다.")
        return default_config

# 설정 적용
CONFIG = load_app_config()

# 1. 목표치 및 총 주행거리 설정
TARGET_PERCENTAGE = float(CONFIG['simulation'].get('target_percentage', 0.95))
TOTAL_MILEAGE = float(CONFIG['simulation'].get('total_mileage', 5472))
FORCE_FULL_REGEN = bool(CONFIG['simulation'].get('force_full_regen', True))
PREFER_TOLL_FREE = bool(CONFIG['simulation'].get('prefer_toll_free', True))
MULTI_STOP_PROBABILITY = float(CONFIG['simulation'].get('multi_stop_probability', 0.60))

# 2. 차량 및 시작/종료 설정
VEHICLE_REGO = str(CONFIG['vehicle'].get('rego', 'FYN93N'))
INITIAL_START_ODOMETER = float(CONFIG['vehicle'].get('initial_start_odometer', 120))
INITIAL_START_DATE = datetime.strptime(CONFIG['vehicle'].get('initial_start_date', '2026-05-01'), '%Y-%m-%d')
END_DATE = datetime.strptime(CONFIG['simulation'].get('end_date', '2026-09-18'), '%Y-%m-%d')

# 2-1. 특정 날짜 범위 재생성 설정
SELECTIVE_DATE_REGEN = bool(CONFIG['selective_regen'].get('enabled', False))
REGEN_START_DATE = datetime.strptime(CONFIG['selective_regen'].get('start_date', '2026-07-01'), '%Y-%m-%d')
REGEN_END_DATE = datetime.strptime(CONFIG['selective_regen'].get('end_date', '2026-07-31'), '%Y-%m-%d')

# 3. 파일 경로
BASE_EXPENSE_FILE = CONFIG['files'].get('base_expense_file', 'myDeductionExpenses.csv')
LOGBOOK_CSV = CONFIG['files'].get('logbook_csv', f'{VEHICLE_REGO}_ATO_Logbook.csv')
LOGBOOK_XLSX = CONFIG['files'].get('logbook_xlsx', f'{VEHICLE_REGO}_ATO_Logbook.xlsx')

# 4. 공휴일 설정 (제외할 날짜)
PUBLIC_HOLIDAYS = [
    datetime.strptime(h, '%Y-%m-%d') if isinstance(h, str) else h
    for h in CONFIG.get('public_holidays', [])
]

# 5. 주간 정기 고정 루틴 (일요일: 서점 교재 구매, 월요일: 본사 정기 방문)
# 추가 기간이 연장될 때마다 매주 일요일과 월요일은 최우선적으로 자동 배정됩니다.
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

# 6. 주중 추가 목적지 및 다구간 경유(Multi-stop) 경로 목록
# Toll 옵션: Toll-Free (무료 도로 / Great Western Hwy 등) vs Toll Road (M4 / WestConnex / M7 유료 도로)
# 기본적으로 Toll-Free 경로 우선(가중치 높음), 경우에 따라 Toll 경로도 선택 가능하도록 구성

PREFER_TOLL_FREE = True  # True: 무료도로 우선 배정 (약 75% 확률), False: 유료/무료 균등
MULTI_STOP_PROBABILITY = 0.60  # 주중 추가 운행 중 다중 경로를 선택할 확률

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

def get_generation_window():
    """전체 생성기간 또는 선택된 재생성 기간을 반환합니다."""
    if SELECTIVE_DATE_REGEN:
        start_date = REGEN_START_DATE
        end_date = REGEN_END_DATE
        if start_date > end_date:
            raise ValueError(f"재생성 시작일({start_date})이 종료일({end_date})보다 늦습니다.")
        return start_date, end_date
    return INITIAL_START_DATE, END_DATE


def load_and_clean_base_data(file_path, start_date=None, end_date=None):
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

    effective_start = start_date or INITIAL_START_DATE
    effective_end = end_date or END_DATE
    mask = (df['Date'] >= effective_start) & (df['Date'] <= effective_end)
    df = df[mask].copy()
    df['Vehicle'] = VEHICLE_REGO
    df = df.drop_duplicates(subset=['Date', 'End location#', 'Total Km'])
    return df

def make_trip_row(date, route, start_location, end_location, trip_details, trip_distance, total_km):
    """기존 포맷에 맞는 단일 trip row를 생성합니다."""
    return {
        'Uploaded': 'Not uploaded',
        'Type': 'Employee',
        'Status': 'Completed',
        'Date': date,
        'Vehicle': VEHICLE_REGO,
        'Purpose of trip': 'Employee - work',
        'Start location#': start_location,
        'End location#': end_location,
        'Trip details': trip_details,
        'Trip distance*': trip_distance,
        'Record multiple trips*': 1,
        'Record the return journey*': 'Yes',
        'Total Km': total_km,
        'Logbook trip': 'Y'
    }


def expand_route_segments(route, date):
    """다중 경유 경로를 실제 경로별 segment로 분해해 여러 trip row를 생성합니다."""
    end_location = route.get('End location#', '')
    start_location = route.get('Start location#', '')

    if 'Ikea' in end_location or 'IKEA' in end_location:
        return [
            make_trip_row(
                date,
                route,
                start_location,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Visit Parramatta HQ before IKEA Marsden Park trip',
                38.61,
                77.22,
            ),
            make_trip_row(
                date,
                route,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia',
                'Travel from Parramatta HQ to IKEA Marsden Park',
                22.62,
                45.24,
            ),
            make_trip_row(
                date,
                route,
                'Ikea Marsden Park, Hollinsworth, Marsden Park NSW, Australia',
                start_location,
                'Return from IKEA Marsden Park to Penrith',
                22.62,
                45.24,
            ),
        ]

    if 'KMall09' in end_location or 'Lidcombe' in end_location:
        return [
            make_trip_row(
                date,
                route,
                start_location,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Visit Parramatta HQ before Lidcombe shopping trip',
                38.61,
                77.22,
            ),
            make_trip_row(
                date,
                route,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia',
                'Travel from Parramatta HQ to KMall09 Lidcombe',
                39.40,
                78.80,
            ),
            make_trip_row(
                date,
                route,
                'KMall09 Lidcombe Shopping Centre, Parramatta Road, Lidcombe NSW, Australia',
                start_location,
                'Return from KMall09 Lidcombe to Penrith',
                39.40,
                78.80,
            ),
        ]

    if 'Costco' in end_location or 'Marsden Park' in end_location and 'Costco' in route.get('Trip details', ''):
        return [
            make_trip_row(
                date,
                route,
                start_location,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Visit Parramatta HQ before Costco stop',
                38.61,
                77.22,
            ),
            make_trip_row(
                date,
                route,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia',
                'Travel from Parramatta HQ to Costco Marsden Park',
                39.50,
                79.00,
            ),
            make_trip_row(
                date,
                route,
                'Costco Wholesale Marsden Park, Richmond Road, Marsden Park NSW Australia',
                start_location,
                'Return from Costco Marsden Park to Penrith',
                39.50,
                79.00,
            ),
        ]

    if 'Seven Hills' in end_location or 'Five Senses' in end_location:
        return [
            make_trip_row(
                date,
                route,
                start_location,
                'Five Senses Education Prospect Highway Seven Hills NSW Australia',
                'Visit Five Senses Education before reporting to HQ',
                30.79,
                61.58,
            ),
            make_trip_row(
                date,
                route,
                'Five Senses Education Prospect Highway Seven Hills NSW Australia',
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                'Travel from Seven Hills to Parramatta HQ',
                38.61,
                77.22,
            ),
            make_trip_row(
                date,
                route,
                'Edu-Kingdom College Sorrell Street Parramatta NSW Australia',
                start_location,
                'Return from Parramatta HQ to Penrith',
                38.61,
                77.22,
            ),
        ]

    return [
        make_trip_row(
            date,
            route,
            route.get('Start location#', start_location),
            route.get('End location#', end_location),
            route.get('Trip details', 'Business trip'),
            float(route.get('Trip distance*', 0.0)),
            float(route.get('Total Km', 0.0)),
        )
    ]


def choose_route():
    """다중 경로와 Toll-Free 선호도를 반영해 경로를 선택합니다."""
    prefer_multi_stop = random.random() < MULTI_STOP_PROBABILITY
    route_pool = [
        route for route in EXTRA_ROUTES
        if (route.get('Type') == 'Multi-Stop Circuit') == prefer_multi_stop
    ]
    weights = []
    for route in route_pool:
        w = route.get('Weight', 1)
        if PREFER_TOLL_FREE:
            # 무료 도로 선호 시: 무료도로 가중치는 유지, 유료도로 가중치는 감소
            if route.get('Is Toll', False):
                w = max(1, w // 2)
            else:
                w = w * 2
        weights.append(w)
    return random.choices(route_pool, weights=weights, k=1)[0]

def generate_incremental_trips(start_date, end_date, needed_km, last_odometer, personal_budget, existing_dates=None):
    """지정된 기간과 목표 km에 맞춰 기존 마지막 오도미터부터 이어서 Trip을 생성합니다.
    1. 일요일(Five Senses 서점 교재 구매)과 월요일(Parramatta HQ 본사 정기 방문)을 최우선 기본 일정으로 자동 배정
    2. 목표 비즈니스 주행거리(95%) 충족을 위해 남은 km는 주중(화~토)에 다구간/Toll-Free 경로 풀에서 자동 배정
    """
    if start_date > end_date:
        return pd.DataFrame(), last_odometer

    if existing_dates is None:
        existing_dates = set()

    new_trips = []
    accumulated_km = 0.0

    # 1단계: 일요일(Seven Hills 서점) 및 월요일(Parramatta 본사) 정기 일정 우선 배정
    current_date = start_date
    available_weekdays = []  # 화~토 중 운행 가능한 평일 풀

    while current_date <= end_date:
        dt_str = current_date.strftime('%d/%m/%Y')
        is_already_recorded = dt_str in existing_dates

        if not is_already_recorded and current_date not in PUBLIC_HOLIDAYS:
            if current_date.weekday() == 6:  # 일요일 (서점 교재 구매)
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

            elif current_date.weekday() == 0:  # 월요일 (Parramatta HQ 본사 방문)
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

            elif current_date.weekday() in [1, 2, 3, 4, 5]:  # 화, 수, 목, 금, 토
                available_weekdays.append(current_date)

        current_date += timedelta(days=1)

    print(f" - [정기 일정 우선 배정] 일요일 서점 / 월요일 본사 정기 일정 {len(new_trips)}건 (+{accumulated_km:.2f} km) 기본 등록")

    # 2단계: 목표 비즈니스 주행거리(needed_km) 도달을 위해 남은 거리 화~토요일에 배정
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
        return pd.DataFrame(), last_odometer

    new_df = pd.DataFrame(new_trips)
    new_df = new_df.sort_values(by='Date').reset_index(drop=True)

    # 3단계: 오도미터 연속성 및 개인 용도(personal) 간격 배분
    actual_new_km = new_df['Total Km'].sum()
    actual_personal_budget = max(0.0, personal_budget - max(0.0, actual_new_km - needed_km))

    current_odo = float(last_odometer)
    start_odos = []
    end_odos = []

    for _, row in new_df.iterrows():
        if actual_personal_budget > 2 and random.random() > 0.5:
            gap = min(actual_personal_budget, round(random.uniform(3, 15), 1))
            current_odo += gap
            actual_personal_budget -= gap

        start_odos.append(round(current_odo))
        current_odo += row['Total Km']
        end_odos.append(round(current_odo))

    new_df['Start odometer*'] = start_odos
    new_df['End odometer*'] = end_odos
    new_df['Date'] = new_df['Date'].apply(lambda d: d.strftime('%d/%m/%Y'))
    new_df = new_df.sort_values(by=['Date', 'Start odometer*', 'End odometer*'], kind='mergesort').reset_index(drop=True)

    return new_df, current_odo

def main():
    target_business_km = TOTAL_MILEAGE * TARGET_PERCENTAGE
    regen_start, regen_end = get_generation_window()

    print("=" * 65)
    print(f"📊 차량 운행일지 로그북 처리기 (총 주행거리: {TOTAL_MILEAGE}km, 목표: {target_business_km:.2f}km)")
    if SELECTIVE_DATE_REGEN:
        print(f"📅 선택 재생성 모드 활성화: {regen_start.strftime('%d/%m/%Y')} ~ {regen_end.strftime('%d/%m/%Y')}")
    print("=" * 65)

    existing_df = None if FORCE_FULL_REGEN else load_existing_logbook(LOGBOOK_CSV)

    if FORCE_FULL_REGEN:
        print(f"⚠️ 강제 전체 재생성 모드: 기존 {LOGBOOK_CSV}를 무시하고 실제 odometer 기준으로 처음부터 생성합니다.")
        existing_df = None

    if SELECTIVE_DATE_REGEN:
        print("ℹ️ 특정 날짜 범위만 다시 생성합니다. 선택한 기간 외의 데이터는 유지하고, 해당 기간만 재생성합니다.")
        if FORCE_FULL_REGEN:
            print("   - 강제 전체 재생성 플래그는 범위 재생성 모드에서 무시됩니다.")
            existing_df = None

        preserved_df = pd.DataFrame()
        if existing_df is not None and not existing_df.empty:
            parsed_dates = existing_df['Date'].apply(parse_date)
            outside_window_mask = ~parsed_dates.between(regen_start, regen_end, inclusive='both')
            preserved_df = existing_df.loc[outside_window_mask].copy()

        last_odo = INITIAL_START_ODOMETER
        if not preserved_df.empty:
            last_odo = float(preserved_df['End odometer*'].iloc[-1])
        elif existing_df is not None and not existing_df.empty:
            prior_rows = existing_df[existing_df['Date'].apply(parse_date) < regen_start].copy()
            if not prior_rows.empty:
                last_odo = float(prior_rows['End odometer*'].iloc[-1])

        source_df = load_and_clean_base_data(BASE_EXPENSE_FILE, regen_start, regen_end)
        target_km = float(source_df['Total Km'].sum()) if not source_df.empty else 200.0

        new_df, _ = generate_incremental_trips(
            start_date=regen_start,
            end_date=regen_end,
            needed_km=max(target_km, 50.0),
            last_odometer=last_odo,
            personal_budget=max(0.0, TOTAL_MILEAGE - target_business_km),
            existing_dates=set()
        )

        final_df = pd.concat([preserved_df, new_df], ignore_index=True)

    elif existing_df is not None and not existing_df.empty:
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

        if next_start_date > END_DATE:
            print(f"\n⚠️ 종료 날짜({END_DATE.strftime('%d/%m/%Y')})가 기존 마지막 기록일({last_date.strftime('%d/%m/%Y')}) 이전이거나 같습니다.")
            print("   새로운 운행 기간을 생성하려면 END_DATE를 늘려주세요.")
            final_df = existing_df
        elif needed_km <= 0:
            print(f"\n🎉 이미 목표 비즈니스 주행거리({target_business_km:.2f}km)를 달성하였습니다. 추가 생성이 불필요합니다.")
            print("   추가 주행거리를 반영하려면 TOTAL_MILEAGE 값을 늘려주세요.")
            final_df = existing_df
        else:
            print(f"\n🚀 [증분 생성 시작] 기간: {next_start_date.strftime('%d/%m/%Y')} ~ {END_DATE.strftime('%d/%m/%Y')}")
            print(f" - 추가 필요 비즈니스 주행거리: {needed_km:.2f} km")

            remaining_total_km = max(0, TOTAL_MILEAGE - last_end_odo)
            personal_budget = max(0, remaining_total_km - needed_km)

            existing_dates_set = set(existing_df['Date'].dropna().astype(str).tolist())

            new_df, final_odo = generate_incremental_trips(
                start_date=next_start_date,
                end_date=END_DATE,
                needed_km=needed_km,
                last_odometer=last_end_odo,
                personal_budget=personal_budget,
                existing_dates=existing_dates_set
            )

            print(f" - 신규 생성된 추가 Trip 수: {len(new_df)}건 (+{new_df['Total Km'].sum():.2f} km)")
            final_df = pd.concat([existing_df, new_df], ignore_index=True)

    else:
        print("ℹ️ 기존 로그북 파일이 없어 최초 신규 생성을 진행합니다.")
        base_df = load_and_clean_base_data(BASE_EXPENSE_FILE, regen_start, regen_end)
        current_km = base_df['Total Km'].sum() if not base_df.empty else 0.0
        needed_km = target_business_km - current_km

        personal_budget = TOTAL_MILEAGE - target_business_km
        existing_dates_set = set()
        if not base_df.empty:
            existing_dates_set = set(base_df['Date'].dt.strftime('%d/%m/%Y').tolist())

        new_df, _ = generate_incremental_trips(
            start_date=regen_start,
            end_date=regen_end,
            needed_km=needed_km,
            last_odometer=INITIAL_START_ODOMETER,
            personal_budget=personal_budget,
            existing_dates=existing_dates_set
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
    final_df['_sort_date'] = pd.to_datetime(final_df['Date'], format='%d/%m/%Y', errors='coerce')
    final_df['_sort_start_odo'] = pd.to_numeric(final_df['Start odometer*'], errors='coerce').fillna(0)
    final_df = final_df.sort_values(by=['_sort_date', '_sort_start_odo'], kind='mergesort').drop(columns=['_sort_date', '_sort_start_odo']).reset_index(drop=True)
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
