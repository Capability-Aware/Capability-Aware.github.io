# C+B阶段展示策略：CB11650 / e469

这是为逐项公开已有结果而保存的阶段候选。原18个展示位置：8项完整、5项部分、5项原Body链待验证；不是全部18项最终通过。动态进展以论文展示页的逐项结果为准。

完整原始文件 `policy_full_raw.pt`，10,967,003 bytes，SHA256：

```
e469b10b11da21ef93cf3c74d3747d9da824dc1b26286293738139a5a6db3849
```

Actor、Critic、归一化、探索、Adam、LR、四类随机状态和原始训练合同均在内，原字节保留。本阶段新增训练0。来源为完整10650共同父续训1000的正式11650终点。

## 加载

在本仓库根目录、含Torch的环境中执行：

```python
import sys
import torch
sys.path.insert(0, 'scripts/locomotion')
from paper_demo_e469_stage_loader_v1 import load_selected, mean_action
model, raw, receipt = load_selected(torch)
# packet217须由所用公开执行profile生成，float32，shape=[N,217]
# action = mean_action(model, packet217)
```

单PT加载器不读取历史祖先权重。实际CPU完整31状态／Actor21恢复、原strict loader的真实217输入与512合成输入均值逐值相等，见manifest证据。输出为12腿关节raw均值，后续原profile执行clip、滤波、限位和PD；不能把均值直接当力矩。

`profiles/`保留本阶段真实运行的合同与结果；`physical_contract.json`为原物理设置。不同任务切换公开目标和执行profile，Actor SHA相同。高速直接Actor，地形含IK/WBC弱Actor正则，机械臂含独立ArmIK与COM反馈。未声称全部为裸Actor、未见场景泛化或真机部署。

阶段视频优先从该权重已有真实仿真记录原速渲染；来源、采样和代表环境逐项登记。PhysX记录在MuJoCo中重画不视为MuJoCo动力学迁移。原“C+B Demo展示”保持冻结，后续发布独立论文页。正式匹配消融另行保留，不能用播放时mask冒充重新训练。
