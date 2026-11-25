# EPC 加固《残差硬门禁》需求 v0

| 项 | 内容 |
|---|---|
| 状态 | **v0**（Kai 开加固小增量；对标 P2 验收非阻塞建议；**本侧不扇出**；拍板后由编排器交开发） |
| 日期 | 2026-10-21（Asia/Shanghai） |
| 触发 | `/workspace/epc_fixtures/P2_可复用算子包_验收报告.md` §5–§6：四角-only + Geom+`residual_gbdt` p95 劣于 `idw_nn`；H3 Geom 实现偏软（`ok ≈ finite(idw) ∧ idw<0.2`） |
| 锚点 | `/workspace/EPC_P2_可复用算子包_需求_v0.md` §5 H3；P1 S5=`fail_job`；算法升级 hold-out 报表并列口径 |
| 引擎 | `/workspace/epc_engine/`；评估脚本现状 `epc_fixtures/p2/eval_h3.py` |

> 本轮 = **把门钉硬**，防止绿路径默默切到劣于 IDW 的 residual。  
> **非目标**：重训冲榜、换 prior、真工艺标定、改 `char_data` schema、重开 P0/P1、替代 P0 主故事。

---

## 1. 目标

1. 将「所选非-`idw_nn` backend 的 p95 **≤** 同协议 `idw_nn`」从软 flag 升为 **硬断言（H3-hard）**。  
2. 失败策略与 **S5** 一致：`fail_job`、**不落盘** 输出 db。  
3. 报表并列 `p95_selected` / `p95_idw_nn` / `delta` / `pass`，避免口径漂移。  
4. fixtures / suite 增量可一键复现；P2 绿默认 **保持** `idw_nn`（不因本轮被迫改绿路径）。

---

## 2. H3-hard 定义（钉死）

### 2.1 比较符

| 项 | 钉死 |
|---|---|
| 比较 | `p95_rel(selected_backend) ≤ p95_rel(idw_nn)`（**允许相等**） |
| 不做 | **不**要求严格 `<`（原 P2「推荐严格 <」降为报表旁注，**不**作硬 FAIL） |
| ε | 相对误差定义与现 H3 / 算法升级一致：`\|pred−truth\| / max(\|truth\|, 1e-12)`；p95 在 hold-out cell 集合上 |
| 并列 | 报表必须同时写出两路 p95、比值或差、`selected_backend`、协议 id（算子+hold-out 描述） |
| 适用 backend | 凡 `construct.backend ∉ {idw_nn}`（含 `residual_gbdt` 及未来非 idw）；`idw_nn` 自身 **跳过** H3-hard（仍受既有 H3 实用上限，见下） |

### 2.2 与既有 H3 的关系

| 层 | 谁必须过 |
|---|---|
| **H3-base**（已有） | 分算子原门槛仍有效（Geom：idw 同协议有限且 DEMO 实用 `p95_idw < 0.2`；Miss：孔 p95&lt;0.15；Sparse：leave-one ≤ 同点基线） |
| **H3-hard**（本轮新增） | 当所选 backend ≠ `idw_nn` 时，**额外**强制 `p95_selected ≤ p95_idw_nn` 同协议；失败 → 整 job **FAIL** |

实现建议：`eval_h3.py`（及 job 内联 gate，若有）对 Geom 的 `ok` 改为：

```text
ok = finite(p95_idw) ∧ (p95_idw < 0.2) ∧ (
      backend == idw_nn  ∨  finite(p95_selected) ∧ p95_selected ≤ p95_idw
    )
```

（Miss/Sparse 见 §3；数值阈值不变。）

---

## 3. 适用范围（推荐默认）

| 范围 | 本轮 | 理由 |
|---|---|---|
| **Op-Geom** | **必须** | 验收报告唯一暴露「残差劣于 IDW」的洞；四角 prior 协议与现 `eval_h3` hold-out 一致 |
| **Op-Miss** | **同规则启用** | 成本低；当前 residual 通常不劣于 idw；统一断言防漂移 |
| **Op-Sparse** | **同规则启用** | 现 leave-one 已比 ≤ idw；升硬即可，避免两套口径 |
| **`mode=epc_ab` 主路径 hold-out** | **本轮不做** | 已有算法升级 / PVT 残差独立门禁与报表；避免本轮与 LOI/LOP 协议缠死。标 **下次**（可选：把「selected ≤ idw」并入 `algo_holdout` 硬断言） |

**推荐默认即上表**；若 Kai 要缩到「仅 Geom」，实现跟拍板，Miss/Sparse 保持现软比较即可。

---

## 4. 失败策略与绿夹具

### 4.1 失败策略（钉死）

| 项 | 规则 |
|---|---|
| 违规 | H3-hard 不通过 → **`fail_job`**：EXIT≠0，输出 db **不落盘**（与 S5 / P2 红路径一致） |
| Audit | 必须含 `h3_hard: FAIL`、两路 p95、backend、协议摘要 |
| 回退 | **禁止** 静默把 backend 改回 `idw_nn` 后当绿过；允许 YAML 显式 `fallback: idw_nn` 仅在模型缺失时（既有语义），且 audit 注明；**精度劣于 idw 不算「模型缺失」** |

### 4.2 绿夹具策略（推荐默认）

| 项 | 推荐 |
|---|---|
| Op-Geom 绿默认 backend | **保持 `idw_nn`**（与现 F1 PASS 一致；不改绿默认） |
| residual 对照 | **新增** 硬门用例，而不是把绿改成 residual |
| 预期 | 当前 DEMO 四角协议下 `residual_gbdt` Geom **应 H3-hard FAIL**（已知 p95_res≈0.026 &gt; p95_idw≈0.0077）——这是加固要锁住的行为，**不是**缺陷 |

---

## 5. 额外可选加固（≤2）

| ID | 内容 | 本轮 / 下次 |
|---|---|---|
| **R1** | Suite 硬检查：绿 Geom YAML 含 `require_corner_coverage: true`；缺角红仍 FAIL；`run_p2_suite` 断言「绿未关覆盖」 | **本轮**（文档+1 断言，几乎零算法） |
| **R2** | `mode`/`operator` 冲突已拒载：升为套件 **具名硬用例**（已有则补断言名 `F_mode_conflict` 进报告表） | **本轮**（若已覆盖则只改报告勾选） |
| — | 把 H3-hard 扩到 `epc_ab` LOI | **下次**（见 §3） |
| — | 为 residual 换 denser prior / 重训使 Geom 过硬门 | **非本轮**（非目标） |

---

## 6. 验收 F / Fixtures 增量

### 6.1 F 清单（本轮）

| # | 项 | 标准 |
|---|---|---|
| F0 | 回归 | 现 P2 F0–F5、sample、P1 绿红 **仍过**；Op-Geom 绿仍为 `idw_nn` |
| F1 | H3-hard · Geom+idw | 绿路径：跳过 hard 或 hard 平凡过；H3-base 仍过 |
| F2 | H3-hard · Geom+residual | 固定四角 hold-out 协议：`backend=residual_gbdt` → **EXIT≠0、不落盘**；报表两路 p95 且 `p95_res > p95_idw` 时 `h3_hard=FAIL`（锁定已知限制） |
| F3 | H3-hard · Miss/Sparse（若 §3 启用） | `backend≠idw` 时套用 ≤ idw；现绿若用 residual 且已 ≤ idw → 仍 PASS；人为劣化 fixture（可选）可红 |
| F4 | Audit | 含 `h3_hard`、`p95_selected`、`p95_idw_nn`、`backend`、协议 id |
| F5 | R1/R2 | 角覆盖断言 + mode 冲突具名用例进 suite 报告 |

### 6.2 Fixtures 建议（增量，目录 `/workspace/epc_fixtures/p2/`）

| 文件 | 角色 |
|---|---|
| `job_corner_fill_residual_h3hard.yaml` | 同绿几何 seed/target/pvt，**仅** `construct.backend: residual_gbdt`；期望 **红**（H3-hard FAIL） |
| （可选）`job_*_residual_ok.yaml` | 仅当未来 residual ≤ idw 时再加绿；**本轮不要求造假绿** |
| `eval_h3.py` | 实现 §2.2 `ok` 公式；输出写入 `h3_report.md` / 分算子 report |
| `run_p2_suite.sh` | 纳入 F2（及 F3/F5）；汇总进 `P2_算子包_验收报告.md` 或短文 `加固_残差硬门禁_验收报告.md` |

禁止覆盖 `A_ref.db`；红路径不得留下 `out_*.db`。

---

## 7. 非目标

- 重训 / 调参使四角+residual 冲过 IDW  
- 改 schema、改 Instance/PVT 解析、重开 P0/P1 约束语义  
- 真工艺 / 真 PDK 标定  
- 把 P2 升格为唯一产品故事  
- 本轮强制改 Op-Geom 绿默认 backend 为 residual  

---

## 8. 须 Kai 拍板（仅 1 问；其余为推荐默认）

| # | 问 | 推荐默认 |
|---|---|---|
| **Q1** | H3-hard 范围：仅 Op-Geom，还是 Geom+Miss+Sparse？ | **Geom+Miss+Sparse**（§3）；`epc_ab` 下次 |
| — | 比较符 ≤ vs &lt; | **已钉死 ≤**（本需求不开放） |
| — | 绿默认 backend | **已钉死保持 idw_nn**；residual 走红对照 F2 |
| — | 失败策略 | **已钉死 fail_job 不落盘** |

无更多拍板项。Kai 若只回「同意默认」或只答 Q1，即可交接开发。

---

## 9. 一页结论

- **H3-hard**：非-`idw_nn` backend 必须 `p95 ≤` 同协议 `idw_nn`（允许 =）；报表并列；失败 `fail_job` 不落盘。  
- **本轮必做** Op-Geom；**推荐** Miss/Sparse 同规则；`epc_ab` hold-out **下次**。  
- 绿 Geom **保持 idw**；新增 residual **红**用例锁住「四角+residual 劣于 IDW」这一已知限制。  
- 可选本轮：角覆盖断言 + mode 冲突具名硬检查。  

**本文路径**：`/workspace/EPC_加固_残差硬门禁_需求_v0.md`
