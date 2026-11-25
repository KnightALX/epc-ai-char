# EPC P0 MVP 门禁修复复验报告

| 项 | 内容 |
|---|---|
| 结论 | **PASS** |
| 复验角色 | EDA 测试验证（本 bot） |
| 复验对象 | `fail_job` + `table_upper_bound` verify-only；gate FAIL 不写 / 清理 B.db |
| 日期 | 2026-10-21 22:27 CST（Asia/Shanghai） |
| 数据性质 | **合成 DEMO，非真实 PDK** |
| 编排来源 | EDA开发任务编排协调器(Top)「请复验门禁修复」 |
| 关联 | `/workspace/epc_fixtures/P0_MVP_验收报告.md`（初验 PASS；本报告关闭其 §5.1 / §5.2 残留） |

---

## 0. 一页结论

| 声称修复 | 复验结果 |
|---|---|
| 1. `table_upper_bound` 在 `fail_job` 下为 **verify-only**；超界 FAIL，禁止 clip-then-pass | **PASS** |
| 2. gates FAIL 时 **不写 B.db**（并清理目标路径旧库），写 FAIL audit，exit 1 | **PASS** |

**阻塞缺陷：无。**

---

## 1. 绿路径复现（sample yaml）

```bash
cd /workspace && python3 -m epc_engine /workspace/epc_fixtures/epc_job.sample.yaml
```

| 检查 | 期望 | 实测 |
|---|---|---|
| EXIT | 0 | **0** |
| COUNT(*) | 4950 | **4950** |
| distinct (instance,pvt,key) | (9,11,50) | **(9,11,50)** |
| 不完整 (instance,pvt) 组 | 0 | **0** |
| `#0 table_upper_bound` | PASS；mode=verify_only；无 clip | **PASS**；`mode=verify_only`；`before_max=after_max=1387.9`；`cells_clipped=0/25` |
| `#1 relative_delta_vs_source` | `-4%`→×0.96 | **PASS**；`×0.9600`；落库 ratio ∈ [0.959983, 0.960020] |
| Audit | PASS / gates_ok True | **PASS**；`gates_ok: True` |
| B.db | 写出 | `/workspace/epc_fixtures/B_out.sample.db` 存在 |

Stdout 关键行：

```
[epc]   [PASS] #0 table_upper_bound: op<= 1500.0; mode=verify_only; before_max=1387.9; after_max=1387.9; cells_clipped=0/25
[epc]   [PASS] #1 relative_delta_vs_source: delta_pct=-4.0 → ×0.9600; …
[epc] gates: PASS — all constraints PASS
[epc] wrote 4950 rows
[epc] OK
```

绿 audit（`B_out.sample_audit.md`）明确写明：

- `table_upper_bound` / `value_range`：under `on_violation: fail_job` **verify only**（no clip-then-pass）
- On gate FAIL + fail_job：formal B.db is **not** written（prior file at path removed）

---

## 2. 红路径复现（`run_red_upper_bound.sh`，bound=1000）

```bash
bash /workspace/epc_fixtures/run_red_upper_bound.sh
```

脚本将 `#0` 上界改为 **1000**（实测 max≈1387.9），输出到 `/tmp/epc_B_red.db` / `/tmp/epc_B_red_audit.md`，**不改** sample yaml。

| 检查 | 期望 | 实测 |
|---|---|---|
| 引擎 EXIT | ≠0 | **1** |
| 脚本自检 | RED regression PASS | **PASS**（`RED_SCRIPT_EC=0`） |
| `#0` 结果 | FAIL；verify_only；**未 clip** | **FAIL**；`mode=verify_only`；`before_max=after_max=1387.9`；`cells_clipped=0/25` |
| B.db 目标路径 | 不存在 | **`/tmp/epc_B_red.db` absent** |
| FAIL audit | 存在且标明 FAIL | **存在**；title `**FAIL**`；`gates_ok: False`；`B.db written: **no (FAIL / skipped)**`；`rows written: **0**` |
| stderr | gate fail | `[epc] FAIL: constraint gate failed (on_violation=fail_job)` |
| `#1` relative | 仍可评估为 PASS（与 #0 AND） | **PASS**（×0.96 仍正确）；总体 gates 仍因 #0 失败 |

Stdout 关键行：

```
[epc]   [FAIL] #0 table_upper_bound: op<= 1000.0; mode=verify_only; before_max=1387.9; after_max=1387.9; cells_clipped=0/25
[epc] gates: FAIL — #0 table_upper_bound … 
[epc] skipped write of B.db (gates FAIL, on_violation=fail_job)
[epc] audit (FAIL) → /tmp/epc_B_red_audit.md
```

**verify-only 证据要点：** `before_max == after_max == 1387.9` 且 `cells_clipped=0`，说明超界后**没有**把数值 clip 到 1000 再伪 PASS。

---

## 3. 附加抽测

### 3.1 预置旧库后清理 — PASS

在 `/tmp/epc_B_red.db` 预写入 stale SQLite（含 `STALE` 行，size=12288），再以 bound=1000 跑引擎：

| 检查 | 实测 |
|---|---|
| EXIT | **1** |
| stdout | `removed prior/stale B.db → /tmp/epc_B_red.db` |
| stdout | `skipped write of B.db (gates FAIL, on_violation=fail_job)` |
| 跑后 db 存在 | **False** |
| FAIL audit | 写出；`gates_ok: False`；`B.db written: no (FAIL / skipped)` |

### 3.2 不依赖红脚本、仅收紧上界 — PASS

手工改 YAML 副本 `target.value=1000` → `/tmp/epc_job_manual_red.yaml`：

| 检查 | 实测 |
|---|---|
| EXIT | **1** |
| verify_only FAIL | 同红路径 |
| B.db | **absent** |

（初验报告 §3.5 / §5.2 曾记「收紧上界不会失败 / clip-then-pass」——**本行为已关闭**。）

---

## 4. 缺陷与残留

| ID | 严重度 | 描述 | 状态 |
|---|---|---|---|
| — | — | （无阻塞缺陷） | — |

**残留风险（非 FAIL，建议后续）：**

1. **序列化舍入**：`relative_delta` 落库后与精确 ×0.96 仍有 ≤~0.004 绝对误差（显示精度）；审计内存校验为 0。与初验 §5.3 相同，非门禁问题。
2. **非 `fail_job` 策略未本轮抽测**：audit 注明 other policies may clip；若产品还有 warn/clip 策略，需另开用例。
3. **红脚本依赖 `/tmp`**：CI 需保证可写；脚本本身不修改正式 sample yaml（好）。
4. **数据为合成 DEMO**：不得外推为真实工艺结论。

---

## 5. 签署

| 项 | 内容 |
|---|---|
| 总体结论 | **PASS** |
| 关闭的初验残留 | §5.1 门禁失败仍写库 → **已关闭**；§5.2 clip-then-pass → **已关闭**（fail_job + table_upper_bound） |
| 关键证据 | 绿 EXIT0 COUNT=4950 verify_only；红 EXIT1 / no B.db / FAIL audit；stale 清理 OK |
| 报告路径 | `/workspace/epc_fixtures/P0_MVP_门禁复验.md` |
