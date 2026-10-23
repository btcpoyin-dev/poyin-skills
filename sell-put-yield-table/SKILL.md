---
name: Sell-put 收益表
description: >-
  When the user names one or more US tickers (optionally strikes, expiries, or a
  reference price) and wants to know the cushion and yield of selling
  cash-secured puts.
  用途：想卖现金担保 put 时，看各行权价/到期日的安全垫和年化收益。
  触发说法：COIN CRCL 卖 put 收益表
---

# Sell-put yield table

1. Inputs: tickers; optional strikes, expiries, reference spot. If no expiries are given, default to the next ~4 weekly/monthly expiries up to ~30 days out. If no strikes are given, default to the listed strikes nearest 5%, 10%, 15%, 20% below spot.
2. Pull live data (Nasdaq option-chain API `api.nasdaq.com/api/quote/<TICKER>/option-chain?assetclass=stocks`, fallback Yahoo): spot, bid/ask/open interest for each put. Also look up the next earnings date.
3. Compute per row:
   - 离现价跌多少 = (spot - strike) / spot
   - 收益率 = bid / strike (premium per contract ÷ cash secured per contract; use bid as the realistic fill)
   - 年化 = 收益率 × 365 / days to expiry
4. Output one table per ticker with ONLY these columns: 到期 | 行权价 | 离现价跌多少 | 收益率 | 年化. Header line: ticker, spot, earnings date and whether each expiry spans earnings. Footer: quote timestamp (user's timezone) and source.
5. Notes only when relevant: thin open interest, missing strikes, stale pre-market quotes. Never fabricate; mark missing quotes. Never place orders.

## 输出

按标的×行权价×到期日的安全垫%、权利金、年化收益率表
