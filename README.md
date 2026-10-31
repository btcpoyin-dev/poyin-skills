# poyin-skills

Poyin 的个人技能（Agent skills）。每个技能一个文件夹，内含 `SKILL.md`。

| 技能 | 路径 | 用途 |
|---|---|---|
| 期权正EV回测 | [option-ev-backtest/SKILL.md](option-ev-backtest/SKILL.md) | 买虚值 call/put 前，比 IV 与实际波动、挑最划算行权价、用历史数据回测是否正 EV，并按 1/4 凯利给仓位 |
| Sell-put 收益表 | [sell-put-yield-table/SKILL.md](sell-put-yield-table/SKILL.md) | 想卖现金担保 put 时，看各行权价/到期日的安全垫和年化收益 |
| 市场情绪雷达 | [market-sentiment-radar/SKILL.md](market-sentiment-radar/SKILL.md) | 采集 A 股与 Crypto 情绪，核验时间，分析关键 K 线事件与情绪变化 |
| SNIPE 交易记录 V2.2 | [snipe/SKILL.md](snipe/SKILL.md) | 简洁记录交易想法、实际操作和本人复盘；明确授权后才写入 |

## SNIPE V2.2

安装：`npx -y skills add btcpoyin-dev/poyin-skills --skill snipe`

使用示例：“帮我整理这笔交易，先给草稿，不要写入。”

需要能读取、更新用户指定日志的工具；Notion 用户需自行授权并指定目标页面。通用模板见 [snipe/references/trading-log-template.md](snipe/references/trading-log-template.md)。仓库不包含个人交易记录或账户配置。

Source = Notion 🧰 技能库, migrated 2026-10-23.
