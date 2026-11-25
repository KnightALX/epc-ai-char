# SCALE_EVAL — 大规模生成评测记录（Milestone 4）

> 目的：回答「B.db 生成在 10×/20× 规模下能否跑通、内存与耗时多少」。
> 诚实声明：合成数据（最近几何参考 + 平滑趋势 + 确定性抖动），只测规模吞吐，
> 不做精度声明。精度结论以 P0/P1/ab_hard/transfer 夹具与模型印章为准。

## 环境

| 项 | 值 |
| --- | --- |
| OS / Python | Windows / Python 3.13.8 |
| scikit-learn 运行时 | 1.6.1（模型以 1.9.1 训练 → InconsistentVersionWarning，数值不受影响） |
| 源夹具 | A_ref.db 40000 行（20 inst × 40 pvt × 50 key） |
| 引擎 | residual_gbdt（fallback_used=false），prior=idw_nn |

## 规模定义

| 规模 | 源实例数 | 源行数 | 源库体积 | B 输出行数 | 输出体积 |
| --- | --- | --- | --- | --- | --- |
| 10× | 200 | 400,000 | ~100.5 MB | 27,500 (50×11×50) | ~8.3 MB |
| 20× | 400 | 800,000 | ~201 MB | 27,500 | ~8.3 MB |

## 实测结果（run_with_rss.py，psutil 轮询 50ms）

| 规模 | EXIT | G2 | wall time | RSS_PEAK |
| --- | --- | --- | --- | --- |
| 10× | 0 | PASS rel=1.110e-16 | 12.70 s | 419.3 MB |
| 20× | 0 | PASS rel=1.110e-16 | 13.97 s | 614.5 MB |

日志：`%TEMP%\epc_scale_10x.log`（首次失败 + 复跑成功）、20× 日志同目录。

## 首次 10× 失败（引擎行为正确，保留为 fail-closed 证据）

- 现象：`G2 FAIL: row missing in B.db` → exit 1，B.db 被删除，无半成品残留。
- 根因：约束 relative_delta_vs_source 定位实例 `HINP3TCAM64X8SWISDC` 不在 B 目标清单
  （首版 B_TARGETS 缺 64X8），构造结果不含该行，G2 正确 fail-closed。
- 修复：B_TARGETS 扩到 50 名（含 512X100 与 64X8 满足两条约束定位）。
- 结论：约束定位实例必须在 B 清单内——这是 YAML 作者纪律，已写入测试断言。

## 内存外推（线性趋势，供容量规划）

- 源库全量载入内存是当前主要放大源（source.py 全库 → dict），10× 时引擎进程峰值
  419 MB ≈ 源库体积 4.2×。20× 时 614.5 MB（源库 201 MB ≈ 3.1×，dict 去重后行数
  相同 key 共享 value 串引用）。
- 200 万行规模（≈50×）外推：源库 ~500 MB、进程峰值 ~1.5-3 GB。若需控制内存，
  下一步是 source.py 的流式/列式加载（见总验收报告的 roadmap）。

## 复现命令

```
cd <repo>
python epc_fixtures/scale/build_scale_fixture.py --instances 200 --out epc_fixtures/scale/A_scale.db --b-list epc_fixtures/scale/B_scale_instance_list.txt
python epc_fixtures/scale/run_with_rss.py epc_fixtures/scale/epc_job.scale_10x.yaml
python -m pytest tests/test_scale.py -q            # pytest 化的同一评测（slow 标记）
```

## 版本钉死说明（gate ③ 证据）

- 根级 `requirements.txt` 已钉：joblib 1.5.3 / numpy 2.2.3 / pandas 2.2.3 /
  PyYAML 6.0.3 / scikit-learn 1.6.1 / pytest 9.0.2 / psutil 7.2.0。
- 模型训练环境：scikit-learn 1.9.1（印章 generated 2026-10-22T14:32:34+08:00）。
  字节级重训复现需 1.9.1 环境；运行时 1.6.1 已通过全量 59 绿 + 本次 scale 评测，
  仅产生非阻塞 InconsistentVersionWarning。
