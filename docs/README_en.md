# OpenRouter Monitor

Home Assistant에서 [OpenRouter](https://openrouter.ai) 잔액과 사용량을 모니터링합니다.
Monitor your [OpenRouter](https://openrouter.ai) balance and usage in Home Assistant.

- 잔액 / 일별 / 주별 / 월별 사용량 추적 | Balance / daily / weekly / monthly usage tracking
- API Key별 독립 디바이스로 분리 | Separate device per API Key
- 15개 주요 통화 환율 변환 | Exchange rate conversion for 15 major currencies
- 한국어 / English / 日本語 / 中文

[한국어](../README.md) | [日本語](README_ja.md) | [中文](README_zh.md)

---

## Installation

### HACS (Recommended)

1. HACS → Integrations → Top-right menu → **Custom repositories**
2. URL: `https://github.com/Lemon-HACS/openrouter_monitor`, Category: `Integration`
3. Search **OpenRouter** and download
4. Restart Home Assistant

### Manual

Copy `custom_components/openrouter/` to your HA `config/custom_components/` and restart.

---

## Configuration

**Settings → Devices & Services → Add Integration → OpenRouter**

| Field | Description |
|-------|-------------|
| **Management API Key** | [Get one here](https://openrouter.ai/settings/management-keys) |
| **Polling interval** | API call interval (1–60 min, default 5) |
| **Exchange rate mode** | `None (USD only)` / `Fixed rate` / `Sensor` |
| **Currency** | Target currency for conversion (default: HA system currency) |

---

## Sensors

### Account (OpenRouter)

Balance, total usage (cumulative), total daily/weekly/monthly usage (sum of all keys)

### Per Key (OpenRouter - {Key name})

Usage (cumulative), daily/weekly/monthly usage, limit, limit remaining

When exchange rate conversion is enabled, a converted version of each sensor is also created.

---

## Requirements

- Home Assistant 2026.4+
- OpenRouter Management API Key
