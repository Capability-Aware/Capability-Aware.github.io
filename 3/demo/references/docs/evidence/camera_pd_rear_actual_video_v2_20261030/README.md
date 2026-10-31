# 真实相机PD case独立同步媒体

本次 stage=`controlled_camera_pd`，实际 2870 物理步；六路共享曝光 144 组，源共享末拍 14.300s。首失败 13.850000000000765s；原失败 'bounded_current_wrist_candidate_unavailable'。

从真实 `camera_pd_trace.jsonl` 读取每拍next_command/current_camera_candidate/camera_pd_command与来源标签；未构造旧front/tail trace。两第三视角+四机载同真实物理曝光，逐RGB/depth/mask检查SHA。mask仅显示覆盖，不用于身份或成功认证。预览展开不等于执行PD，PD pregrasp不等于抓取投桶；仍0/24。

保留最初.005s曝光，按10fps逐真实组编码，成片长度与源终止时刻有差异。原失败及后续真实尾录保留，不补帧/复制尾帧。source_recording保存选定少量原图、原源代码快照与全部闭合元数据/压缩逐物理证据；完整depth/未选RGB仍在原run，不将此部分归档称完整原录制。

运行依赖闭合合同存在：True；旧preview没有该合同，不能继承后续actual依赖闭合资格。所有publish manifest均排除__pycache__/pyc缓存。
