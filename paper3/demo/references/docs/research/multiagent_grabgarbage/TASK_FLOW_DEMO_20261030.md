# multiagent-grabgarbage：任务流、第三人称与机载录像

日期：2026-10-30（Asia/Shanghai）。独立分支 `feat/grab-garbage`。

最新更新：默认已切换为 `active_handoff_v2_20261030`，25.1 秒成片对应 5001 个连续物理步、25.005 秒。实际执行预测停车、三帧前视复查续行、重新选择转身及腕部观察，并在 24.0 秒通过自动腕部三帧结构复查。初始空地提示仍人工配对，自动身份未标定，未抓取，清理 0/24。详见 [主动观察闭环接线与验证](ACTIVE_HANDOFF_INTEGRATION_20261030.md)；下文原 10 秒录像与此前尾腕展开的记录均按原实验保留。

## 展示入口

[项目原版页面](../../evidence/multiagent_grabgarbage_task_flow_20261030/index.html)展示完整七阶段设计、当前接通范围与实际录像。用户明确指定桌面新目录，展示副本位于 `/home/user/Desktop/multi agent demo/index.html`；HTML、视频、封面和页面引用资源一起导出。该指定授权覆盖本次桌面展示导出，不改变旧冻结 `bc demo` 的边界。

最初只有机载画面，难以看清团队和环境的位置关系。根据用户反馈，本轮新增两路真实外部相机，重新进行物理仿真和同步录制；默认显示近侧第三人称，可切换全景、四个独立机载视角和六路同步画面。没有从旧轨迹重建世界来冒充新录像。

## 本轮改动

- `observer_camera.py`：静态世界第三人称 RGB，相机在 reset 前创建；每个物理步更新，在任务相机渲染之后读取同次画面。独立保存实际帧号、仿真时间、物理 tick、位姿/内参读回、PNG SHA 和连续 manifest 链。不进入策略、原四路传感输入或计分。
- `isaac_session.py`：可选 `enable_observer_cameras`、`observer_camera_views`、`observer_output`；默认关闭，沿用已验证的 CPU PhysX/Fabric 同步路径。
- `check_live_blindspot.py`：可选 `--observer-cameras --observer-views JSON`，同时记录四路机载和两路第三人称；原算法、手动提示、原运控权重与成功标准保留。
- `build_multiview_task_demo.py`：校验同一次 run、同一个物理 tick、共享实际渲染及源文件 SHA 后生成八段录像。`build_task_flow_video.py`生成上一轮的前视对照与四视角片段。
- `export_task_flow_demo.py`：导出可离线播放的展示包；`--update-owned` 仅更新上次导出清单中且当前 SHA 仍匹配的文件，保留用户修改及其他文件。
- HTML：七阶段交互说明、两层视角按钮、关键时刻定位、真实结果与缺口。第三人称与第一视角可独立全屏，不要求在小分屏中辨认细节。

## 新录制的实际结果

先运行 3 s 构图预览 `observer_preview_guard_v1_20261030`，检查无人机、四足/折叠臂、地面罐子、附近三个桶均可见，再录制正式 10 s：

`outputs/multiagent-grabgarbage/live_multiview_guard_v1_20261030/`

正式运行无 `failure.json`，2000 个连续物理帧、504 次机载曝光及 504 次位姿核验。两路第三人称各 101 次，共 202 次曝光，均与同次任务相机渲染、实际物理 tick 对齐；两套录制均正常关闭。独立审计复核 1210 个图像/深度文件 SHA、两套 manifest 链和执行源快照，归档于 [new_run](../../evidence/multiagent_grabgarbage_task_flow_20261030/new_run/README.md)。

真实前视定位接受 89 次、拒绝 2 次，空中定位接受 91 次；2.6 s 边缘保护停车，3.0 s 用新曝光确认并保持。实际世界 X 前移 0.1058388 m；95 ms 负向命令期间仍向前约 8.16 mm，严格实际后退验收失败。证据、感知及安全分项通过，不把这些分项合成完整任务成功。完整拾取投放仍为 **0/24**。

正式运行墙钟约 166.87 s，神经网络推理时物理暂停。10 s 视频不是实时推理性能证明。新增外部相机仅观察实际状态，没有给策略提供全局目标真值，也没有改写机器人或物体运动来补全动作。

## 视频与来源

新录八段：

| 文件 | 用途 |
| --- | --- |
| `team_side_only.mp4` | 默认近侧第三人称，四足、折叠臂、无人机、罐子及附近桶同框 |
| `team_overview_only.mp4` | 第三人称场景全景 |
| `first_uav.mp4` | 无人机下视第一视角 |
| `first_front.mp4` | 狗前相机第一视角 |
| `first_rear.mp4` | 狗后相机第一视角；本轮未初始化目标跟踪 |
| `first_wrist.mp4` | 腕部第一视角；当前收拢姿态未接管目标 |
| `team_side.mp4` | 近侧为主的六路同步画面 |
| `team_overview.mp4` | 全景为主的六路同步画面 |

以上在同一 evidence 目录，均有同名封面和逐帧来源清单，汇总为 [multiview_manifest.json](../../evidence/multiagent_grabgarbage_task_flow_20261030/multiview_manifest.json)。单路视频保留完整原画幅及原尺寸，标题放在新增的 48 px 画布；成片 H264 CRF21 为有损展示副本，原 PNG 保留。第三人称单片为 1920×1128，同步片为 1920×1440。

每片按 10 Hz 展示 101 个实际曝光组，长 10.1 s：首曝 0.005 s，其后 0.1 s 至 10.0 s。腕部原始 20 Hz，选用对应曝光下采样；不补造曝光、插值运动或复用上一实验画面。媒体播放时间与实际曝光时间均在来源清单中保留。

历史两段 `front_fixed_vs_guard.mp4`、`guard_four_cameras.mp4` 继续来自 2026-10-29 的 `live_blindspot_guard_v3_20261029` 和 `live_blindspot_fixed_v3_20261029`，由旧 `manifest.json` 管理。HTML 已明确标记历史对照，不把新录外部机位拼到历史第一视角上。

所有录像中的首框、类别和空地同物对应关系仍来自人工提示。独立夹爪夹持、受控落桶等分项没有被拼接成自主抓取投放的成功过程。当前任务状态仍为接近阶段；停车等待操作不等于已经到达可抓距离。

## 验证与复现

外部相机接入后、后续腕部动作研发前，完整 `tests/cooperative` 在既有 SDK USD/Torch 隔离环境下 **478 passed in 17.50 s**，无跳过。新测试覆盖光学朝向、内参、只读来源、实际曝光排程、时间及哈希链；真实画面另通过上述 3 s 和 10 s 运行验收。测试成功不替代机器人任务成功。

Chrome 实际浏览检查覆盖七阶段切换、九个视频选项的元信息与 4.7 s 跳转、地图/对照图加载、1440 px 及 390 px 窗口无横向溢出；项目版和桌面副本分别检查。媒体另外通过 ffprobe 帧数、帧率、时长检查并解码目视核对。浏览器记录与原始日志保存在 `outputs/multiagent-grabgarbage/task_flow_*_review_20261030/`。

```bash
task_root=/home/user/isaac/capability_research/.worktrees/grab_garbage
/home/user/isaac/run-capability.sh "$task_root/scripts/cooperative/check_live_blindspot.py" \
  --output "$task_root/outputs/multiagent-grabgarbage/new_multiview_run" \
  --baseline observation_guard --seconds 10 --observer-cameras \
  --observer-views "$task_root/docs/evidence/multiagent_grabgarbage_task_flow_20261030/new_run/observer_views.json" \
  --headless
python3 "$task_root/scripts/cooperative/export_task_flow_demo.py" \
  --output '/home/user/Desktop/multi agent demo' --update-owned
```

录制输出必须是新目录。现有独立验收器的严格后退失败会返回退出码 2，需保留分项结果，不能降低阈值或将失败隐藏。完整目标继续：腕部真实观察动作与接管、自主候选/身份关联、操作模块、单目标运输投放及多目标论文评测；展示任务与这些研发并行推进。
