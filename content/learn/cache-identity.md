截图内容变了，文件名没变，缓存会返回什么？下面的交互演示可以直接试，看看按文件名缓存和按内容缓存会给出什么结果。

不用安装软件。演示中的“编码器”只读取虚构文本里的按钮名，不调用模型，也不处理真实图片。

## 改内容，再改文件名

两种实现一开始读到的都是 `screen.txt`，内容为 `button=save`。左边用文件名作为缓存键，右边用完整内容。

{{CACHE_DEMO}}

先点“更新内容，保留文件名”。按钮已经变成 `cancel`，左边却仍可能返回 `save`：它发现文件名没变，就直接取出了上次的结果。

再点“只换文件名”。按路径缓存的实现会重新计算，按内容缓存的实现可以继续用上次的结果，因为内容没有变化。点“重置”可以从头再试。

## 错误是怎样产生的

把按文件名缓存的逻辑写成 Python，就是下面这样。`encode` 只解析字符串，不是模型的图像编码器。

```python
cache = {}

def encode(content):
    return content.split("=", 1)[1]

def by_path(path, content):
    if path not in cache:
        cache[path] = encode(content)
    return cache[path]

assert by_path("screen.txt", "button=save") == "save"
assert by_path("screen.txt", "button=cancel") == "save"
```

第二个断言会通过，但通过的恰好是一个错误结果：文件名相同，函数就跳过了新内容，返回旧值。

## 把内容放进缓存键

这个小实验可以直接用完整字符串作键。实际系统通常使用字节摘要，省去在键里保存整个输入的开销。会影响结果的处理条件也要考虑进去，例如这里的编码器版本。

```python
from hashlib import sha256

cache = {}

def by_content(content, encoder_version="demo-v1"):
    raw = content.encode("utf-8")
    key = (sha256(raw).hexdigest(), encoder_version)
    if key not in cache:
        cache[key] = content.split("=", 1)[1]
    return cache[key]

assert by_content("button=save") == "save"
assert by_content("button=cancel") == "cancel"
```

计算摘要和处理内容要用同一份读入的字节。如果先算摘要，再重新打开文件，而文件恰好在中途变了，就会把新内容的结果存到旧内容的键下面。

## 两道自检题

1. 内容相同，文件名不同，哪一种缓存更容易复用？
2. 输入字节没变，但模型版本或预处理配置改变，能直接复用旧结果吗？

第一题，按内容缓存可以复用结果；按路径缓存会把新名字当成新输入。第二题，不能仅凭字节相同就复用。模型版本、预处理和精度等条件也可能改变结果，需要一并考虑是否放入缓存键。

## 回到真实系统

这个演示只说明缓存键怎样影响结果，无法给出模型提速或准确率的结论。在真实系统里，还要检查数值容差、并发时结果有没有绑定到正确请求，以及缓存容量和失效策略。

接下来的[截图缓存对照实验](/blog/image-cache-identity/)记录了另一个问题：分类结果正确时，数值检查仍可能不通过。

本文和交互示例使用 AI 编程工具辅助编写，已按页面里的步骤验证。
