# EPC 加固《epc_ab / algo_holdout 硬门禁》正式验收报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS**（阻塞缺陷：无） |
| 日期 | 2026-10-22 14:42 Asia/Shanghai |
| 规格 | `/workspace/EPC_加固_epc_ab_holdout硬门禁_需求_v0.md` **v0**（Kai：Q1=A 离线硬+在线 stamp；Q2=`≤`） |
| 引擎 | `/workspace/epc_engine/`（验收**未改**产品代码；仅写入本报告于 fixtures） |
| 验收方 | 独立复跑 `run_ab_hard_suite.sh` + U0–U5 抽检（非盲签开发自测） |
| 开发自测 | `/workspace/epc_fixtures/AB_hard_自测.md`（仅参考） |
| 解耦 | 与 Op-Geom H3-hard / `run_p2_suite` / `eval_h3.py` **并列、不缠死** |
| DEMO | fixture ≠ 真 PDK |

---

## 1. 一键 suite（独立复跑）

```bash
bash /workspace/epc_fixtures/run_ab_hard_suite.sh
# → SUMMARY pass=8 fail=0 ；SUITE_EXIT=0
```

### Suite 摘录

```text
======== AB-hard suite ========
=== U2/U3 offline gate logic ===
gate_logic PASS
OK U2_U3_gate_logic
=== seed/verify green stamp ===
ab_hard: PASS protocol=loi_v0+lop_v0 loi=0.102257≤0.31168 lop=5.22059e-05≤5.2333e-05 stamp_sha16=bd6ecde2f27e622b
OK U1_stamp_green
=== U1 online green residual ===
… ab_hard: PASS … writing B.db → …/B_out.ab_hard_green.db
OK U1_online_green
=== U4 online red bad stamp ===
… ab_hard: FAIL (offline_fail) …
OK U4_online_red_stamp
=== U4 missing stamp ===
… ab_hard: FAIL (missing_stamp) …
OK U4_missing_stamp
=== U5 idw skip ===
… ab_hard: SKIP (backend=idw_nn) …
OK U5_idw_skip
=== U0 sample residual ===
… OK
OK U0_sample
=== AB-M4 decouple (suite isolation) ===
OK AB-M4_h3_hard_present_untouched_by_this_suite
======== SUMMARY pass=8 fail=0 ========
```

| 计数 | 值 |
|---|---|
| pass | **8** |
| fail | **0** |
| SUITE_EXIT | **0** |

---

## 2. U0–U5 证据表

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| **U0** | 回归 | **PASS** | **sample** residual：EXIT **0**，落盘 `B_out.sample.db`，audit `ab_hard: PASS`。**约束绿** `p1_improve_green`：EXIT **0**，G3=16，约束 PASS=17。**约束红**：R1 vague EXIT **2**（拒载）；R2 proxy forbid EXIT **1**、不落盘。**P2 idw 绿** `job_corner_fill_green`：EXIT **0**，COUNT=2000，`H3-hard SKIP (backend=idw_nn)`。**P2 residual Geom 红不变**：`job_corner_fill_residual_h3hard` EXIT **1**、无 `out_geom_residual_h3hard.db`；`h3_hard: FAIL`，p95_sel≈0.02632 > p95_idw≈0.00767（与既有加固报告一致） |
| **U1** | 离线绿 | **PASS** | `algo_holdout_report.md`：**AB-hard-LOI** PASS（0.102257 ≤ 0.31168）；**AB-hard-LOP** PASS（5.22059e-05 ≤ 5.2333e-05）；两路 p95 + delta + protocol 并列；`Hard gates overall: ALL PASS`（compare `≤`）。现行 stamp `residual_gbdt.joblib.ab_hard.json`：`ab_hard=PASS`，sha16=`bd6ecde2f27e622b`。在线绿 job EXIT **0**、有 B.db、audit `ab_hard: PASS`。用报表数字复算 `evaluate_ab_hard_gates` → True |
| **U2** | 离线红 | **PASS** | `evaluate_ab_hard_gates(0.2,0.1,0.05,0.05)` → overall FAIL，`AB-hard-LOI=False`；LOP 劣化同理 FAIL。比较符为 `<=`：`p95_sel > p95_idw` 必红。Suite 项 `U2_U3_gate_logic` OK |
| **U3** | 比较符 `≤` | **PASS** | `evaluate_ab_hard_gates(0.1,0.1,0.05,0.05)` → **PASS**（equality）；detail `compare='<='`。严格 `<` 不再作为唯一绿条件。别名门 `P-LOI-base` / `P-LOP` 与 AB-hard 同布尔 |
| **U4** | 在线 stamp | **PASS** | **坏 stamp**（`ab_hard=FAIL` + p95_sel>p95_idw）：EXIT **1**；**无** `B_out.ab_hard_red.db`；audit `ab_hard: FAIL`，reason=`offline_fail`。**缺 stamp**：EXIT **1**；无 B.db；audit `ab_hard: FAIL`，reason=`missing_stamp`。独立复跑与 suite 一致 |
| **U5** | idw 跳过 | **PASS** | `epc_job.ab_hard_idw.yaml` backend=`idw_nn`：EXIT **0**；有 B.db；audit `ab_hard: SKIP`；功能约束门禁仍 PASS（16/16），AB-hard **不挡** |

Should（AB-S*）未做者不挡 PASS；Won't（AB-W1–W4）未当缺陷。

---

## 3. 关键 EXIT / 落盘一览（本轮独立）

| 场景 | EXIT | B.db | audit 要点 |
|---|---|---|---|
| AB 在线绿 residual | **0** | 有 | `ab_hard: PASS`；loi 0.102257≤0.31168；lop 5.22059e-05≤5.2333e-05 |
| AB 在线 idw | **0** | 有 | `ab_hard: SKIP` |
| AB 坏 stamp | **1** | **无** | `ab_hard: FAIL` / `offline_fail` |
| AB 缺 stamp | **1** | **无** | `ab_hard: FAIL` / `missing_stamp` |
| sample residual | **0** | 有 | `ab_hard: PASS` |
| P1 约束绿 | **0** | 有 | 约束全 PASS |
| P1 R1 vague | **2** | 无 | 拒载 |
| P1 R2 proxy | **1** | 无 | 约束门禁 FAIL |
| P2 Geom idw 绿 | **0** | 有 | H3-hard SKIP |
| P2 Geom residual H3 | **1** | 无 | H3-hard FAIL（行为不变） |

---

## 4. 解耦抽检（AB-M4）

| 检查 | 结果 |
|---|---|
| Suite 独立脚本 | `epc_fixtures/run_ab_hard_suite.sh`（**未**并入 `run_p2_suite` / `eval_h3`） |
| `epc_engine/ab_hard.py` | **无** import `modes.h3_hard`（仅文档提及解耦） |
| `modes/h3_hard.py` | 仍在；本验收未改产品代码；P2 residual Geom 红行为与既有加固报告一致 |

---

## 5. 已知限制 / 非阻塞

1. **全量离线 holdout 折**（`python -m epc_engine.train --skip-train`）本轮未重跑（自测标注「慢；可选」）；U1 以现行 `algo_holdout_report.md` 两路 p95 + stamp + 门禁函数复算为准，与 Kai Q1=A（离线硬结果经 stamp 在线只读）一致。
2. **Should** AB-S1/S2/S3：stamp sidecar 已落地（S1 实质满足）；CI 红夹具已由 suite mock（S2）；比较符说明见自测 AB-S3 — 均不挡 PASS。
3. **DEMO fixture ≠ 真 PDK**；报表/stamp 数字绑定现行 `A_ref` + `residual_gbdt` DEMO 模型。
4. 并行双开 `epc_engine` 对本机曾出现长时间高 CPU（疑似争用）；验收改为串行复跑后均秒级结束 — **非产品缺陷**。

---

## 6. 结论

**PASS**。U0–U5 无失败项；`run_ab_hard_suite.sh` **pass=8 fail=0**；在线绿/红/idw 与回归路径符合需求 v0。

**报告路径**：`/workspace/epc_fixtures/加固_epc_ab_holdout硬门禁_验收报告.md`
