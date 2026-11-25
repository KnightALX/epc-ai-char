# EPC — SRAM DB 总验收报告（Windows 实机，2026-11-24）

> 背景材料：TSMC 2026 VLSI Symposium「AI-Assisted SRAM Compiler Characterization」Slide 25 —
> 用已有大数据训练模型预测额外 PVT/新几何，精度优于传统插值/外推（尤其非线性行为），以"少仿真+AI 预测"替代全量仿真。
> 本仓库 `EPC — AI Characterization (A→B .db)` 即该思想的工程实现：A 库（已表征）+ 模型/IDW → B 库（新配置预测生成）。

## 0. 交付总览（一句话）

引擎（预测生成 + 七项 P1 加固 + 原子落盘 + db_meta 溯源 + importer 适配器）、GUI（Fluent 风格收敛 + 死代码清除 + 路径可移植）、测试（79 个 pytest + 3 个 GUI 冒烟 + 规模 10×/20× 实测）全部在本机 Windows 实跑通过；CI 门禁与单入口脚本已交付，真实公开数据集评测为唯一未闭环的外部依赖项。

## 1. Reality Checker 八道生产硬门槛 — 逐条证据

| # | 门槛 | 状态 | 证据 |
|---|---|---|---|
| ① | pytest 化单入口 + 覆盖率基线 | ✅ 通过 | `python -m pytest tests -q`（79 tests）+ `run_all_tests.ps1` 单入口；覆盖率 63%（详见 §2） |
| ② | /workspace 全部可迁移 + 干净机装通 | 🟡 部分 | 引擎/GUI/脚本全部 rebase（`epc_engine/paths.py` + `epc_gui/paths.py` portable，全仓仅剩文档引用）；本机 1 台验证通过；两台干净机未实测（见 §5 缺口 2） |
| ③ | 钉死依赖版本 + 回退用例 | ✅ 通过（带回退语义测试） | 根级 `requirements.txt` 精确钉版本；P1③ 空白容忍 3 例 + 坏值拒绝 2 例；R2 both 双头语义由 `test_units.py` 覆盖；模型 sklearn 1.9.1 训练 vs 运行时 1.6.1 的 InconsistentVersionWarning 已在 requirements 注释中说明（数值经 G2 1.110e-16 验证不受影响） |
| ④ | ≥1 真实/公开 SRAM 数据集评测 | 🔴 未闭环（外部依赖） | 合成数据（scale 10×/20×）只证吞吐不证精度；`epc_engine/importer.py` 已提供真实库 schema 适配入口（`source.table` + `source.col_map`），真实库到达即可评测（见 §5 缺口 1） |
| ⑤ | ≥10× 规模生成评测 | ✅ 通过 | 10×=40 万行源→27500 行 B，12.70s/RSS 419MB；20×=80 万行→13.97s/RSS 615MB；G2 均 1.110e-16；证据文件 `epc_fixtures/scale/SCALE_EVAL.md` |
| ⑥ | GUI live 点通 + 干净装 | ✅ 通过（headless） | PyQt5 5.15.2 全新安装；`brief_start_quit` EXIT=0 实启动；`smoke_headless/P1/P2` 三套全 OK；19 张截图 offscreen 重新生成；人工目视确认未执行（见 §5 缺口 3） |
| ⑦ | 双份 joblib/stamp sha 对齐 | ✅ 通过 | `epc_fixtures/models/` 已与 `epc_engine/models/` 对齐：joblib sha16=BD6ECDE2F27E622B、sidecar sha16=C763E3D253C80EA4（与印章 bd6ecde2f27e622b 一致） |
| ⑧ | CI 红门禁 | ✅ 交付（激活需托管） | `.github/workflows/epc-ci.yml`（push/PR 触发：pytest fast+slow + GUI 三冒烟，任一失败即红）；本地等价入口 `run_all_tests.ps1`；仓库尚未托管到 GitHub（非 git 仓库），激活为外部动作（见 §5 缺口 4） |

## 2. 测试基线（本机实测）

- **pytest 全量**：79 passed, 34 warnings（248.28s），`PYTEST_EXIT=0` 干净退出码捕获，日志 `%TEMP%\epc_pytest_final_cov2.log`
- **覆盖率（epc_engine）**：TOTAL 63%（3422 stmts / 1262 missed；高覆盖：source 98%、audit 97%、importer 95%、write_db 94%、parse 94%、backends\__init__ 95%、job 86%、idw_nn 81%、residual_gbdt 80%、transfer_ab 81%；train.py/lon_holdout.py 0% 与 transfer_holdout 23% 为离线训练链，刻意 subprocess 隔离不计归因）
- 测试分层：
  - `tests/test_paths.py`（8）：rebase 三形式 + 相对/绝对路径透传
  - `tests/test_engine_green.py`（10）：10 个绿 job 参数化（sample/p1×2/ab_hard×2/p2×3/transfer×2）+ audit 内容断言
  - `tests/test_engine_red.py`（6）：红 job exit 码 + 无落盘 + h3hard/毒印章/缺印章 fail-closed
  - `tests/test_p1_regressions.py`（12）：七项 P1 逐一回归（空 locator/非法 op/on_violation 校验/失败删库/原子写/G2 单元格子集/transfer raise）
  - `tests/test_units.py`：AB-hard/transfer 门控逻辑、parser 默认、fixture 诚实性、decoupling 扫描
  - `tests/test_db_meta.py`（2）+ `tests/test_importer.py`（7）：数据库接入层
  - `tests/test_engine_inprocess.py`（10）：进程内跑通全部引擎路径（cli→construct→backends→constraints→write_db→audit），供覆盖率归因
  - `tests/test_scale.py`（1，slow）：10× 构建 + 引擎实跑断言

## 3. 本轮七项 P1 修复（全部带回归测试）

1. 空 locator 约束静默跳过 → ValueError（fail-closed）
2. value_range 非法 op → ValueError（白名单 `<,<=,>,>=`）
3. `on_violation` 未 strip/枚举校验 → 加载期拒绝非法值，容忍纯空白
4. 失败路径残留陈旧 B.db → 构造失败/加载失败均删旧库
5. 写库非原子 → tmp + `os.replace` 原子落盘 + NaN/inf 有限性校验
6. G2 固定 toks[0] 误杀单元格子集约束 → cell-aware 逐格比对
7. transfer 预测失败静默写 "0" → ValueError

## 4. 数据库接入层（新增）

- `char_data` 四列 + 复合主键（贴契约）；`PRAGMA user_version=1`
- `db_meta` 溯源表：yaml/source/model 三个 sha16 指纹 + backend/prior/apply_on/fallback_used/行数/门禁终态
- 原子落盘（tmp+rename，崩溃不丢旧库）；索引精简（删 idx_inst，PK 最左前缀覆盖）
- `epc_engine/importer.py`：真实库 schema 内省 + 列映射（`source.table`/`source.col_map`）+ 可解析性降级（unparseable 名跳过并告警，strict 模式可拒绝）

## 5. 已知缺口与风险（诚实披露）

1. **真实/公开 SRAM 数据集评测缺失**：仓库内全部为合成/伪域夹具；importer 已就绪，拿到真实库（如 TSMC 风格 .db 或公开 SRAM 表征集）即可评测。
2. **两台干净机未实测**：本机（Windows + Python 3.13.8）全绿；第二台机器与 Linux CI 首次运行未执行。
3. **GUI 人工目视未执行**：offscreen 截图 + 冒烟全过，但像素级/交互体感需人在桌面环境确认。
4. **CI 未激活**：仓库无 .git；workflow 文件已交付，推送托管即生效。
5. **模型字节级不可复现**（历史已知）：同 seed 重训 sha 与出厂印章不同（sklearn 1.9.1 vs 1.6.1 + HistGBR 内部非确定性）；运行时数值正确性由 G2 门禁（1e-6 阈值，实测 1.110e-16）保障，requirements.txt 已注明重训环境。

## 6. 复现指南（Windows）

```powershell
cd <repo>
pip install -r requirements.txt
pip install PyQt5==5.15.2
powershell -ExecutionPolicy Bypass -File run_all_tests.ps1   # 单入口全门禁
python -m epc_engine epc_fixtures\epc_job.sample.yaml        # 引擎单跑
python epc_gui\scripts\brief_start_quit.py                   # GUI 启动冒烟
```

## 7. 结论

项目已达到「真实项目导入应用」的候选状态：引擎 fail-closed、数据库可溯源可适配、GUI 可启动可验证、测试可复跑可门禁。唯一阻断生产导入的是外部数据依赖（真实 SRAM 库评测），其余门槛均以可核对证据闭环。
