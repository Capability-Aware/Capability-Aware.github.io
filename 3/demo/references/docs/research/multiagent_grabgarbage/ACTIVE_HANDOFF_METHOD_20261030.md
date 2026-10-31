# 靠近失视时的动作条件主动交接方法

本轮主问题是：四足靠近后，前视目标即将进入近处下盲区，如何提前停车并选择能重新观察目标的动作。两个实体是无人机与带臂四足，四个传感器是无人机下视、狗前视、狗后视、腕部相机，不能称四个智能体。抓取暂沿用明确的绝对坐标受控基线；本方法不扩展抓取规划或以抓取接口运行冒充闭环完成。

`cooperative/active_handoff.py`实现纯标准库CPU选择器，可插入现有`BlindspotController`外侧。它只消费已观测RGB-D可见点、公共视觉记忆及机器人/相机自身几何，不读场景垃圾pose、任务目录、物理witness或未来真实相机帧。动作选择和同物验证分开；初始人工当前图像配对可以作为明确披露的身份基线。

## 输入与时间合同

`ObservedCloud.from_surface(target_id, surface)`保留实际camera/track/frame/capture/外参SHA、原surface位置、原不确定度和最多256个可见点。`decide`只使用与`BeliefSnapshot.sources`各route的最后正曝光、位置完全一致的云。旧云不能冒充较新曝光；同帧负证据优先由现有`SharedBeliefMemory`撤销当前有效性，但保留最后正位置用于搜索。新的无人机曝光不刷新地面时钟。

保留全部来源，不平均无人机与地面坐标。规划锚点优先最新匹配的地面实测云；没有可用地面云时才能用无人机粗云作为搜索先验，附`anchor_is_aerial=True`，降低近处信息收益，始终要求新的实际地面曝光。最后正点云可用于最多30秒的名义搜索预测，半径按原半径＋失视时间×0.03m/s扩张；它不是仍然有效的近处确认。当前相机自身pose最大年龄0.35秒；当前地面曝光鲜度同样单独按0.35秒判断。

## 先预测失视，再停稳选择观察

`forecast_loss_horizon(cloud, view, base_pose_world, desired_velocity_body, now_s, *, horizons=(.5,1,2), feedback=None, policy=None)`，把当前实际可见点经过名义body SE(2)运动和持姿相机外参投影到0.5/1/2秒视图。记录FOV内支持点比例、像素边界margin、尺寸和随时间扩张的包络。若传入实际`ViewFeedback`，其公共ID、camera、track、frame、capture和图像尺寸须精确对应当前曝光，用实际mask margin校正初始投影边界。

当前实际负反馈立即建议停车；否则在任一固定短horizon下预计margin不超过20px或支持率低于0.6，就返回`should_stop=True`及第一个风险horizon。它是固定速度＋持姿模型的前瞻，不是已测动力学后果、真实失视时刻或未来LOS。控制方仍每拍使用真实观测与本体守护；不能把预测当新曝光发布。

实际停稳由外部速度/姿态及持续时间守护证明。`decide(..., motion_is_settled=False)`不选择新的观察运动；只有明确的停稳来源才能比较后续动作。候选为stop、front重看、rear复查、wrist观察、turn+wrist、UAV补视。候选的`feasible/feasibility_source`来自外部真实动作库资格，不由选择器证明。

腕展开和turn+wrist的未来相机pose必须来自机器人自身运动学或显式名义动作模型，缺失就拒绝；不从目标真值“对准”相机。`forecast_rigid_camera(view,base_before,base_after)`只传播刚性持姿相机；腕关节变化须另提供自身FK结果。长动作默认上限30秒且必须携带`bounded_profile_id`，由外部执行器监督实际到位与超时。

## 选择持续可观测的动作，避免永久停车

只奖励“停车后还看得见”会偏爱一直停着。本方法额外比较每个候选到位后，沿同一固定名义接近预算继续一段时的相机FOV：`continuation_pose_world`、`continuation_prediction_source`、`continuation_seconds`及`expected_progress_m`。当前比较距离可以统一0.24m，固定最大0.30m。它是名义几何查询，**不是已验证可执行的进度、移动授权或实际位移**。当前腕部持姿倒退的实际资格尚未通过，本轮目标仅为停车→选择观察→实际到位→新腕曝光恢复。

令动作终点可见比例为v₀、名义继续后为v₁。两阶段均须满足与短horizon预警相同的可用视野合同：margin严格大于20px、支持比例至少0.6、最小投影跨度至少3px。只有此时持续支持s=min(v₀,v₁)；缺少continuation或任一阶段不满足时s=0，也不给持续包络或名义进度收益。有效可见性c=0.25v₀＋0.75s。固定评分为：

`utility = information_potential + nominal_observable_progress_potential - cost`

信息项以3×c乘0.5～1的失视时效因子，另加0.5×两阶段均有效的包络支持率及0.25×新地面route收益；UAV仅获0.15倍信息项，地面从UAV粗先验预测则乘0.4。原route实际失效且相机预测未改变时，信息/进度项乘0.05，避免重复原地查询。名义进度评分为2×比较距离×s，只对地面相机使用。成本为0.04×秒数＋0.5×路程米＋1×外部风险标量＋0.0005×焦耳＋0.00001×通信字节。

**v2预先声明两项合同修复，权重不变**：第一，stop仍保留两阶段FOV诊断，但信息、名义进度、成本和utility全部为0。stop本身不是一次感知请求，不能因为比front新曝光少0.3秒成本就永远获选。第二，持续收益与`forecast_loss_horizon`共用同一个margin/支持比例/投影跨度判据，不能预警已判不安全却继续奖励截断mask的局部点。该判据对所有camera统一，不强制选turn，完整可持续的front仍可胜出。v1原源码及真实失败结果保留，不以调权重修饰。

这些是未校准、预先固定的工程权重和信息潜力，未声称Shannon信息增益、成功概率或论文效果。它不会强制选turn：便宜的front动作若确实允许继续观察，应优先获选；若front只在静止时可见而继续后失视，则可能选择更慢的腕观察。每个候选保留完整分数、两阶段投影、来源和拒绝原因；可以用`sustainability_weight=0`作纯瞬时可见性消融。

## API与运行时门禁

`ActiveHandoffPlanner(ground_agent_id=..., aerial_agent_id=..., camera_registry=..., policy=None).decide(snapshot, clouds, views, actions, now_s, *, motion_is_settled=False, motion_state_source='')`返回`HandoffDecision`。注册表必须是两实体的四路物理相机；`CurrentView(spec,pose,captured_at_s,frame_id)`为实际相机自身曝光。`HandoffAction`显式包含动作来源、耗时、预测pose和可选continuation几何。

长动作仅调用`decision.bounded_action_request()`取得独立执行请求。`to_reobserve_option()`只桥接旧FSM真正支持且不超过3秒/0.2米的短动作，长turn+wrist返回None。原`BlindspotPolicy`的3秒recovery与6秒wait不能承担真实约十几秒的转身/腕动作；主线程须在独立动作库到位后才将新的腕曝光交给原三帧恢复门禁。

`ground_confirmation_granted=False`、`continuation_motion_authorized=False`、`continuation_execution_qualified=False`始终成立。预测新route没有身份绑定权；实际新mask/RGB-D和同物复查须通过原公共记忆、负证据撤销与三帧确认，才可进入恢复hold。选择器不发布policy成功标志，不读或改变垃圾状态。

## 对照与当前验证边界

本轮29项新CPU合同测试与现有共享记忆、BlindspotController回归共118项通过（0.28秒）。覆盖提前预测风险、后退改善前视、负反馈无bbox立即停、低成本但不可见动作、持续可见性消融、短front确实更好时不强选turn、长动作预算、旧云重放、同帧负证据优先、UAV更新不刷新ground、无未来腕pose拒绝、带倾角的SE(2)不漂world z、stop零收益、同一视野条件下预警与持续收益一致，以及不颁发continuation授权。它们是合成合同fixture，不是真实恢复率或模型性能验收。

既有combo v3的纯CPU前缀审计见`docs/evidence/multiagent_grabgarbage_active_handoff_prefix_20261030/`：3.2/4.2/5.0/5.2秒各自只用该时刻之前的真实RGB-D、mask及本体反馈，均未满足连续0.5秒静止，因此只建议stop。精确5.02秒才满足该窗口，v1确实将safe_stop排在front新曝光与turn+wrist之前；同时front名义继续后仅约77.9%可见点留在画面，边界已负。该检查没有读未来目标或未来实际camera，不等于执行了新的动作。v2只修上述两项合同，原输入完全相同的CPU复算另存`v2_exact_5_02s.json`，不替代真实执行。实际新曝光复查、front续行最多一次、真实位移和短程预测风险由运行时闭环记录，预算耗尽后才可将front标为不可用并重新选择，不能手工强选turn。

后续固定同一初始人工绑定、同一可见点/相机和实际动作预算，比：被动到边界后停车；只选瞬时可见/时间成本；本方法含短horizon预测但无持续项；完整两阶段方法。实测指标包括预测margin误差、首次失视前停车提前量、实际制动/轨迹、恢复到三帧有效新地面曝光的时间与比例、错误身份确认、超时、感知调用数和通信量。空中候选、几何FOV和同物身份分别计分。

同物复查另作“无检验延续人工ID”与“当前实际mask外观＋独立RGB-D复查”对照，保留原误跟阴影负例以及真实同物因视角纵横比被拒的假阴性；不能只统计拒绝阴影就宣称整体更好。人工提示/配对在各组一致，实际未来帧只在动作后验收，不用于本次候选选择。当前尚未完成上述真实对照，不宣称主动策略已恢复靠近、倒退或全任务抓取。
