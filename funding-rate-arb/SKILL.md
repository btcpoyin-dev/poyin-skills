---
name: funding-rate-arb
version: "1.0"
description: 用户报一个标的、想查跨交易所资金费率套利时使用：实时拉各家费率与标记价，统一折算到每小时，算开仓价差、手续费、滑点、净收益和回本时间，结合 7–10 天历史与结算时点给出多空放置策略。
---

# 资金费率套利 Skill 1.0

## 核心原则

**一律按每小时比较；看历史日合计，不看单个快照；结算时点决定开仓时机。**
负费率 = 空头付多头。多头放在费率最负的平台，空头放在付得最少的平台。快照只是当下，下单前必须重拉。

## 一、数据来源（公开接口，无需密钥）

| 平台 | 当前 | 历史 | 周期 |
|---|---|---|---|
| OKX | `https://www.okx.com/api/v5/public/funding-rate?instId=X-USDT-SWAP` | `/api/v5/public/funding-rate-history?instId=X-USDT-SWAP` | 8h |
| 币安 | `https://www.binance.com/fapi/v1/premiumIndex?symbol=XUSDT` | `/fapi/v1/fundingRate?symbol=XUSDT` | 可能 4h，查 `/fapi/v1/fundingInfo` |
| Hyperliquid | POST `https://api.hyperliquid.xyz/info` `{"type":"metaAndAssetCtxs","dex":"xyz"}`（或 `"para"`） | `{"type":"fundingHistory","coin":"xyz:X","startTime":ms}` | 1h |
| Gate / Bitget / Aster | 各自公开 futures 接口 | 同 | 多为 4h/8h，以接口返回为准 |

- `fapi.binance.com` 被地区屏蔽，走 `www.binance.com/fapi`。
- Lighter、Bybit 可能被屏蔽：用 CoinGlass 等聚合站兜底，并标注“推算”。
- 实时面板：https://btc1998.com/stockcoin/unitree-funding

## 二、计算

1. 费率/h = 单期费率 ÷ 周期小时数。
2. 费率差/h = 空头平台费率 − 多头平台费率（负费率下多头收、空头付）。
3. 约 U/h = 名义仓位 × 费率差/h。
4. 开仓价差 = (空头价 − 多头价) ÷ 多头价；正数开仓即有利，负数需费率先赚回。
5. 手续费：两腿开 + 平，吃单/挂单分开算（例：HL 吃单 0.0432%、挂单 0.0144%）。
6. 滑点：买卖价差 + 按仓位规模估冲击，开仓、平仓各算一次。
7. 回本小时 = (−开仓价差 + 手续费 + 滑点) ÷ 费率差/h。

## 三、看历史（7–10 天）

- 负费率常常是阵发的：如 UNITREE 只在北京时间 08:00–16:00 大幅为负，OKX 16:00 那期打到 −1% 上限，其余时段约 0。
- 比较平台用**日合计**，不要拿快照的每小时值直接乘 24。
- 某平台有大幅价格溢价时，必须确认其费率优势在历史上持续，才值得付溢价。

## 四、结算时机

- OKX、币安按**结算瞬间**持仓收费：持仓几分钟也付整期。
- 要付钱的那条腿，在大额结算**刚过之后**开，不要在之前开。

## 五、执行

1. 先用挂单开新腿，成交后再挂单平旧腿。
2. 价格跑开几分钟未成交，改市价补齐，裸敞口风险大于多付的手续费。
3. 负费率连续两期回到 ~0 即平仓。

## 六、输出

表格：策略 | 多头平台 | 空头平台 | 费率差/h | 约 U/h | 开仓价差 | 回本时间；注明数据时间（北京时间）与推算项。然后给出建议：首选、备选、不推荐及原因，并提示下一次大额结算时点。

## 脚本
`scripts/fr_all.py`：拉 12 家公开接口（费率历史、当前费率、标记/指数价、盘口滑点），输出 JSON/CSV。用法：`python3 fr_all.py`（标的与数量在脚本顶部）。Bybit/HTX 需在未被地区封锁的机器上运行。
