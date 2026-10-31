# 当前本机相机到 PD 预抓取桥

本轮新增 `cooperative/camera_pd_control.py` 与独立 CPU 回归。已实现可调用的候选生成和有限速关节目标输出；**尚未接入实际 runner、未执行相机驱动的机械臂物理预抓取，更未验证夹持、抬升、运输或投桶**。旧 runner、生产抓取证书、冻结源与默认 actuator 均未修改。

用户要求机械臂先用 Kp/Kd，坐标必须来自相机。此桥只接当前本机 front/rear/wrist 的 RGB-D、mask、实际内外参、既有地面关联结果和机器人自身反馈。没有 scene/task/object 目录、垃圾真值 pose、物理见证垃圾状态、UAV 坐标或模型下载入口。无人机粗坐标及约 10 cm 误差由独立搜索/交接链处理，不能填入本桥的机械臂目标。这里的目标仍是相机可见表面，不等完整物体中心。

## 实际 API

```python
proposal = prepare_camera_pregrasp(
    actual_frame, actual_track_mask, actual_camera_spec,
    existing_ground_target, actual_controller_observation,
    confirmation=current_upright_can_confirmation,
    kinematics=chain, now_s=session.time,
)

executor = CameraPDPregraspExecutor(
    chain, actual_controller_observation, soft_arm_limits, hard_arm_limits,
    initial_desired_joint_targets=current_desired_arm_targets,
    actuator_contract=session.arm_control_contract,
    path_reviewer=runtime_owned_path_reviewer,
)

command = executor.update(
    current_proposal_or_none,
    session.controller_observation(), actual_wrist_observation_sample,
    session.time, contact_errors=tuple(contacts.errors),
)
actions = command.as_actions(session.time, session.joint_limits())
# 在保留原记录/接触回调/身体守护的控制循环中送往 session.step(actions)。
```

`chain` 必须是实际 `ArmKinematics(tool_frame=simulation_grasp_geometry().tool_frame)`。默认 gripper-base 原点不能冒充 TCP。输入均使用现有真实类型：`CameraFrame`、`TrackMask`、`CameraSpec`、`GroundGraspTarget`、`ControllerObservation`、`UprightCanConfirmation`、`WristObservationSample`。不由回传 JSON、最近点、UAV proposal 或动作意图重造这些观测。

`GroundGraspTarget` 由已有地面关联接口提供。本桥再次核对当前 localizer 的 surface 坐标和不确定度，既不创建它，也不缩小其不确定度。其关联来源仍是外部显式证据；本轮 `UprightCanConfirmation` 只代表人工当前图像的直立罐模型基线，不代表自动跨视角同物认证。

构造时的 `initial_desired_joint_targets` 必须取**上一实际已发 desired** 六臂目标，不能用实际 q 替代，否则接管会发生首拍目标跳变。现 Session 缓存准确名称是 `_joint_target`，重力偏置前读取，例如：

```python
current_desired_arm_targets = {
    name: float(session._joint_target[0, session._robot_joint_ids[name]])
    for name in ARM_JOINTS
}
soft_arm_limits = {name: session.joint_limits()[name] for name in ARM_JOINTS}
hard_arm_limits = {
    name: tuple(session.robot.data.joint_pos_limits[
        0, session._robot_joint_ids[name]].tolist())
    for name in ARM_JOINTS
}
```

以上是下一步运行器接线示例，当前没有增加读取这些私有缓存的 runner。最初 desired 和 actual q 都必须在原 soft/hard 内；原 fold 的 q3 在 soft 外，因此必须先独立完成已记录的合法 soft-entry，不能借此桥跳过。

## 从实际相机到工具目标

1. 核 `spec.agent_id == observation.robot_id`，拒绝 aerial/observer。实际 `CameraFrame` 必须在该拍本机 observation 中；frame ID、捕获/接收时间、角色、光学 pose、K 和外参 SHA 都相符。实际运行仍须保留 Session 的 PhysX 自身姿态→相机 pose 校验，不能用名义 USD pose 替代测得相机 pose。
2. `localize_mask` 从同曝光 RGB-D 独立重算可见 surface；拒绝无效深度、陈旧帧、先验/真值 mask、错标定、错 K、错 track。`diagnose_visible_geometry` 用 mask 外附近有效深度拟合支撑平面；不填充 NaN/Inf，不用场景地面真值。
3. `fit_upright_cylinder` 和既有 `build_cylinder_grasp_candidate` 在显式人工模型假设下估计圆柱中心、高度及条件 fit 不确定度。原 surface UQ 保留，不能用条件 fit UQ 冒充整体精度；`robust_fit=False` 也明确保留，不删去名义诊断来伪造稳健性。
4. 仅取 `pregrasp`，即名义圆柱中心上方 0.12 m 的工具目标。使用 world-down 与实际 body Y 的水平投影确定名义工具方向，显式转换 world TCP→base TCP，以及 TCP→`gripper_base_link`。这不把 surface 顶部点当 TCP 或抓取中心。
5. 复核 IK 使用的 URDF SHA、simulation TCP 和自身 FK；IK 的 `converged` 标记本身不足以推进。实际每拍自身 q、base pose 和 `gripper_base_link` pose 还必须满足 1 mm / 0.001 rad 的 FK 一致性。整个路径的真实 Jacobian/装配校验仍应沿用空气预抓取的 `validate_actual_arm_kinematics` 诊断，不能凭 CPU IK 代替实际资格。

本桥不执行后续 grasp/lift waypoint，不发手指目标，不发 `begin_grasp/release`，不创建 `PlannedGrasp`，不注册任务成功。`grasp_authorized` 永远 False。

## 独立路径审查与有限速输出

`path_reviewer(paths, proposal, actual_observation)` 由仿真运行器持有，不能取策略动作中的自报结果。返回现有新类型 `PregraspPathReview(accepted, source, evidence)`；没有 reviewer 或返回拒绝时不推进目标。异常先锁存失败再向调用线程传播，运行器必须保存 failure 并停止推进。

每拍送三个 `ArmPathCandidate` 给 reviewer：实际 q→上一 desired、上一 desired→pregrasp、实际 q→拟发本拍 desired。第三段避免把前两段折线的采样通过错误描述成覆盖本拍追踪的短线。候选步长沿用 `candidate_path` 的 0.02 rad；实际 desired 使用一个共享比例沿审过的关节直线前进，最大每关节 0.15 rad/s。首拍无此前 dt，仅原样输出已发 desired，不虚构时间。真实物理路径仍可能偏离这些采样线；review 不是连续碰撞或动态稳定证书。

旧空气实验的具体可复用来源为 `scripts/cooperative/check_arm_pregrasp.py` 中局部 `CapturedJointSourceScreen` 与 `analyze_arm_grasp_candidates.SourceBoundsScreen.path`，它会保留各自 `sampled_source_screen_clear` / 最小间隔证据。但是该筛查只覆盖其声明的自身源几何，不能冒充环境、目标接触或连续碰撞资格。**本轮未实现实际运行器的 reviewer，因此默认构造虽可生成候选，执行仍保持原 desired。**下一受控物理试验须接独立 source 自碰筛查、当前传感深度/支撑面净空检查和实际接触守护，并将其检查范围写入 evidence；不得默认 `lambda ...: accepted=True`。测试中的 accepted callback 仅是明确标记的合成路径夹具。

## 时效、撤销与身体守护

相机最大 age 为 0.35 s。每个物理步都必须给当前候选或 None；上游失视、空 mask、定位拒绝或 IK 失败时给负候选/None，不能只检查旧缓存仍未过 TTL。

新负曝光按其本机 camera/calibration 锁存 tombstone，包括首次绑定前；相同曝光随后变正也不能恢复。恢复须严格更新的曝光。public ID、track、相机、角色、K、外参或人工模型来源变化不能静默切换路线。机器人 base 相比计划时移动超过 5 mm 或旋转超过 0.01 rad 时需新相机候选，不能继续消费冻结在旧 base 上的 IK。

失视、过期、review 拒绝时停止推进并保持上一合规 desired；这不保证物理瞬时刹停。身体、关节、接触、时限或反馈失败锁存为 failed，不能以新图像消除。保留原 `WristObservationConfig` 守护且只允许收紧，包括：

- 实际 soft/hard、hard 容差 0.02 rad、qdot 1.5 rad/s、tracking error 0.45 rad / 0.5 s。
- 身体线速 norm 0.08 m/s、角速 norm 0.5 rad/s、tilt 0.25 rad、离地 0.30–0.85 m。
- 反馈 age / 更新 gap / 命令有效期均 0.02 s；同一物理帧不能重放。
- 模块总预算最大 12 s，自构造 anchor 计时，等待/失视也不重置。
- `contact_errors` 必须每拍显式传入，即使 `contact_violation=False`，接触后端错误仍失败。未监控 contact source 不可推进。无接触事件不构成碰撞净空证据。

只有实际 TCP 误差 ≤0.015 m / 0.08 rad、actual q 与目标误差 ≤0.10 rad、实际 qdot ≤0.15 rad/s，并持续原 0.35 s，才能标 `pregrasp_held`。新负观测会撤销此标志；它始终不是抓取/夹持/清理成功。

## Kp/Kd 与重力项

构造必须传当前 `session.arm_control_contract`；只接受 `task_implicit` 或 `task_implicit_gravity_bias`、Kp=60 N·m/rad、Kd=6 N·m·s/rad、总驱动 effort cap=60 N·m 的实际任务配置。新模块只输出六臂 **desired 位置，单位 rad**，不发根 pose、腿或手指 DOF。

开启 gravity-bias 时，Session 从当前机器人自身 PhysX `get_gravity_compensation_forces` 取 G，仅对六臂使用 `drive = desired + G/60`。本桥不再次加 G，不把 drive 当 desired 接管，不读取垃圾 pose/质量给该补偿。Session 原有限幅、非有限/过 effort cap / hard-limit 的拒绝保留。补偿属于本体模型辅助项，需在实际来源合同中记录，不能宣称纯无模型 PD。

每条正常输出的 diagnostics 保留 public ID、原关联 ID、人工模型来源、agent、camera/frame/exposure/receipt、K、光学 pose、外参 SHA、计划及当前 base、可见 surface、名义 TCP/基座目标、URDF SHA、path review 范围和实际误差；不含 RGB/深度大数组。原图由 `RgbdRecorder` 以 frame ID 另存。本模块没有任务真值或 physics witness 的观察通道。

## 验证与剩余接线

CPU 命令：

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=source/capabilitylab \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venvs/tracking_sam_5090/bin/python -m pytest -q \
  tests/cooperative/test_camera_pd_control.py
```

结果：**41 passed**。解析合成 RGB-D 真正调用 localize、局部支撑面/圆柱 fit、simulation TCP 和 IK，不以 fake planner 代替。负例覆盖 UAV/真值 mask、跨 agent、错 K/外参、无效深度、旧曝光、负先到/后到同帧优先、失视恢复、来源切换、首 desired 接管、变量 dt、review 拒绝/异常、错误机器人 IK、实际 FK、身体/接触/关节/时间守护与实际保持判据。相关 cylinder/surface/IK 四组联测 92 passed；最后只增加来源诊断和收紧可配置上界后，41 项重新通过。

独立只读审查确认上述三项来源/水位/接管修复；未运行 Kit、NN 或 GPU。下一步是由主线程将实际当前相机感知输出、当前 desired 缓存、独立路径 reviewer、`ArmContactReports` 和完整逐物理帧日志接入受控预抓取试验。相机同物验证、未校准几何、实际运动路径、接触/夹持/提升和投放仍各自保留独立资格；不能从此 CPU 结果推断 24 件清理已接通。
