## 从三值编码开始

Bonsai 风格量化教学有三值编码、量化感知训练（QAT）和压缩推理的代码，也保留了实验记录。训练损失下降、检查点能恢复，回答质量仍可能不过关。读实验结果时，解码速度和回答质量要分开看。

可以先在浏览器里改几个数，试试下面的编码小实验，也可以复制 Python 示例到本地运行。之后再按手头的机器选择[公开仓库](https://github.com/adenzhou1350/bonsai-qat-teaching)中的练习。读原理和实验记录不需要大显卡。

想直接使用模型，27B、35B 和 122B 权重都已公开；从[安装、下载与提问步骤](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md)开始。三款使用不同量化方法，速度也不同。

## 先用五个数字理解 1.6bit

三值权重的编码只有 `-1`、`0`、`1`。把它们映射成三进制的 `0`、`1`、`2`，五个编码一共有 `3^5 = 243` 种组合，可以放进一个有 256 种取值的字节。只看这部分编码，每个权重占 `8 / 5 = 1.6bit`。

{{TERNARY_DEMO}}

想自己运行，把当前示例保存为 `ternary_demo.py`，再运行 `python ternary_demo.py`。只用 Python 标准功能，不需要模型、PyTorch 或 GPU。

默认输入打包后是 `183`，二进制为 `10110111`，解包后仍是原来的五个数。改掉其中一个选项，看看字节值怎样变化，再把全部选项设为 `-1` 或 `+1`，试试两端的取值。

这里的 1.6bit 只算了三值编码。实际部署还要存分组尺度、padding、保留的非专家权重和运行缓存，不能把它当成整个模型的平均位宽。这个程序也没有做权重拟合、训练或推理；分组三值网格、STE 和张量打包的实现放在 [quantization.py](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/quantization.py)。

## 按资源选择学习路线

| 路线 | 你能学习什么 | 需要准备什么 | 当前范围 |
|---|---|---|---|
| CPU 原理与测试 | 三值网格、STE 梯度、打包、恢复后下一步是否一致 | Linux CPU 环境，安装仓库所列依赖 | 小规模方程和检查点测试，不加载大模型 |
| 35B 全专家 QAT | 准备数据与教师、更新专家主权重、保存和恢复 | Linux、2×B300、原模型和本地文本 | 全 40 层两步控制通过；长程训练暂停，未完成质量验收 |
| 27B 三值 QAT | 旋转、量化、教师蒸馏与检查点恢复 | 按课程准备 Linux、GPU 和主机内存 | 32 步版已公开；96 步候选已保存和恢复，质量仍未通过 |
| 三款固定产物推理 | 下载校验、自定义提问、显存与计时 | Linux、32GB RTX 5090、指定 packed 权重和匹配环境 | 权重均已公开；部署入口与验证范围见下表 |
| 122B 校准与 CPU 初始化 | 重建校准数据、拟合低比特权重、组装 seed | 原始 BF16 模型、大内存 Linux CPU | 数据与初始化课程已发布；完整恢复训练链尚未跑通 |

27B 指稠密模型 Qwen3.8-27B；35B 和 122B 分别是 Qwen3.5-35B-A3B、Qwen3.5-122B-A10B，都是 MoE。MoE 的总参数量和每 token 激活的参数量不同，不能按模型名称里的 B 数直接排序生成速度。

主课程的 35B 全专家 QAT 会更新 FP32 主权重，每次前向重新投影到三值网格。公开的 **R35-8192 是 INT2 专家加 rank-16 补偿**，与这条尚未完成的训练路线不同。122B 则冻结三值专家和非专家 4bit 权重，只训练 rank-8 补偿。方法对照见 [METHOD.md](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)，27B 从[小机制课程](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/courses/qwen38_bonsai2/README.md)开始。

## 跑完编码实验之后

仓库的[四节动手课程](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/LABS.md)列出了每个练习的输出、完成后要回答的问题，以及所需资源。第一次读可以按这个顺序：

1. 读[方法说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/METHOD.md)，弄清哪些参数参与训练，哪些保持冻结。
2. 在 Linux CPU 环境按[复刻步骤](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/REPRODUCING.md)安装匹配依赖，运行 CPU 测试 `test_equations.py`。通过信息应以 `PASS: ternary grid, identity STE, packing` 开始。检查点实现用了 POSIX 目录同步，这条测试路线尚未验证 Windows 原生支持；上面的纯 Python 编码小实验没有这个依赖。
3. 打开[测试源码](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/test_equations.py)，找到打包往返、STE 梯度和检查点恢复的断言。再想想：只看到 loss 下降，能发现这些地方的错误吗？
4. 有对应训练资源时，按复刻步骤做 35B 两步控制。检查数据、教师位置、导出文件和检查点都对得上，再决定是否启动长程训练。
5. 读[实验索引](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/README.md)，分开记录训练、数值检查、能力评测和计时结果。

完整的 35B 训练很吃显存，不能按部署时的占用来准备机器。公开记录中的专家训练状态约 480GiB，两步实测峰值每卡约 247.5GiB，完整检查点约 360GiB/份。这也是完整训练路线使用 2×B300 的原因。手头显卡装不下时，可以先做 CPU 练习、读代码。

## 三款模型怎样部署，速度多少

先完成[一次环境安装](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md)，再复制对应模型的下载与运行命令。35B 提供常驻终端聊天；122B 和 27B 提供自定义问题入口。它们是自定义压缩格式，不能直接交给标准 `AutoModel`、llama.cpp 或 `vllm serve`。

| 公开产物 | 单卡 5090 速度记录 | 部署入口 |
|---|---|---|
| 35B · R35-8192 | 短上下文 **59.33**、4K **49.85 token/s**；历史固定 64 步热解码 | [下载与常驻聊天](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md#35b) |
| 122B · native4095 | 历史短请求 CLI **21.72–24.00 token/s** | [下载与自定义提问](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md#122b) |
| 27B · step32 | 公开 `decode_rotate` 路径短提示热解码 **9.37 token/s** | [下载与自定义提问](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md#27b) |

**测试口径不同，这不是统一榜单。** 35B 的历史测试遇 EOS 仍跑满 64 步，新便携入口尚未 GPU 复验；122B 的范围对应原预填充与分组预填充 CLI 历史对照，不是当前 `infer_hf.py` 的新测速。27B 只测八条短开发题的热计算，共用生成代码已测，单独交互 CLI 未直接 GPU 调用。

27B 的私有 GDN Graph 实验测得 **9.40 → 13.02 token/s**，但便携 Graph 入口尚未完成 GPU 验证，本轮不发布；部署仍用上表的 9.37 路径。[收尾记录](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/2026-10-20-q38-inference-closeout.md)保留结果。本轮已停止继续优化，速度或数值一致都不代表量化质量达标。

下载大小、固定版本和上下文配置见[部署指南](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT.md)；显存与完整计时范围见[参数参考](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/DEPLOYMENT_REFERENCE.md)。35B 可先用 4K 上下文和 256 输出上限；27B 当前入口含模板输入最多 128 token，输出最多 64 token。

## 怎样阅读 122B 单卡案例

想先看这次实验做到了什么，可以读[单张 5090 跑 122B MoE 的案例](/blog/bonsai-5090-experiment/)。里面放在一起比较了模型存储、运行占用与配对评测，也记录了一次最终没有采用的解包优化。

如果想核对这些数字，克隆仓库后可以先运行下面的标准库脚本，Windows 和 Linux 都不需要安装模型依赖：

```bash
python scripts/check_public_evidence.py
```

它核对已公开文件的哈希，并从摘要重算 HTTP 吞吐、请求差异数与显存单位。`PASS` 表示文件和摘要算术相符，不代表重跑了模型或验证了未发布的原始日志。[公开证据说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/PUBLIC_EVIDENCE.md)逐项列出仓库里能拿到什么，以及继续复现还缺哪些文件。

这套文件与摘要检查也配置在 [GitHub Actions](https://github.com/adenzhou1350/bonsai-qat-teaching/actions/workflows/public-evidence.yml) 中，分别在 Linux 和 Windows 环境执行。

[122B 运行说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/experimental122/README.md)记录了新旧两版固定产物。新版已完成训练、独立数值检查和单张 RTX 5090 推理；四组公开开发评测都低于对应原生 BF16 基线，质量未达标。

三款权重现在均已在 Hugging Face 公开，下载地址与固定提交见[发布目录](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/model-releases.json)。122B 公开包使用 `infer_hf.py`，旧 `infer.py` 和 HTTP 入口不能直接加载新清单。完整训练与质量复刻的缺项仍见 [122B 实验记录](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/experiments/122B.md)。

历史 HTTP 实验的四客户端合计吞吐为 21.01 / 23.30 token/s，不能当作每个用户的生成速度。256 条正式请求中有 12 条与旧 CLI 的完整输出 token 序列不同，严格输出一致性验收未通过；它不是上表公开包的已验证服务。

显存同样要看口径：122B 模型持久存储约 28.10 GiB，历史 HTTP 采样 NVML used 峰值约 30.64 GiB，驱动另保留约 0.484 GiB。分数、显存、CLI 与 HTTP 的完整解释见[结果说明](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/docs/RESULTS.md)。

已有代码、证据和检查点保留，35B 全专家训练与 122B 研究继续暂停。122B 的[CPU 初始化课程](https://github.com/adenzhou1350/bonsai-qat-teaching/blob/main/courses/122b/seed_cpu/README.md)已发布，从原模型重新训练到新部署产物的完整课程仍未连通；历史记录里的“等待”不表示当前仍在运行。

## 留下你自己的实验记录

每次实验至少记下仓库 commit、模型与权重身份、环境、输入数据和实际命令，再写上预期结果、实际结果以及还没验证的部分。如果换了数据，可以继续用来学习训练机制，但结果不能算作原有能力分数的复刻。

整理结果时，分别回答四个问题：编码能否还原？恢复后下一步是否相同？独立评测是否达标？速度是在什么条件下测得的？

阅读入口与公开材料核对至 **2026 年 10 月 21 日**，对应教学仓库 [`9a96af3`](https://github.com/adenzhou1350/bonsai-qat-teaching/tree/9a96af3a60fe34c7965f08158e10e9b60e8ebb25)。三款部署权重已公开，本轮优化已停止；尚未完整复现 Bonsai 官方训练方案，也没有通过原定质量门槛。
