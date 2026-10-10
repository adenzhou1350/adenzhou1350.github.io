## 先看模型怎样做一个选择

推箱子时，模型下一步往哪走？页面有四个按钮时，它该点哪一个？[Jev Decision Teaching](https://github.com/adenzhou1350/jev-decision-teaching) 用这两类小任务讲决策模型：给出当前状态和可选动作，逐个打分，选出一个执行，再读取新的状态。

可以先试玩，再回头读训练代码。仓库带了推箱子的模型和演示页面，用 CPU 就能运行，无需下载语言模型。这是独立的 Jev-style 教学实现，采用候选打分思路，没有复现 TypeSafe Jev 的专有训练方法。

## 在 Windows 上先玩起来

准备 Python 3.11+ 和 Git，在 PowerShell 中运行：

```powershell
git clone https://github.com/adenzhou1350/jev-decision-teaching.git
cd jev-decision-teaching
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jev_teaching
```

打开 `http://127.0.0.1:8765`，选一个关卡，切换训练前后的策略，先点几次单步，再让它自动运行。每一步都会调用模型，也可以用方向键接管。留意模型什么时候兜圈、什么时候把箱子推入死角；这些失败往往比一局顺利通关更容易看出问题。

## 同一个接口，两种模型

推箱子模型接收墙、目标、箱子和玩家四层棋盘信息。CNN 编码棋盘后，共享打分器分别评估上、右、下、左；当前不能执行的动作由规则屏蔽。整个网络有 **360,097 个参数**，从零做监督训练。最短路径求解器只在离线生成标签时充当老师，实际玩游戏时没有求解器兜底。

文本和页面按钮课程则冻结 Qwen3.5-0.8B，用它编码状态与候选描述，再训练一个 **1,024 参数的共享线性头**。它输出候选分数，不生成一段回答；底座的前向计算仍然存在，不能把小头的参数量当成整个系统大小。

这两课需要额外安装模型依赖，并下载完整 Qwen 快照。随附页面按钮头会核验底座指纹；同名模型的快照若不匹配，就要用自己的快照重训头。具体命令见[安装指南](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/docs/getting-started.md)。

## 结果要和任务一起看

以下是仓库一轮固定种子教学实验的训练后结果。推箱子测完整通关，页面按钮测单次选择，两个指标不能直接比较。

| 任务 | 测试范围 | 完成数 |
|---|---|---:|
| 单箱推箱子 | 32 个未见布局、128 个起点 | 122/128 |
| 双箱推箱子 | 12 个布局、48 个起点 | 25/48 |
| 页面按钮 | 六类本地页面、48 条留出表达 | 34/48 |

同一布局的多个起点有关联，页面数据也来自少量合成模板。双箱下降到约一半，按钮模型仍会误读引用和否定；这些数字还不能说明它会通用规划或操作任意网站。随机初始化头也不是原始 Qwen 的生成能力基线。逐条结果和对照方法保留在[实验记录](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/docs/experiments.md)与[证据目录](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/artifacts/README.md)。

## 接下来自己改一次

想先读懂训练，可以从[文本决策头](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/docs/lessons/01-text.md)的 `fit_head()` 入手；想看行动怎样影响后续状态，就读[推箱子课程](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/docs/lessons/02-sokoban.md)。熟悉以后再做[页面按钮课程](https://github.com/adenzhou1350/jev-decision-teaching/blob/main/docs/lessons/03-browser.md)，尝试改写任务里的否定和引用。

第一次实验只改一个变量，例如增加训练布局，保存到新的 `runs/` 目录，比较完整通关率。若根据公开错例继续调参，就另外留出一份新测试集。这样既能保留这次尝试，也能分清模型学到了什么。
