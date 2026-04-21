# OpenRouter Monitor

Home Assistant용 [OpenRouter](https://openrouter.ai) 커스텀 통합 구성요소입니다.
Management API Key를 통해 크레딧 잔액, API Key별 사용량을 센서로 모니터링할 수 있습니다.

---

## 기능

- **계정 모니터링**: 잔액, 총 사용량(누적), 일별/주별/월별 전체 사용량
- **API Key별 사용량**: 누적/일별/주별/월별 사용량, 한도 및 잔여 한도
- **환율 변환**: 고정 환율 또는 HA 센서 연동으로 현지 통화 표시 (15개 주요 통화 지원)
- **디바이스 분리**: 계정 디바이스 + Key별 독립 디바이스로 구성
- **다국어 지원**: 한국어/영어 UI 및 엔티티 이름 번역
- **설정 가능한 폴링 주기**: 1~60분 범위에서 자유롭게 설정
- **HACS 지원**: HACS를 통해 간단하게 설치 및 업데이트 가능

---

## 설치

### HACS를 통한 설치 (권장)

1. HACS → 통합 구성요소 → 우측 상단 메뉴 → **사용자 지정 저장소 추가**
2. URL: `https://github.com/Lemon-HACS/openrouter_monitor`, 카테고리: `통합 구성요소`
3. **OpenRouter** 검색 후 다운로드
4. Home Assistant 재시작

### 수동 설치

1. 이 저장소를 클론하거나 ZIP으로 다운로드
2. `custom_components/openrouter/` 폴더를 Home Assistant의 `config/custom_components/` 경로에 복사
3. Home Assistant 재시작

---

## 설정

### 초기 설정

**설정 → 기기 및 서비스 → 통합 구성요소 추가 → OpenRouter**

| 단계 | 항목 | 설명 |
|------|------|------|
| 1 | **Management API Key** | [Management Keys](https://openrouter.ai/settings/management-keys) 페이지에서 발급 |
| 2 | **폴링 주기** | API 호출 간격 (1~60분, 기본 5분) |
| 2 | **환율 모드** | `없음(USD만)` / `고정 환율` / `센서 연동` |
| 2 | **통화** | 환율 변환에 사용할 통화 선택 (기본: HA 시스템 통화) |

### 환율 모드

- **없음**: USD 센서만 생성
- **고정 환율**: 1 USD = ? 값을 직접 입력 (기본: 1450)
- **센서 연동**: HA의 환율 센서 entity를 선택 (예: Open Exchange Rates 통합의 USD→KRW 센서)

환율이 설정되면 각 USD 센서에 대응하는 현지 통화 센서가 추가 생성됩니다.

---

## 생성되는 센서

### 계정 디바이스 (OpenRouter)

| 센서 | 설명 |
|------|------|
| 총 사용량 | 누적 사용 크레딧 |
| 잔액 | 잔여 크레딧 |
| 총 일일 사용량 | 전체 Key 당일 사용량 합산 |
| 총 주간 사용량 | 전체 Key 당주 사용량 합산 |
| 총 월간 사용량 | 전체 Key 당월 사용량 합산 |

### Key별 디바이스 (OpenRouter - {Key 이름})

각 API Key마다 독립된 디바이스가 생성됩니다.

| 센서 | 설명 |
|------|------|
| 사용량 | 누적 사용량 |
| 일일 사용량 | 당일 사용량 (UTC 기준) |
| 주간 사용량 | 당주 사용량 (UTC 월요일 기준) |
| 월간 사용량 | 당월 사용량 (UTC 기준) |
| 한도 | 키에 설정된 한도 |
| 남은 한도 | 잔여 한도 |

환율 변환 활성 시 각 센서마다 통화 변환 센서가 추가로 생성됩니다.

---

## 요구 사항

- Home Assistant 2026.4 이상
- HACS (권장)
- OpenRouter Management API Key
