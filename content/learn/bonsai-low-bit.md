## 从三值编码开始

Bonsai 风格量化教学有三值编码、量化感知训练（QAT）和压缩推理的代码，也保留了实验记录。训练损失下降、检查点能恢复，回答质量仍可能不过关。读实验结果时，解码速度和回答质量要分开看。

可以先用普通 Python 跑下面的小实验，再按手头的机器选择[公开仓库](https://github.com/adenzhou1350/bonsai-qat-teaching)中的练习。读原理和实验记录不需要大显卡。

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

运行后会打印 `packed byte: 183`，下一行是还原出的五个三值编码。可以改掉其中一个数字，看看字节值怎样变化、解包后是否还能得到原来的输入。输入仍须来自 `-1`、`0`、`1`。

这里的 1.6bit 只算了三值编码。实际部署还要存分组尺度、padding、保留的非专家权重和运行缓存，不能把它当成整个模型的平均位宽。这个程序也没有做权重拟合、训练或推理；分组三值网格、STE 和张量打包的实现放在 [quantization.py](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/quantization.py)。

## 按资源选择学习路线

| 路线 | 你能学习什么 | 需要准备什么 | 当前范围 |
|---|---|---|---|
| CPU 原理与测试 | 三值网格、STE 梯度、打包、恢复后下一步是否一致 | Linux CPU 环境，安装仓库所列依赖 | 小规模方程和检查点测试，不加载大模型 |
| 35B 全专家 QAT | 准备数据与教师、更新专家主权重、保存和恢复 | Linux、2×B300、原模型和本地文本 | 全 40 层两步控制通过；长程训练暂停，未完成质量验收 |
| 122B MoE 固定产物推理 | 压缩布局、单卡生成、HTTP 服务与计时 | Linux、32GB RTX 5090、指定 packed 权重和匹配环境 | 固定产物 CLI 与 HTTP 实验完成；质量未达标，仓库未提供权重 |
| 122B 校准与 CPU 初始化 | 重建校准数据、拟合低比特权重、组装 seed | 原始 BF16 模型、大内存 Linux CPU | 数据与初始化课程已发布；完整恢复训练链尚未跑通 |

35B 指 Qwen3.5-35B-A3B，122B 指 Qwen3.5-122B-A10B。两者都是 MoE，总参数量和每 token 激活的参数量不同。单卡运行 122B MoE，不等于能运行同规模的稠密模型。

主课程的 35B 全专家权重 QAT 会更新 FP32 主权重，在每次前向时重新投影到三值网格。122B 走的是另一条路线：冻结三值专家和非专家 4bit 权重，只训练 rank-8 补偿。具体方法见 [METHOD.md](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)。

## 跑完编码实验之后

仓库的[四节动手课程](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/LABS.md)列出了每个练习的输出、完成后要回答的问题，以及所需资源。第一次读可以按这个顺序：

1. 读[方法说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)，弄清哪些参数参与训练，哪些保持冻结。
2. 在 Linux CPU 环境按[复刻步骤](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/REPRODUCING.md)安装匹配依赖，运行 CPU 测试 `test_equations.py`。通过信息应以 `PASS: ternary grid, identity STE, packing` 开始。检查点实现用了 POSIX 目录同步，这条测试路线尚未验证 Windows 原生支持；上面的纯 Python 编码小实验没有这个依赖。
3. 打开[测试源码](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/test_equations.py)，找到打包往返、STE 梯度和检查点恢复的断言。再想想：只看到 loss 下降，能发现这些地方的错误吗？
4. 有对应训练资源时，按复刻步骤做 35B 两步控制。检查数据、教师位置、导出文件和检查点都对得上，再决定是否启动长程训练。
5. 读[实验索引](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/README.md)，分开记录训练、数值检查、能力评测和计时结果。

完整的 35B 训练很吃显存，不能按部署时的占用来准备机器。公开记录中的专家训练状态约 480GiB，两步实测峰值每卡约 247.5GiB，完整检查点约 360GiB/份。这也是完整训练路线使用 2×B300 的原因。手头显卡装不下时，可以先做 CPU 练习、读代码。

## 怎样阅读 122B 单卡案例

[122B 运行说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/experimental122/README.md)记录了新旧两版固定产物。新版已完成训练、独立数值检查和单张 RTX 5090 推理，也做了四组公开开发评测。四组结果都低于对应原生 BF16 基线，质量未达标。

仓库没有提供模型权重。要运行这个案例，需要另行取得与所选 manifest 对应的 packed 权重，不能直接传入原始 BF16 模型。仅克隆仓库，也还无法从头重建记录中的 122B 产物。完整可移植训练链路和质量复刻还缺哪些部分，见 [122B 实验记录](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/122B.md)。

最近的 HTTP 实验用了四个闭环客户端，原预填充与可选分组预填充的合计输出吞吐为 21.01 / 23.30 tokens/s。这是 8 条固定提示反复请求的观测结果，不是每个用户都能获得的生成速度。256 条正式请求中有 12 条与旧 CLI 的完整输出 token 序列不同，原版和优化版都出现差异，严格输出一致性验收未通过。

读速度数字时，要一起看权重版本、输入和输出长度、并发数，以及计时是否包含预填充和 Graph 录制。显存也有不同口径：模型持久存储约 28.10 GiB，HTTP 已采样 NVML used 峰值约 30.64 GiB，驱动另保留约 0.484 GiB。不能只拿权重大小估算显卡要求。分数、显存、CLI 与 HTTP 的完整解释放在[结果说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/RESULTS.md)，具体定位过程见[推理适配实验](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/INFERENCE.md)。

本轮研究已暂停，已有代码、证据和检查点保留。35B 全专家训练尚未完成；122B 的[CPU 初始化课程](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/courses/122b/seed_cpu/README.md)已经发布，完整教师生成、恢复训练和新产物部署仍未连通。可以按已验证的范围学习，不必把历史记录里的“等待”理解成当前仍在运行。

## 留下你自己的实验记录

每次实验至少记下仓库 commit、模型与权重身份、环境、输入数据和实际命令，再写上预期结果、实际结果以及还没验证的部分。如果换了数据，可以继续用来学习训练机制，但结果不能算作原有能力分数的复刻。

整理结果时，分别回答四个问题：编码能否还原？恢复后下一步是否相同？独立评测是否达标？速度是在什么条件下测得的？

这里的方法与实验状态核对至公开仓库 `ce2e903` 的 2026-10-10 收尾记录；阅读入口随本次文档整理更新。后续进展请看仓库中带日期的实验索引。目前这些工作属于 Bonsai 风格教学与实验，尚未完整复现 Bonsai 训练方案，也没有通过原定质量门槛。
