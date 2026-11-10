# Nav2 联合仿真复核 · 2026-11-10

同一轮 Isaac＋Nav2＋RViz 完成两个独立导航目标，四足使用冻结 MoE 26399。代码提交 `bcf8a2070926c70885d4a7289faf69313c056c80`。

| 导航目标 | 实际路程 | 仿真耗时 | 墙钟耗时 | 终点误差 |
|---|---:|---:|---:|---:|
| CLI：(-39.5, -50.8) | 17.802 m | 36.570 s | 154.228 s | 0.624 m |
| waypoint：(-42.987, -50.577) | 4.620 m | 32.785 s | 137.846 s | 0.644 m |

两个目标均有 Nav2 成功状态及独立位姿稳定1秒的记录，容差0.75m；本轮恢复次数0。无效waypoint `(10000,10000)` 因没有全局路径被拒，原目标编号保持不变并继续完成。实时系数约0.237。

[打开展示页](index.html)观看原始同轮双窗口录屏（610.7秒、4.88MB），以及调整RViz布局后的实际截图。视频保留等待和较窄布局；截图与视频布局不同。没有重新生成或美化机器人、点云和运行过程。

**原始运行没有写出退出 `report.json`。** 本目录的 [offline_review_summary.json](offline_review_summary.json) 是归档时离线复核，引用逐目标JSON、trace、事件及原文件SHA-256；它不冒充运行程序的汇总。退出收尾的后续修复不改变这轮原始证据。

[只读ROS检查](readonly_ros_visual_health.json)验证RGB、CameraInfo、机器人URDF、TF及RViz订阅；`evidence/`与`goals/`保留本轮轻量日志和原结果。未保存逐帧图片、RGB-D序列或rosbag。

本轮不验证100/200m、死路恢复、真实断流注入、精确yaw或整机无碰撞，也不是完整垃圾收集或真机任务。地图和odom使用已知仿真信息。15cm圆半径不能代表真实全机身；低平台完全遮挡地面时仍有种子歧义。

复现：在相同资产和依赖的capability_research工作目录使用记录的提交，启动方式见 `evidence/processes.json`；再运行 `./deploy/ros2_ws/scripts/run_nav2_goal.sh -39.5 -50.8` 和 `./deploy/ros2_ws/scripts/view_lidar_navigation.sh`。本轮三者使用 `ROS_DOMAIN_ID=84`。第二目标由同轮已走轨迹选取，通过 `/navigation/waypoint` 发送，不应从视频时长推断消息时间。

后续退出修复的最终v3[空场景Kit＋实际ROS短检查](post_run_shutdown_smoke.json)由外层核验进程退出码为0，finally和ROS遥测关闭完成。SDK保留默认原生快速退出，app.close没有返回；不声称关闭后信号处理器恢复通过。该检查没有机器人，未重跑完整导航；原始run的report.json仍保持缺失，未补造。
