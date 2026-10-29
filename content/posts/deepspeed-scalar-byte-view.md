一个模型只有一个可训练参数，也可能在初始化时出错。这里的输入很普通：`nn.Parameter(torch.tensor(1.0))`。它有一个元素，但形状是 `[]`，也就是零维张量；和形状为 `[1]` 的单元素向量不同。

这个问题先由 jinyouzhi 在 [DeepSpeed issue #8639](https://github.com/deepspeedai/DeepSpeed/issues/8639) 报告。我提交的 [PR #8642](https://github.com/deepspeedai/DeepSpeed/pull/8642) 修复了相关广播路径，于 2026 年 10 月 27 日合入。

## 失败发生在广播之前

沿公开的报错位置看，初始化进入 `DeepSpeedEngine._broadcast_model()` 后，会先把参数存储解释成 `uint8` 视图，再交给广播函数。这样传输的是参数原有的字节，而不是经过数值转换的一组整数。

问题出在这次视图转换。一个 float32 元素占四个字节，uint8 元素占一个字节。PyTorch 在两种元素大小不同的 dtype 之间重解释时，对张量维度有要求；零维输入直接调用 `view(torch.uint8)` 会报 `self.dim() cannot be 0`。通信函数还没执行，初始化就中断了。

这一点也解释了为什么“参数只有一个数”仍然重要：元素个数相同，形状不一定相同。原路径处理普通参数时没有触及的维度条件，被标量参数触发了。

## 补一维，但保留原参数

原 issue 已提出先为标量增加一维的办法。最终补丁把这个处理放进一个小函数：

```python
def view_as_uint8(tensor):
    if tensor.ndim == 0:
        tensor = tensor.unsqueeze(0)
    return tensor.view(torch.uint8)
```

`unsqueeze(0)` 为标量建立一维视图，仍共享原来的存储。随后取得字节视图，广播写入的内容仍会更新原参数；原参数自身的形状和 dtype 不需要改变。非标量输入继续走原来的字节视图路径。

修复也不能只停在报错的那一行。同类转换还用于 ZeRO 参数初始化、模块初始化回调，以及 `GatheredParameters` 退出时的更新广播。[最终 diff](https://github.com/deepspeedai/DeepSpeed/pull/8642/files) 将这些位置统一接到同一个函数，避免不同入口各自处理标量。

## 测试要看同步后的值，也要看形状

随附回归测试使用两个 CPU/Gloo rank，让它们分别以 `1.0`、`2.0` 初始化参数。初始化结束后，两边都应该得到来源 rank 的 `1.0`，形状仍为 `[]`。ZeRO stage 3 在聚合参数后检查这两个条件，stage 0 直接检查。

如果两边起始都是 `1.0`，即使没有完成预期广播，最后的值也可能对上。特意使用不同初值，才能让断言检查同步行为，而不只是看初始化是否抛异常。

PR 记录的验证环境是 Python 3.12、PyTorch 2.12.1，两种 stage 均通过；相同的 stage 0 测试在未修改的基线上重现了维度错误。这个对照同时检查了“能初始化”“值确实同步”和“没有把标量永久改成向量”。

这些结果限于该 CPU 分布式回归。补丁替换的所有广播入口并未因此获得逐项测试覆盖，也没有 GPU 分布式或性能结论。原 issue 中的 GPU 复现属于报告者的环境，不能算作这次补丁的 GPU 验证。本文依据公开代码、评审与历史测试记录整理，没有重跑实验。
