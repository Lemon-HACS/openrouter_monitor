# OpenRouter Monitor

Home Assistant에서 [OpenRouter](https://openrouter.ai) 잔액과 사용량을 모니터링합니다.
Monitor your [OpenRouter](https://openrouter.ai) balance and usage in Home Assistant.

- 잔액 / 일별 / 주별 / 월별 사용량 추적 | Balance / daily / weekly / monthly usage tracking
- API Key별 독립 디바이스로 분리 | Separate device per API Key
- 15개 주요 통화 환율 변환 | Exchange rate conversion for 15 major currencies
- 한국어 / English / 日本語 / 中文

[한국어](../README.md) | [English](README_en.md) | [中文](README_zh.md)

---

## インストール

### HACS（推奨）

1. HACS → インテグレーション → 右上メニュー → **カスタムリポジトリ**
2. URL: `https://github.com/Lemon-HACS/openrouter_monitor`、カテゴリ: `インテグレーション`
3. **OpenRouter** を検索してダウンロード
4. Home Assistantを再起動

### 手動インストール

`custom_components/openrouter/` をHAの `config/custom_components/` にコピーして再起動

---

## 設定

**設定 → デバイスとサービス → インテグレーション追加 → OpenRouter**

| 項目 | 説明 |
|------|------|
| **Management APIキー** | [こちらで発行](https://openrouter.ai/settings/management-keys) |
| **ポーリング間隔** | API呼び出し間隔（1〜60分、デフォルト5分） |
| **為替レートモード** | `なし（USDのみ）` / `固定レート` / `センサー` |
| **通貨** | 変換先の通貨（デフォルト: HAシステム通貨） |

---

## センサー

### アカウント (OpenRouter)

残高、合計使用量（累計）、合計日次/週次/月次使用量（全キー合算）

### キー別 (OpenRouter - {キー名})

使用量（累計）、日次/週次/月次使用量、上限、残り上限

為替レート変換が有効な場合、各センサーの通貨変換バージョンも生成されます。

---

## 要件

- Home Assistant 2026.4以上
- OpenRouter Management APIキー
