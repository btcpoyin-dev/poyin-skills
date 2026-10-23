---
name: 索普优势模型
description: >-
  When the user wants to buy short-dated OTM calls or puts (lottery-style) on a
  US ticker and asks which strike is best value, what payoff multiples need, or
  whether it is positive EV versus history (索普优势模型).
  用途：想买短期虚值 call/put（彩票期权）时，挑最划算的行权价并用历史模拟判断是否正 EV。
  触发说法：索普优势模型 TQQQ call 10/30
---

# 索普优势模型（买方彩票期权：挑行权价 + 历史模拟 EV）

Input: ticker, direction (call/put), expiry. Optional: budget (U), specific strikes. Analysis only; never place orders.

## Step 1 Data

- Live spot and option chain for the expiry (e.g. Nasdaq API `api.nasdaq.com/api/quote/<T>/option-chain?assetclass=etf|stocks&fromdate=&todate=`; filter by date, drop the type param). Use ask as entry price.
- Count remaining trading days N to expiry (note weekend/holiday gaps).
- Daily adjusted closes, max history (Yahoo chart API `range=max&interval=1d`).
- Recent move: 5-day and 10-day % change, to classify the current regime.

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

- Note small samples and clustered years (e.g. 2020, 2022).

## Step 4 Conclusion (short)

- Which regime applies now (not a choice).
- 历史概率是基准；用户自己的把握 > 门槛 才是正EV（算牌逻辑）. Say what news/move would be needed.
- Wording: “超过即正 EV”, not “过了一定赚”.

Output as markdown tables in chat, Chinese, concise.

## 输出

两张表：①行权价性价比表（报价/张数/回本价/10x20x价/EV）②历史模拟分状态胜率与正 EV 门槛（🟢/🔴）
