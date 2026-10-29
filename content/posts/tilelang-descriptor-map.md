输入缓冲区叫 `A`，输出缓冲区叫 `A_desc`。这两个名字看起来都很普通，却能让 TileLang 在构造调用包装代码时失败，报出 `Handle name A_desc_1 not found in desc_name_var_map`。我提交的 [PR #3484](https://github.com/tile-ai/tilelang/pull/3484) 修的就是这条路径。

## 名字相似，类型却不同

走 TMA lowering 时，输入 `A` 会生成一个描述符参数 `A_desc`，它的声明类型是 `CUtensorMap`。原本叫 `A_desc` 的普通输出则变成 `A_desc_1`。生成的参数里同时出现：

```cpp
const CUtensorMap A_desc
half_t* A_desc_1
```

名字相似，类型却不同。后面的包装代码需要把真正的描述符名字对应回缓冲区，不能把普通指针也登记进去。

## 判断失败，字典却已经变了

定位到 `maybe_desc_name` 后，问题出在检查顺序。它先看名字是不是 `A_desc` 或以 `A_desc_` 开头，只要符合，就立即写入 `desc_name_map`；然后才检查相邻声明是不是 `CUtensorMap`，决定返回 True 还是 False。

对于普通指针 `A_desc_1`，第二步会返回 False，但第一步已经留下了错误映射。调用方得到“这不是描述符”，共享字典里却多了一项“这是 A 的描述符”。之后包装代码照着字典查找对应变量，自然找不到。只检查返回值，很容易漏掉这种失败后仍然残留的修改。

修复把写入放到类型检查之后：先计算 `is_descriptor`，确认相邻声明里确有 `CUtensorMap`，并且调用方提供了映射表，才登记名字。名称匹配失败、类型不符都不改表。真正的描述符仍沿用原来的映射方式。[最终代码](https://github.com/tile-ai/tilelang/blob/10866657c0f7b96aca1ee162c792866de4323941/tilelang/jit/adapter/utils.py#L321)

## 测试与最后的评审

验证时也需要把两件事分开看：小测试能检查“返回 False 后，字典是否原样保留”；真实 lowering 路径则能检查生成的参数是否真的会触发问题，以及包装代码能否构造出来。删除测试文件之前，记录中的原版和当时主线工具模块都是两项失败、一项通过；修复版三项通过，包含真实 TMA lowering。隐藏 CUDA 后是两项通过、一项跳过，较早的 CUDA CI 也通过了这三项。[验证记录](https://github.com/tile-ai/tilelang/pull/3484)

但这些测试没有作为最终文件留下。评审要求收缩范围，移除整个 adapter-wrapper 测试文件、保留映射修复；随后维护者提交了删除。公开讨论记录了收缩范围的要求，没有进一步解释这一取舍。[评审原文](https://github.com/tile-ai/tilelang/pull/3484#discussion_r4398683797) · [删除提交](https://github.com/tile-ai/tilelang/commit/267d6c65c38ac843d6b82ff10871bc56f363ecc0)

所以，三项通过是删除前的回归证据，不是最终版本仍有这三项测试。删除提交记录的检查是 `git diff --check` 和针对工具文件的格式检查。这里没有本地 GPU kernel 执行、从头完整原生构建或全项目 CI 通过的结论。

这类辅助函数看起来只是在做判断，实际上还承担了登记状态的工作。下次排查类似代码，我会把返回值和调用后的字典一起看，尤其留意“验证没通过，但修改已经发生”的分支。

PR 于 **2026 年 10 月 28 日**合入，最终提交为 [`10866657c0f7`](https://github.com/tile-ai/tilelang/commit/10866657c0f7b96aca1ee162c792866de4323941)。以上是对公开补丁、评审和既有验证记录的整理，没有为本文重新运行实验。
