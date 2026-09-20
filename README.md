# myDeduction Car Logbook Generator

## 프로젝트 목적
이 프로젝트는 차량 운행일지를 생성하고, myDeductions 앱에 적합한 CSV/Excel 형식으로 정리하는 도구입니다.

## 현재 설정값
- TARGET_PERCENTAGE = 0.95
- TOTAL_MILEAGE = 5472
- INITIAL_START_ODOMETER = 120
- INITIAL_START_DATE = 2026-05-01
- END_DATE = 2026-09-18
- FORCE_FULL_REGEN = True

## 핵심 수정 내용
### 1. 경로 분할 로직
다중 경유 경로가 하나의 row로 합쳐지는 문제를 개선했습니다.

다음 경로는 실제 이동 leg 단위로 분해되도록 정리했습니다.
- IKEA Marsden Park
- KMall09 Lidcombe
- Costco Marsden Park
- Five Senses Seven Hills

이렇게 분해함으로써 실제 이동 순서가 명확해지고, 수동 입력 시 혼동이 줄어듭니다.

### 2. odometer 연속성 유지
각 trip의 Start odometer / End odometer가 연속적으로 이어지도록 로직을 정리했습니다.

이제 각 행이 실제 이동 경로의 흐름에 맞게 이어지도록 보장됩니다.

### 3. 같은 날 내 정렬
same-day 행들이 날짜별로 섞이지 않고, 실제 이동 순서 기준으로 정렬되도록 수정했습니다.

정렬 기준:
- Date
- Start odometer*
- End odometer*

이 방식으로 같은 날의 운행 기록도 자연스럽게 시간/거리 흐름에 맞게 정리됩니다.

### 4. 강제 재생성 모드
기존 CSV를 그대로 재사용하지 않고, 실제 odometer 기준으로 처음부터 다시 생성하도록 설정했습니다.

- FORCE_FULL_REGEN = True

이를 통해 이전 생성 결과와 충돌 없이 새 로그북을 구성할 수 있습니다.

## 확인 포인트
최종 로그북은 아래 조건을 만족하는 형태로 정리하는 것을 목표로 합니다.
- 총 누적 Trip 건수 확인
- 총 비즈니스 운행거리 확인
- 최종 계기판 숫자 확인
- 날짜 순서 정렬
- 같은 날 여행 순서 정렬
- 다구간 경로 분할 확인

## 파일 구조
- generate_logbook.py : 로그북 생성 로직
- FYN93N_ATO_Logbook.csv : 생성된 CSV 결과
- FYN93N_ATO_Logbook.xlsx : Excel 결과
- myDeductionExpenses.csv : 원본 지출/운행 데이터

## 메모
이 문서는 현재 반영된 수정 의도와 생성 로직 정리를 위해 기록한 문서입니다.
다음 단계는 실제 실행 결과를 검증하고 필요한 경우 최종 CSV를 다시 확인하는 작업입니다.
