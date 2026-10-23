---
name: 期权正EV回测
description: >-
  期权正 EV 回测：用户想在美股某标的上买虚值 call/put，问哪个行权价最划算、要多少倍赔付、
  拿历史数据回测是否正 EV 时使用。先比隐含波动率与同类行情实际波动，再用两张表（表一赔率、
  表二历史胜率）检验，并按凯利给仓位。只是历史回测，不代表必然有优势。
  Use when the user wants to buy OTM calls/puts on a US ticker and check, by historical
  backtest, which strike is best value and whether it is positive EV (with IV check and Kelly sizing).
  触发说法：期权正EV回测 TQQQ call 10/30（旧名：ED 期权模型、索普优势模型）
---

# 期权正 EV 回测（表零 IV 对比 + 表一赔率 + 表二历史胜率 + 仓位）

定位：这只是用历史数据回测正 EV，不是确定的优势。表零、表一、表二都过关才考虑出手，任一不过就不做。

Input: ticker, direction (call/put), expiry. Optional: budget (U), specific strikes. Analysis only; never place orders.

## Step 1 Data

- Live spot and option chain for the expiry (e.g. Nasdaq API `api.nasdaq.com/api/quote/<T>/option-chain?assetclass=etf|stocks&fromdate=&todate=`; filter by date, drop the type param). Use ask as entry price.
- Count remaining trading days N to expiry (note weekend/holiday gaps).
- Daily adjusted closes, max history (Yahoo chart API `range=max&interval=1d`).
- Recent move: 5-day and 10-day % change, to classify the current regime.

## Step 1.5 Table 0: IV vs realized vol (先看贵不贱)

- Current IV of the chosen expiry (ATM and target strike) vs annualized realized vol of N-day windows in the similar regime (median and 75th pct).
- IV ≥ 相似行情实际波动中位数 → 标"期权偏贵"，后面即使 🟢 也降级为观察；IV 明显低于 → 标"偏便宜"，这是正 EV 的主要来源。

## Step 2 Table 1: strike value (挑行权价)

For ~6-8 OTM strikes around the target, one row each:

行权价 | ask | 预算可买张数 | 距现价% | 回本价(+%) | 10x价(+%) | 20x价(+%) | 历史EV/1$（全部/相似/对应极端）

- 回本 = K + ask; Nx price = K + N\*ask (call; mirror for put).
- EV per $1 = mean over historical N-day windows of max(0, S\*(1+r)-K)/ask.
- Recommend the best EV/price balance; flag overpriced strikes (e.g. 74 worse than 75) and penny strikes whose EV is distorted by spread.

## Step 3 Table 2: historical simulation (历史模拟) for the chosen strike

Regimes (rows or columns): 全部天数 / 与当前相似（5日跌幅同区间） / 5日≤−10% / 5日≤−15% (adjust to current situation; for puts use rallies). Show sample count.

Per regime: 胜率(≥回本) , ≥10x , ≥20x , ≥50x , 平均盈利倍数 , EV/1$ , 正EV门槛 = 1/平均盈利倍数.

Cell format: `历史% / 门槛%` with 🟢 if 历史 ≥ 门槛, 🔴 otherwise; the ≥Nx rows use sufficient threshold 1/N.

- Count independent episodes, not overlapping windows: windows overlapping the same move count once. Show both 窗口数 / 独立事件数.
- 独立事件 < 15 → 标"样本不足"，该档不给 🟢.
- Note clustered years (e.g. 2020, 2022). Strikes × regimes scanned many times: don't treat a single 🟢 as edge.

## Step 3.5 Pass rule + sizing (仓位)

- 出手门槛：EV/1$ ≥ 1.3（按 ask 计，已含价差）且至少 2 档行情 🟢 且表零不是"偏贵"。
- 仓位：p = 历史胜率(≥回本), b = 平均盈利倍数; Kelly f = (p·b − (1−p))/b，取 1/4 Kelly，单笔上限总资金 1–2%。f ≤ 0 就不做。

## Step 4 Conclusion (short)

- Which regime applies now (not a choice).
- 历史概率是基准；用户自己的把握 > 门槛 才是正EV（算牌逻辑）. Say what news/move would be needed.
- Wording: “超过即正 EV”, not “过了一定赚”.

Output as markdown tables in chat, Chinese, concise.

## 输出

表零 IV 对比 + 两张表：①行权价性价比表（报价/张数/回本价/10x20x价/EV）②历史模拟分状态胜率与正 EV 门槛（🟢/🔴，含独立事件数）+ 是否过门槛与建议仓位

## 复盘

每次实际出手记入交易日志（行权价、价格、当时表零/EV、结果）；满 20 笔回看实际胜率与回报是否接近回测，不接近就说明回测的 EV 不可靠。
