# Grab-Garbage（Paper 3）演示

站点路径：`/3/demo/`。主展示已更新到 v37：六路同轮画面以 3 行×2 列同步播放（无人机俯视、四足前视、四足后视、腕部、observer wide、observer side）。两段原始组合视角也保留在页面折叠区。

v37 在一个连续 session 中完成 2/2 个请求目标并正确投入 `bin_0_can`；场景目录 24 件只完成 2 件，`full_task_success=false`。机载和 observer 视频均为 5 fps、1871 帧、374.2 秒。

目标框及腕部确认来自确切当前图像的外部人工标注/复核；四足使用冻结 MoE 26399，正式抓取算法尚未交付，机械臂仍用临时 PD（Kp=60、Kd=12）。原始 RGB-D 和逐步物理日志不放入网站仓库。视频与封面校验信息见 `DISPLAY_BUNDLE_MANIFEST.json`。
