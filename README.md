# RollSlope Quant

RollSlope Quant 是一個以「滾動分段線性斜率」作為核心特徵的自動化交易系統範例。
核心 AI 決策路由器命名為 **Plutus**。

## 核心功能

- Data Layer：接收與整理時間價格資料。
- Model Layer：使用 `pwlf` 優先進行 3 段分段線性擬合，輸出 `t1, t2, t3` 與 2 個 breakpoints。
- AI Layer：Plutus Router Agent 根據 V 轉、倒 V 頂、R²、連線狀態、回撤狀態進行決策。
- Risk Layer：Kelly position sizing、Historical VaR、Trailing Stop、Circuit Breaker。

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> `pwlf` 為正式模型依賴。若本機尚未安裝 `pwlf`，系統會自動使用內建 NumPy fallback 進行 demo。

## 執行 V 轉模擬

```bash
python scripts/run_simulation.py
```

## 專案設計原則

本專案遵循 Clean Architecture：

- `domain/`：交易規則、資料模型、抽象 port。
- `application/`：use case 與 Plutus Agent 編排。
- `infrastructure/`：外部技術實作，例如 pwlf、WebSocket、Broker、VaR。
- `interfaces/`：CLI、API、Dashboard 入口。

## 永豐 Shioaji API Adapter

本專案已加入 `ShioajiStockBroker`，位置：

```text
src/rollslope_quant/infrastructure/broker/shioaji_stock_broker.py
```

設計方式：

```text
Plutus TradeSignal
    ↓
execute_trade_signal.py
    ↓
BrokerPort
    ↓
ShioajiStockBroker
    ↓
shioaji SDK / 永豐金證券
```

### 安全設定

複製環境變數範例：

```bash
cp .env.example .env
```

至少設定：

```bash
SHIOAJI_API_KEY=你的金鑰
SHIOAJI_SECRET_KEY=你的密鑰
SHIOAJI_SIMULATION=true
ALLOW_LIVE_TRADING=false
```

正式環境下單前，再設定 CA：

```bash
SHIOAJI_CA_PATH=/secure/path/Sinopac.pfx
SHIOAJI_CA_PASSWORD=你的憑證密碼
SHIOAJI_PERSON_ID=你的身分證字號
```

安全開關：

```text
SHIOAJI_SIMULATION=true      # 模擬環境
ALLOW_LIVE_TRADING=false     # 禁止正式下單
```

即使 `SHIOAJI_SIMULATION=false`，只要 `ALLOW_LIVE_TRADING=false`，系統仍會拒絕正式下單。

### 檢查登入

```bash
python scripts/check_shioaji_login.py
```

### 跑一次 Plutus 訊號並接 Broker

紙上交易：

```bash
python scripts/run_shioaji_signal_once.py --broker paper --symbol 2330 --equity 1000000 --max-lots 1
```

永豐模擬環境：

```bash
ROLLSLOPE_BROKER=shioaji \
SHIOAJI_SIMULATION=true \
ALLOW_LIVE_TRADING=false \
python scripts/run_shioaji_signal_once.py --broker shioaji --symbol 2330 --equity 1000000 --max-lots 1
```

### 台股張數語義

```text
quantity = 1 代表 1 張，也就是 1000 股。
```

目前預設：

```text
order_kind = MARKET
order_type = IOC
order_lot  = Common
order_cond = Cash
```

### 測試

```bash
pytest -q
```
