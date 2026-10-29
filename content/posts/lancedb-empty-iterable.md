给 LanceDB 提供字段结构后，即使暂时没有数据，也应该能先建一张空表。但在这个问题里，同样的 schema，下面两种写法会得到不同结果：

```python
db.create_table("a", data=[], schema=schema)
db.create_table("b", data=iter(()), schema=schema)
```

第一行正常，第二行却抛出 `RuntimeError: coroutine raised StopIteration`。还有一个相关问题：把 RecordBatch 装进 tuple，转换器会直接对 tuple 调用 `next()`，连第一批都读不到。这些行为记录在 [LanceDB PR #4538](https://github.com/lancedb/lancedb/pull/4538)。

## 问题落在共用的转换器里

沿着数据转换入口看，list 有专门的处理分支：空列表配上 schema，可以构造一个空 Arrow reader。通用 Iterable 则进入 `_iterator_to_reader`。旧代码没有把已有 schema 传进去，而且一上来就取第一批数据。

这里叠了两个假设。一个是“能遍历的对象可以直接 next”，但 tuple 是可迭代对象，要先取到它的迭代器；另一个是“一定有第一批”。空迭代器恰好没有，`StopIteration` 没被处理，最终在协程边界表现成了难以理解的运行时错误。[源码与改动](https://github.com/lancedb/lancedb/pull/4538/files)

## 先分清空和非空，再决定 schema 从哪来

修复先把 schema 传给 helper，再用一次 `iter(data)` 统一输入，之后始终消费同一个迭代器。读取第一批时处理结束信号：已经有 schema，就返回带这些字段、没有 batch 的 reader；没有 schema，就抛出清楚的 `ValueError`，告诉调用者空输入无法推断字段。

如果读到了第一批，仍按原流程从它取得 schema，再转换后续批次，必要时做类型转换。这样补上了空输入，也保留了正常数据的推断路径；取出来的第一批会继续交给 reader，不会在检查时丢失。[最终实现](https://github.com/lancedb/lancedb/blob/9f4cd1618bddf1041c8ebdaa0b0ccb33656dc57c/python/python/lancedb/table.py#L482)

`add()` 的边界也单独留了测试：清洗路径拿得到现有表的 schema，可以接受空输入；默认路径仍拒绝缺少输入 schema 的空迭代器。这次没有把所有空输入一律放行。

## 验证要让原版和修复版回答同一道题

回归覆盖同步、异步建表，iterator 和 tuple，空与非空，以及有无 schema 的组合。按 PR 保留的验证记录，完整 `test_table.py` 与 `test_scannable.py` 两个模块在修复后 **268 项通过、0 跳过**；把同一套测试交给未修改的实现，是 **24 项失败、244 项通过**。这些数字只属于这两个模块。

验证用仓库的 `ci` profile，从基线 `9f37f392` 构建真实 Rust/PyO3 扩展。两组 Python 代码共享同一份已核验扩展和锁定依赖，都限制为四个 CPU。此前未限制 CPU 亲和性的尝试，在该环境的内存限制下耗尽了线程创建能力；那次失败没有计入通过结果。

Python 包范围的 Ruff 检查和格式检查通过；仓库级检查仍报告未修改的 `docs/web-tests` 中已有问题。这是功能修复记录，没有全平台或性能提升结论，本次整理也未重跑这些测试。

这个 PR 由我以 adenzhou1350 提交，Xuanwo 审核批准，并于 **北京时间 2026 年 10 月 23 日** 合入。它改动不大，但把接口的约定补齐了：已给出字段结构的空数据，应能以一致的方式抵达建表逻辑。[合入提交](https://github.com/lancedb/lancedb/commit/9f4cd1618bddf1041c8ebdaa0b0ccb33656dc57c)
