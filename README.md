# OpenRouter Monitor

Home Assistant에서 [OpenRouter](https://openrouter.ai) 잔액과 사용량을 모니터링합니다.
Monitor your [OpenRouter](https://openrouter.ai) balance and usage in Home Assistant.

- 잔액 / 일별 / 주별 / 월별 사용량 추적 | Balance / daily / weekly / monthly usage tracking
- API Key별 독립 디바이스로 분리 | Separate device per API Key
- 15개 주요 통화 환율 변환 | Exchange rate conversion for 15 major currencies
- 한국어 / English / 日本語 / 中文

[English](docs/README_en.md) | [日本語](docs/README_ja.md) | [中文](docs/README_zh.md)

---

## 설치

### HACS (권장)

1. HACS → 통합 구성요소 → 우측 상단 메뉴 → **사용자 지정 저장소 추가**
2. URL: `https://github.com/Lemon-HACS/openrouter_monitor`, 카테고리: `통합 구성요소`
3. **OpenRouter** 검색 후 다운로드
4. Home Assistant 재시작

### 수동 설치

`custom_components/openrouter/` 폴더를 HA의 `config/custom_components/`에 복사 후 재시작

---

## 설정

**설정 → 기기 및 서비스 → 통합 구성요소 추가 → OpenRouter**

| 항목 | 설명 |
|------|------|
| **Management API Key** | [여기서 발급](https://openrouter.ai/settings/management-keys) |
| **폴링 주기** | API 호출 간격 (1~60분, 기본 5분) |
| **환율 모드** | `없음(USD만)` / `고정 환율` / `센서 연동` |
| **통화** | 환율 변환 대상 통화 (기본: HA 시스템 통화) |

---

## 센서

### 계정 (OpenRouter)

잔액, 총 사용량(누적), 총 일일/주간/월간 사용량(전체 Key 합산)

### Key별 (OpenRouter - {Key 이름})

사용량(누적), 일일/주간/월간 사용량, 한도, 남은 한도

환율 변환 활성 시 각 센서의 통화 변환 버전이 추가로 생성됩니다.

---

## 요구 사항

- Home Assistant 2026.4 이상
- OpenRouter Management API Key
