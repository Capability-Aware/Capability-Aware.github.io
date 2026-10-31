# multiagent-grabgarbage 操作接入协议

本协议供负责四足运控和机械臂操作的同学接入已有控制器。接口实现位于 `source/capabilitylab/capabilitylab/cooperative/interfaces.py`，只依赖 Python 标准库。它提供传感观测、控制请求和独立物理验收的边界，不实现行走、逆运动学、抓取策略或相机识别算法。

运行时已经接入独立的左右指接触传感器、实测垃圾状态与碰撞几何见证，以及外部操作模块的加载和限位接口。操作模块、跨视角身份识别与最终抓取规划仍待操作同学接入；默认程序不会自动行走或抓取。`begin_grasp`、`release` 和控制器阶段均不代表成功。传感器已接线与真实物理任务通过分开记录，后者以各次运行报告为准。

## 坐标、时间与相机

世界系为右手系，`+Z` 向上。机器人基座为 `+X` 前、`+Y` 左、`+Z` 上；相机 optical 为 `+X` 右、`+Y` 下、`+Z` 前。`Pose3(position, quaternion_wxyz)` 的位置单位为米，四元数为单位 `wxyz`，将局部坐标旋转到世界坐标。腿、臂关节目标为弧度，两个夹爪平移关节目标为米；线速度为米/秒，角速度为弧度/秒，接触力为牛顿。

`ControllerObservation.end_effector_pose_world` 读自实际 `gripper_base_link` 刚体，与机器人基座位姿分开提供。它不是已经标定的工具中心点 TCP。若操作模块内部以 TCP 规划，须使用自己的工具标定转换到本接口的末端刚体坐标约定，不能把两者默认为同一坐标系。

USD 相机通常采用 `+Y` 上、`-Z` 前的约定，不能把它的世界四元数直接当作 optical 四元数。相机适配器应先完成约定转换，再构造 `CameraFrame`。

所有时间使用同一个 episode 的仿真秒，不混入墙钟或 Unix 时间。重置 episode 时，应重新创建物理见证 provider、清理图像队列和控制器状态。

| 类型 | 必要信息与语义 |
| --- | --- |
| `CameraIntrinsics` | `width,height,fx,fy,cx,cy`，像素单位的针孔内参。 |
| `CameraFrame` | `camera_id`、`role`（`front/rear/wrist/aerial`）、`frame_id`、`captured_at_s`、`received_at_s`、`optical_pose_world`、`extrinsics_sha256`、`intrinsics`；可选 `rgb` 和米制 `depth_m` 数组。 |
| `TargetBelief` | 目标 ID、观测类别、最后估计世界位置、实际观测时间、源相机与源帧、相机角色、外参 hash、位置不确定半径、置信度和 `needs_reobserve`；阶段固定为 `candidate`。 |
| `ControllerObservation` | 机器人 ID、当前仿真时间、命名关节位置/速度、多相机帧、可选候选 belief、本地 `ground_target`、操作方 `grasp_plan`、任务状态和自身基座/末端位姿。 |

`captured_at_s` 是图像实际曝光/采样时刻，`received_at_s` 是消息交给策略的时刻。`latency_s` 是两者之差。`is_fresh(now,max_age)` 按采样时间判断时效，不能通过重新包装旧帧或使用到达时间刷新观测。可以保留旧图作记忆，但应保留原时间和帧号。

`extrinsics_sha256` 标识固定父连杆到 optical 的标定，而非随机器人运动变化的世界位姿。`extrinsics_sha256(parent_frame,translation_parent_m,quaternion_parent_wxyz)` 提供稳定计算函数。相机资产若另有包含内参/来源的完整标定 hash，可同时记录；应说明各 hash 的覆盖范围。没有图像流时不要填入虚构 RGB 帧。`oracle_visibility` 观测须明确标记为可见性基线，不能描述成 RGB 识别。

四路仿真相机必须通过 `enable_cameras=True`／入口 `--enable_cameras` 启用。当前 spec 为 UAV 下视、四足前视和后视各 10 Hz，腕视 20 Hz。`IsaacCameraRig.capture_due` 按每路 spec 与仿真时钟调度，只有至少一路到期才渲染并读取到期相机；错过的期限不补造帧。最新帧字典分别保留每一路最后一次曝光，有限历史保留原帧号和采样时间。相机采集是渲染读回，尚不等于已完成垃圾识别。

读回的实际内参矩阵与 nominal spec 按 `rel_tol=1e-6, abs_tol=1e-4` 校验，超过容差即拒绝输出。通过校验后，`CameraFrame.intrinsics` 使用实测值；元数据同时记录 nominal/实测矩阵、`intrinsics_source=sensor_readback` 和 `frame_intrinsics_sha256`。不能用 nominal 内参掩盖实际渲染相机的偏差。前、后及腕相机的硬件标定状态仍按各 spec 的证据标记，不由仿真采集自动升级。

`ControllerObservation.wrist_confirmed(max_age_s=2)` 检查独立 `ground_target` 是否来自新鲜腕相机帧，并核对相机、帧号、曝光时间和外参 hash。没有地面定位时，带腕相机来源的候选 belief 也不能通过。该方法不要求抓取计划；`grasp_ready()` 仍独立要求有效计划。无人机候选过期不会否定新鲜地面复观。这个检查只证明观测链满足协议，不证明物体已抓住。任务核心仍独立检查最近的 `Detection`；腕图确认后，应由感知适配器发布实际检测事件，而非由控制器自报“确认成功”。

## 无人机坐标建议到局部抓取坐标

三个阶段必须分开记录。无人机坐标帮助地面搜索和选择图像 ROI；四足前、后或腕相机需要独立重新观察同一目标并输出局部坐标。不能把无人机粗世界坐标直接包装成机械臂末端 pose。

| 阶段 | 接口及信息边界 |
| --- | --- |
| `candidate` | `TargetBelief` 保存搜索建议。`proposal_id` 由任务目标、源相机和帧号确定；保留采样时间、外参 hash、不确定性。即使源相机是地面相机，单独构造 belief 也不会自动升级为抓取定位。 |
| `identity_confirmed` | `TargetAssociation` 记录 `proposal_id` 与地面 `ground_track_id`、相机、帧号的显式对应、置信度及方法。它记录身份关联结论，类本身不实现跨视角识别。 |
| `grasp_localized` | `GroundGraspTarget` 必须来自 `front/rear/wrist` 的独立局部测量，带表面估计世界坐标、位置不确定半径、地面帧/时间/外参 hash、跟踪 ID 及关联记录 ID。该坐标没有自动成为物体完整中心或末端姿态。 |

三类记录均可调用 `to_dict()`，序列化结果显式包含 `stage`。身份关联记录只引用实际源帧，其时间和外参在该帧及本地定位结果中保留；不能给新关联随意贴上当前时间。

[`localization.py`](../../../source/capabilitylab/capabilitylab/cooperative/localization.py) 的职责是从同帧目标 mask、有效米制深度及曝光时相机位姿形成 `LocalSurfaceEstimate`，再在显式身份关联通过后形成 `GroundGraspTarget`。可见表面点、协方差与局部几何供操作方的抓取规划器使用。无人机建议只参与粗 ROI/关联一致性检查，不充当地面深度，也不与地面测量混合后冒充独立复观。地面观察与无人机建议不一致时应拒绝升级并重观，不能强制吸附到原无人机坐标。

每个 `GroundGraspTarget.orientation_status` 固定为 `requires_grasp_planner`。操作方实现 `GraspPlanner.plan(target,observation)->PlannedGrasp|None`，结合局部几何、同帧观测和机械臂约束，生成最终的 `end_effector_pose_world`、夹爪开口宽度、规划器 ID 和有效时段。`PlannedGrasp` 构造器拒绝把 `TargetBelief` 作为输入；规划失败可返回 `None`，继续观测或换位。

`ControllerObservation.grasp_ready()` 要求地面定位、规划和实际源帧一致，检查相机角色、帧号、采样时间、外参 hash、位置不确定性和计划有效期。默认观测时效为 2 秒，不确定半径上限为 0.08 米，这些是可配置的接入门限，不是已经验证的抓取精度。新地面帧或定位改变后，旧计划不能自动沿用。无人机旧建议的时效可以衰减；只要身份关系仍明确，新的独立地面测量无需依赖无人机始终能看到目标。

登记入口只供可信感知流水线调用：`session.accept_aerial_proposal(proposal)` 对齐实际 UAV RGB-D 曝光；`session.accept_ground_localization(target)` 对齐实际地面曝光并清理旧抓取计划；`session.accept_grasp_plan(plan)` 绑定当前局部目标。策略的动作字典没有直接提交这些证据或成功标志的字段。任务用 `Detection.observed_at_s` 保留实际曝光时间，旧帧晚到不能把目标记忆刷新为“刚看见”。

2026-10-29 新增 `sensor_mode='real_rgbd'`（入口 `--sensor-mode real_rgbd --enable_cameras`）。此模式关闭 oracle 探测，初始公开任务表为空；目标 ID 来自视觉记忆的 `visual_*`，不得填场景真实实例 ID。`SharedBeliefMemory` 保存逐来源曝光与身份事件，通过 `snapshots(now)` 发布共享记忆；无人机坐标不会覆盖地面局部坐标。完整框架见 [FRAMEWORK_20261029.md](FRAMEWORK_20261029.md)。

出现空 mask、跟踪失效、触边或定位拒绝时，可信流水线必须立即调用 `session.reject_ground_observation(GroundObservationRejection(...))`。必要字段为公共 `waste_id`、`source_camera_id/source_frame_id/observed_at_s/extrinsics_sha256/source_camera_role`、`ground_track_id` 及原因。时间必须直接复制实际曝光时间，与记录精确相等。不能只捕获定位异常后继续保留旧坐标。

该入口保存每条来源的负水位，并清除该来源当前目标与旧计划；同曝光负结果优先，迟到旧正结果不能恢复许可。更新的有效定位可重新登记，但仍需要新的 `PlannedGrasp`。其他独立有效来源不因这条失视被清空。新计划必须在接收时仍有效，且引用当前局部目标。两条 `begin_grasp` 路径均使用当前 session 状态，因此提前构造的旧动作也不能越过撤销。

操作方还需实现已执行动作的停止/恢复：清空观测和计划只阻断未来抓取许可，不会自动停止已经运动的机械臂。原始关节接口仍用于操作控制器执行，不能把“没有 plan”自行解释为已物理刹停。腕部观察姿态必须提供可达性结果；未初始化的后/腕相机不能自动当作可用观察者。

`Detection.source_camera_id` 将同一机器人的前、后和腕相机分开维护可见性。每个观察者/相机/目标拒绝重复帧与不递增的曝光时间；未来时间被拒绝。独立相机的迟到帧可保留历史证据，但不能覆盖更新的共享位置或刷新最后观测时间。一台相机失视不会抹掉另一台仍有效的观测。`observed_at_s=None` 只为旧 CPU fixture 兼容，此时使用事件到达仿真时间；实际感知入口始终填写真实曝光时间。

以下只展示已存在感知、身份关联与操作模块之间的数据交接，没有定义替代控制器或伪识别器。`proposal`、`track_mask`、`identity_association` 和 `grasp_planner` 必须由实际模块提供：

```python
from capabilitylab.cooperative.localization import localize_mask, confirm_ground_target

session.accept_aerial_proposal(proposal)
frame = session.camera_rig.frame_by_id(track_mask.camera_id, track_mask.frame_id)
surface = localize_mask(
    track_mask, frame, session.camera_rig.specs[frame.camera_id], session.time,
)
target = confirm_ground_target(proposal, surface, identity_association, session.time)
session.accept_ground_localization(target)
plan = grasp_planner.plan(target, session.controller_observation())
if plan is not None:
    session.accept_grasp_plan(plan)
```

`controller_observation()` 只为当前已独占认领的目标提供经过曝光校验的 UAV proposal，以及该目标的任务 phase。只有 oracle 可见性记录、没有合法实际 RGB-D proposal 时，typed `target` 保持 `None`。物体自身物理真值只进入 session 的验收分支，不填充 proposal 或局部抓取坐标。

## 控制器阶段与输出

`ManipulationPhase` 表示控制器当前意图，不能作为任务验收结果。

| 阶段 | 接入动作及后续验收 |
| --- | --- |
| `IDLE` | 等待可用的共享目标。 |
| `APPROACH` | 认领目标、按最后观测位置接近；过期记忆可用于搜索接近。 |
| `WRIST_CONFIRM` | 通过腕相机重新观察；失视不能当作收集完成。 |
| `GRASP` | 发出 `begin_grasp` 请求并驱动已有操作控制器；等待双指实际接触和持续提升。 |
| `TRANSPORT` | 仅在任务核心确认抓取后运输；掉落需要恢复及重新定位。 |
| `DEPOSIT` | 移到正确分类桶，发出 `release` 请求并实际打开夹爪。 |
| `WAIT_PHYSICS` | 等待完整物体进入桶内、线/角速度均低且持续停留的物理判定。 |
| `RECOVER` | 失目标、掉落、断联或操作失败后的恢复；携物取消需等实际脱离才能重新分配。 |

`ControllerOutput` 包含 `issued_at_s`、`valid_until_s`、命名的 `joint_targets`、`mission_commands`、阶段和可选 `drone_target_world`。转换方法如下：

```python
actions = output.as_actions(
    now_s=observation.sim_time_s,
    joint_limits=session.joint_limits(),
    max_latency_s=0.1,
    observation=observation,  # begin_grasp 必须核对独立地面定位与操作方规划
)
session.step(actions)
```

转换会拒绝未来、过期、延迟超预算、未知关节及越界目标。结果与 `session.step` 的 `joint_targets`、`mission`、`drone_target` 字典一致。没有改写机器人 root pose、垃圾 pose、附着垃圾或直接设置成功的动作字段。无人机目标仍须经过会话的飞行范围及碰撞检查。

若输出含 `begin_grasp`，`as_actions` 强制要求当前 `observation.grasp_ready()`，且请求目标必须与局部定位目标一致。运行时的原始字典兼容入口也执行相同门控，不能仅凭无人机最新一次检测就触发操作。任务状态机的物理验收负责判断抓住/投放，它不替代感知链与规划链。

`MissionCommand` 只接受 `claim/approach/begin_grasp/cancel/release`；只有 `release` 带 `bin_id`。运行时通过独立 `b2rm_graspable.usda` 加载完整原手指网格与两个独立执行器；原冻结资产没有被覆盖。两指控制名为 `gripper_finger1_joint` 和 `gripper_finger2_joint`，均为正向增大时闭合，当前导出的硬限位为 `[0, 0.03649999776482582]` 米。`gripper_targets(aperture_m)` 只做源几何开口到关节位置的映射，并拒绝外推；75 mm 开口、2 mm 最小开口来自源网格包络，不是已验证的 PhysX cooked 夹持净空。

`session.joint_limits()` 将两指导出硬限位与原腿/臂软限位组合。不能对两指继续套用腿/臂的 `0.9` 软限位缩放，否则会丢失合法的全开或闭合行程；也不能为了夹爪放宽腿/臂软限位。raw 与 typed 关节输出使用同一组限位。机器人默认仍保持站姿和开爪，实际接近、抓取与投放动作由外部模块负责。

## 显式加载外部控制器

`ManipulationController` 协议包含 `reset(config,robot_id)` 与 `act(observation)->ControllerOutput`。加载入口为 `load_controller("module:factory",controller_config,robot_id)`：无参工厂创建对象，然后调用 `reset`。

当前入口 `--manipulation-controller module:factory` 传入的 `reset` 配置只有 `task_id` 和 `joint_limits`。命名关节列表可读 `config["joint_limits"].keys()`，不要假设存在 `controlled_joint_names`、垃圾初始坐标或整份任务配置。factory 无参数；`reset` 的两个位置参数依次为这份配置和机器人 ID；`act` 的唯一参数为 `ControllerObservation`。返回值必须是 `ControllerOutput`。

已有模块加载和调用方式如下；`controller_spec` 是操作同学提供的可信 `module:factory` 字符串，示例不创建占位操作策略：

```python
from capabilitylab.cooperative.interfaces import load_controller

controller = load_controller(
    controller_spec,
    {"task_id": session.task_id, "joint_limits": session.joint_limits()},
    session.robot_id,
)
observation = session.controller_observation()
output = controller.act(observation)
session.step(output)
```

只从操作者明确指定的可信本地 Python 模块加载。`controller_config` 只传控制器设置、机器人/相机标定及已知公共设施信息，不传整个 `task.json`；加载器会拒绝带顶层 `waste` 的配置，防止直接把初始垃圾真值交给策略。该简单防护不是任意 Python 插件的安全沙箱，调用方仍须保持观测边界。

## 仿真侧物理见证

运行时已经在 `sim.reset()` 之前创建 `IsaacWitnessAdapter`，左右指各一个 `ContactSensor`，显式按垃圾 root 列表过滤。每次实际物理 step 后，先更新机器人和垃圾状态，再更新两指传感器，最后由 session 持有的 `SimulatorWitnessProvider` 读回。矩阵为 `force_matrix_w[env,finger,object,xyz]`；实际列通过 PhysX `filter_paths` 对回垃圾实例，不假设返回顺序，也不回退到整机总接触力。

控制器不持有 `reader` 或 provider。`reader(waste_id,robot_id,now_s)` 返回同一物理帧的 `SimulatorSample`：

- 垃圾、机器人 ID、单调 `sim_frame_id`、`captured_at_s`。
- 实测垃圾 root 位姿、世界线速度、世界角速度、世界 AABB 的真实中心与全尺寸。
- 左指、右指分别与这个垃圾接触的实测力，以及实测末端位姿。

左右指接触必须按垃圾实例/刚体过滤。不能使用脚与地形的接触、整机总接触力、夹爪关节目标、物体离末端的距离或“闭合完成”状态替代。

```python
# 以下由 session 负责，操作控制器不应重复调用或自行构造证据：
session.witness_adapter.update(session.dt)
witnesses = [session.witness_provider.sample(actual_id, session.robot_id, session.time)
             for actual_id in session.waste]
if session.sensor_mode == 'real_rgbd':
    session.mission.observe_physical_frame(witnesses, session.time)
else:
    for witness in witnesses:
        session.mission.observe_witness(witness, session.time)
```

真实视觉模式必须提交完整物理目录的同一帧批次，缺失、重复对象、错误范围或倒序批次均拒绝；不能用旧的逐物体入口。实际物体与公共视觉目标的对应只在正在抓取的 owner 对唯一物体产生双指接触后，由验收侧私下建立。完整目录仍是清理率分母，实际对象去重；私有对应关系仅进入实验报告，不进入策略观测，也不作为视觉身份算法的正确性结论。

provider 拒绝错误对象/机器人、非同步时间以及重复或倒序物理帧，避免把迟到的历史接触重标为现在。默认 `0.01 N` 是接口阈值，不代表已经完成了该机器人接触传感器的噪声标定。

`PhysicalWitness.gripper_contact` 表示任一手指仍与该垃圾接触；`bilateral_contact` 表示左右两指均达到阈值。抓取确认需要后者并持续提升。释放验收需要前者为假，因此单指仍碰着物体时不能误算“已释放”。角速度也参与桶内低速停留判断，避免原地高速旋转的物体被计为静置。外部接入应同时填写这两个接触字段和实际角速度，不能沿用一个“夹爪已闭合”的布尔量。

provider 保留的 `last_sample` 可供仿真审计，不能作为目标 belief 的隐藏位置来源。控制器可读取自身末端位姿，但不可读取未发现垃圾的物理见证。

世界 AABB 由实际 Cylinder/Mesh/Cube 碰撞几何、缓存的 collider-to-root 固定变换和当步 PhysX root pose 计算，不使用可能过期的 USD 世界 pose。旋转后的 AABB 中心可以不同于 root/质心，验收使用实测 AABB 中心及 `max-min` 尺寸，提升仍使用 root 高度。原 root 对称包围尺寸只留审计，不能因它几毫米的保守延伸把已落稳物体永久判为桶外。桶边界的 `0.0001 m` 容差用于浮点数值误差，不用于允许肉眼可见穿透。

`--without-ground-robot` 模式仍读取真实垃圾状态和碰撞 AABB，但场景没有夹爪，接触为无、末端位姿为 `None`。该模式可用于无人机和物体独立检查，不能得到双指抓取成功结论。

## 连续证据日志

独立入口默认在该次输出目录持续写入以下旁路日志，真实垃圾状态不加入 policy observation：

| 文件 | 内容及边界 |
| --- | --- |
| `physics_witness.jsonl` | 每个实际物理 step 一行，记录 frame/time/dt、全部对象的实测 pose、线/角速度、AABB 中心/尺寸、左右指分别接触力、实际末端 pose、接触阈值和交给任务的判据输入。终止帧仍采全部对象；采样中途失败显式标记不完整，不补造样本。 |
| `visual_events.jsonl` | 仅在 UAV proposal、地面定位及 Plan 接受时记录，保留真实曝光和接收时间、源相机/帧号、外参 hash、曝光时位姿/内参、定位与规划内容，不写 RGB/深度大数组。 |
| `events.jsonl` | 增量写入任务事件并刷新；异常退出也尽力保存已发生的事件。 |
| `evidence_summary.json` | 标明已写帧数、完整帧数、帧号/时间连续性和最后物理帧。`runner_finished` 与 `collection_mission_success` 分开；后者要求任务实际 `terminated`、未 `truncated` 且 outcome 为 `success`，不能由程序 exit 0 推断。 |

每次 `step` 返回后立即写入并刷新，不按任意间隔抽样。异常发生在物理前进与采样之间时，该帧记为不完整；帧号或时间跳跃也会显式标记。`evidence_record()` 仅供可信 session/runner 审计使用，不提供给操作策略。这里只保留图像帧引用，尚不能从日志重算 NN mask、跨视角身份识别或复现感知结果；后续实际感知流水线还须保存其输入图像、mask 与模型来源。

入口保留 fatal handler，`--stack-dump-interval` 默认 `0`，不发送周期栈转储信号；只有显式传入正秒数才启用周期诊断。既有长运行曾在周期转储开始后异常退出，关闭后另一次物理验证通过；记录器影响仍待确认，不据此宣称已定位根因。

## 复用 5080 的 TrackingSAM：已经有什么，还缺什么

本支线包含 cherry-pick 的感知复现提交 `6ff36220`（`feat(perception): add pinned TrackingSAM reproduction and verified demos`）。来源与环境范围见 [`REPRODUCTION_20261029.md`](../tracking_sam/REPRODUCTION_20261029.md)、[`verification_20261029.json`](../tracking_sam/verification_20261029.json) 及模块 [`README.md`](../../../source/capabilitylab/capabilitylab/perception/tracking_sam/README.md)。固定版本清单保存在 [`sources.json`](../../../source/capabilitylab/capabilitylab/perception/tracking_sam/sources.json)：上游为 [`RogerQi/Tracking_SAM` 的 `d5e5e81a361dce4ddbe3264a2b8027b2b43ea3fd`](https://github.com/RogerQi/Tracking_SAM/tree/d5e5e81a361dce4ddbe3264a2b8027b2b43ea3fd)。

已审阅本地 [`run.py`](../../../source/capabilitylab/capabilitylab/perception/tracking_sam/run.py)：它读取按文件名排序的离线等尺寸图像序列，用人工框、前景点或初始 mask 提示一个目标，SAM ViT-B 只负责首帧分割，后续由原版 AOT-T 传播。输出为每帧二值 mask、叠加视频、耗时及来源/权重 hash，不输出垃圾三维位置或机器人动作。

5080 原环境已记录三种入口各 82 帧的工程运行。那些记录不意味着当前 5090/worktree 已有模型环境，也不证明多目标关联、跨相机身份交接、真实垃圾检测、深度定位或机器人闭环已完成。原记录的约 11.7 毫秒/帧只计 AOT 传播，排除了加载、图像传输、编码及控制，不是协同系统端到端延迟。上游语言检测链和默认 ViT-H 也没有在该记录中被验证。

接入顺序应为：同一相机流内建立单目标 mask 及原始帧时间/ID → 明确输出目标失跟/无效状态 → 用对应深度及标定做局部定位 → 独立完成无人机候选与地面 track 的身份关联 → 交给操作方规划。多目标队列、跨视角身份、遮挡恢复与在线调度需要额外实现和实际验证，不能仅将单目标 tracker 初始化多次便宣称已形成多目标闭环。该支线的 CPU 合同与来源审阅未安装模型、未启动 GPU。

## 验证与当前边界

2026-10-29 本轮全套协同 CPU 合同测试为 `188 passed in 3.85s`。覆盖运行时替身、实际 USD 几何/材质合同与来源检查；不将替身像素或接触矩阵当作真实渲染/PhysX 通过。重跑时应使用有 SDK CPU USD、numpy 和 Pillow 的测试环境，例如本机 Python 3.11 加已安装 SDK 的 CPU 库路径：

```bash
env PYTHONPATH="source/capabilitylab:/media/user/DATA/apps/isaac-sim-5.1.0/extscache/omni.kit.pip_archive-0.0.0+69cbf6ad.lx64.cp311/pip_prebundle:/media/user/DATA/apps/isaac-sim-5.1.0/extscache/omni.usd.libs-1.0.1+69cbf6ad.lx64.r.cp311" \
  LD_LIBRARY_PATH="/media/user/DATA/envs/conda/isaacsim/lib:/media/user/DATA/apps/isaac-sim-5.1.0/extscache/omni.usd.libs-1.0.1+69cbf6ad.lx64.r.cp311/bin:/media/user/DATA/apps/isaac-sim-5.1.0/extscache/omni.usd.libs-1.0.1+69cbf6ad.lx64.r.cp311/bin/deps:/media/user/DATA/apps/isaac-sim-5.1.0/kit" \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /media/user/DATA/envs/conda/isaacsim/bin/python -m pytest -q \
  tests/cooperative
```

这些测试覆盖过期图像、腕相机确认链、三阶段坐标交接、无人机候选不能直接成为抓取姿态、局部定位与计划的一致性、动作时效与限位、控制器加载、仿真见证对象关联/重放拒绝、单双指接触，以及任务的物理验收反例。新增的运行时替身测试验证：无人机失视超过 2 秒后，地面新曝光仍可重新确认并开始抓取；晚到旧帧、未来帧、错 hash、缺少实际 RGB-D 及重复曝光不能刷新目标；没有真实 UAV proposal 的 oracle 检测不生成 typed proposal。合成见证和接口测试只说明合同按预期执行；真实相机数据、实际双指接触读回、四足行走、机械臂拾取与完整投放仍须分别保留实际物理运行结果。
