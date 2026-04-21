# OpenRouter Monitor

Home Assistant에서 [OpenRouter](https://openrouter.ai) 잔액과 사용량을 모니터링합니다.
Monitor your [OpenRouter](https://openrouter.ai) balance and usage in Home Assistant.

- 잔액 / 일별 / 주별 / 월별 사용량 추적 | Balance / daily / weekly / monthly usage tracking
- API Key별 독립 디바이스로 분리 | Separate device per API Key
- 15개 주요 통화 환율 변환 | Exchange rate conversion for 15 major currencies
- 한국어 / English / 日本語 / 中文

[한국어](../README.md) | [English](README_en.md) | [日本語](README_ja.md)

---

## 安装

### HACS（推荐）

1. HACS → 集成 → 右上角菜单 → **自定义存储库**
2. URL: `https://github.com/Lemon-HACS/openrouter_monitor`，类别: `集成`
3. 搜索 **OpenRouter** 并下载
4. 重启 Home Assistant

### 手动安装

将 `custom_components/openrouter/` 复制到 HA 的 `config/custom_components/` 后重启

---

## 配置

**设置 → 设备与服务 → 添加集成 → OpenRouter**

| 项目 | 说明 |
|------|------|
| **Management API 密钥** | [在此获取](https://openrouter.ai/settings/management-keys) |
| **轮询间隔** | API 调用间隔（1~60分钟，默认5分钟） |
| **汇率模式** | `无（仅 USD）` / `固定汇率` / `传感器` |
| **货币** | 汇率转换目标货币（默认：HA 系统货币） |

---

## 传感器

### 账户 (OpenRouter)

余额、总使用量（累计）、每日/每周/每月总使用量（所有密钥合计）

### 按密钥 (OpenRouter - {密钥名称})

使用量（累计）、每日/每周/每月使用量、限额、剩余限额

启用汇率转换后，每个传感器会额外生成货币转换版本。

---

## 要求

- Home Assistant 2026.4 以上
- OpenRouter Management API 密钥
