## 这门专题想回答什么

模型权重变小之后，为什么有时能运行，却不能可靠回答？训练损失降低、检查点能恢复、解码变快，分别说明了什么？

**Bonsai 风格量化教学**把这些问题放进可阅读的代码和真实实验记录。从三值编码、量化感知训练（QAT）到压缩推理，沿途检查方法、实现和结果，而不是只展示一个显存或速度数字。

这篇是学习路线的入口。你可以先用普通 Python 完成下面的小实验，再按自己的资源进入[公开仓库](https://github.com/adenzhou1350/bonsai-qat-teaching)。阅读原理和检查实验记录不需要拥有大显卡。

## 先用五个数字理解 1.6bit

三值权重的编码只有 `-1`、`0`、`1`。把它们映射成三进制的 `0`、`1`、`2`，五个编码一共有 `3^5 = 243` 种组合，可以放进一个有 256 种取值的字节。只看这部分编码，每个权重占 `8 / 5 = 1.6bit`。

把下面代码保存为 `ternary_demo.py`，运行 `python ternary_demo.py`。只用 Python 标准功能，不需要模型、PyTorch 或 GPU。

```python
trits = [-1, 0, 1, -1, 1]
packed = sum((value + 1) * 3 ** i for i, value in enumerate(trits))
restored = [(packed // 3 ** i) % 3 - 1 for i in range(5)]

assert 0 <= packed < 256
assert restored == trits
print("packed byte:", packed)
print("restored:", restored)
```

预期输出是 `packed byte: 183`，以及原来的五个三值编码。试着改变一个数字，观察字节值与解包结果；所有输入仍须来自 `-1`、`0`、`1`。

**1.6bit 不是整个模型的平均位宽。** 实际部署还要存分组尺度、padding、保留的非专家权重与运行缓存。上面的程序只演示编码和解码，没有进行权重拟合、训练或推理。仓库的 [quantization.py](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/quantization.py) 才包含分组三值网格、STE 与张量打包实现。

## 按资源选择学习路线

| 路线 | 你能学习什么 | 需要准备什么 | 当前范围 |
|---|---|---|---|
| CPU 原理与测试 | 三值网格、STE 梯度、打包、下一步恢复一致性 | Linux CPU 环境，安装仓库所列依赖 | 小规模方程和检查点测试，不加载大模型 |
| 35B 全专家 QAT | 准备数据与教师、更新专家主权重、保存和恢复 | Linux、2×B300、原模型和本地文本 | 全 40 层两步控制通过；长程与能力结果看实验索引 |
| 122B MoE 固定产物推理 | 压缩布局、舍入一致性、单卡生成与计时 | Linux、32GB RTX 5090、指定 packed 权重和匹配环境 | 已完成固定产物推理；质量未达标，仓库未提供权重 |

35B 指 Qwen3.5-35B-A3B，122B 指 Qwen3.5-122B-A10B。**两者都是 MoE；总参数与每 token 激活参数不同。** 不能把单卡运行 122B MoE 描述成单卡运行同规模稠密模型。

主课程是 **35B 全专家权重 QAT**：训练 FP32 主权重，每次前向重新投影到三值网格。122B 案例则冻结三值专家和非专家 4bit 权重，训练 rank-8 补偿；它是另一条实验路线。详细区分见 [METHOD.md](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)。

## 接着读代码，检查一个可解释的结果

1. 阅读[方法说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)，先回答“哪些参数训练，哪些参数冻结”。
2. 在 Linux CPU 环境按[复刻步骤](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/REPRODUCING.md)安装匹配依赖，运行 CPU 测试 `test_equations.py`。预期得到以 `PASS: ternary grid, identity STE, packing` 开始的通过信息。检查点实现使用 POSIX 目录同步，这条测试路线尚未验证 Windows 原生支持；上面的纯 Python 编码小实验没有这个依赖。
3. 对照[测试源码](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/test_equations.py)，找出打包往返、STE 梯度和检查点恢复各自对应的断言。思考为什么只检查 loss 下降还不够。
4. 有对应训练资源时，再按复刻步骤做 35B 两步控制。先核对数据、教师位置、导出文件与检查点，再决定是否启动长程。
5. 阅读[实验索引](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/README.md)，把训练、数值检查、能力评测和计时分别记录。

35B 的训练显存与部署显存差别很大。公开记录中的专家训练状态约 480GiB，实测两步峰值每卡约 247.5GiB，完整检查点约 360GiB/份。因此这里的完整训练路线按 2×B300 编写；小显存显卡仍可以从 CPU 原理和代码阅读开始。

## 怎样阅读 122B 单卡案例

[122B 运行说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/experimental122/README.md)记录了新旧两版固定产物。新版完成了训练、独立数值检查、单张 RTX 5090 推理，以及四组公开开发评测；四组结果均低于对应原生 BF16 基线，**质量未达标**。

仓库不包含模型权重。运行需要另行取得与所选 manifest 对应的 packed 权重；不能直接传入原始 BF16 模型，也不能仅凭克隆仓库从头重建已记录的 122B 产物。完整可移植训练链路与质量复刻仍有缺口，见 [122B 实验记录](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/122B.md)。

测速还要检查权重版本、上下文长度、输出 token 数，以及是否计入预填充和 Graph 录制。当前公开单卡记录是固定输入、单请求的工程测量，不能推导并发服务容量。舍入、后端与缓存的具体问题见[推理适配实验](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/INFERENCE.md)。

## 留下你自己的实验记录

每次实验至少记录仓库 commit、模型与权重身份、环境、输入数据、实际命令、预期结果、实际结果和未验证项。更换数据可以学习训练机制，但不能声称复刻了原来的能力分数。

读完这个专题，可以用四句话检查自己的结论：编码能否还原？恢复后下一步是否相同？独立评测是否达标？速度在什么条件下测得？它们是四个不同的问题。

本导读依据公开仓库 `7248f7f` 的方法、复刻步骤和实验记录整理；状态为 2026-10-09 的记录。后续进展以仓库中带日期的实验索引为准。这是 Bonsai 风格教学与实验，尚未建立完整 Bonsai 训练方案复现或能力恢复的结论。
