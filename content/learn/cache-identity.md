这节课只回答一个问题：**缓存凭什么认为，这次输入和上一次是同一个输入？** 你会在浏览器里看到一个可重复的错误，再通过改变缓存键消除它。

不需要安装软件。下面的“编码器”只是读取虚构文本中的按钮名，不调用模型，也不处理真实图片。

## 先运行，再猜一次

两种实现最初都读到 `screen.txt`，内容为 `button=save`。左边按文件名保存结果，右边按完整内容保存结果。

{{CACHE_DEMO}}

先点击“更新内容，保留文件名”。预期按钮已经变成 `cancel`，左边却仍可能返回 `save`。原因是缓存检查了名字，没有检查内容。

再点击“只换文件名”。这次按路径的缓存会重新计算；按内容的缓存可以继续复用，因为实际内容没有变化。点“重置”即可重复这两个步骤。

## 错误是怎样产生的

下面是机制示意。`encode` 只解析字符串，不是模型的图像编码器。

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

第二个断言描述的是这个实现的错误行为。文件名相同，让它跳过了对新内容的处理。

## 用实际内容确定身份

在这个小实验里，完整字符串足以作为键。工程里通常用字节摘要，避免把整个输入放进键，但还需要把会影响结果的处理条件一起考虑。

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

关键是**对同一份实际读入的字节计算摘要并处理**。如果先算摘要、之后再次打开一个会变化的文件，仍可能发生摘要与处理内容错位。

## 两道自检题

1. 内容相同，文件名不同，哪一种缓存更容易复用？
2. 输入字节没变，但模型版本或预处理配置改变，能直接复用旧结果吗？

第一题：按内容保存结果的缓存可以复用；按路径保存的实现会把新名字当成新输入。第二题：不能仅凭字节相同判断。影响计算结果的模型版本、预处理、精度等条件，也可能需要进入缓存身份。

## 回到真实系统

这个演示验证的是缓存键的语义，没有给出任何模型提速或准确率结论。真实系统还要检查数值容差、并发下的请求绑定、缓存容量与失效策略。

接着阅读[截图缓存对照实验](/blog/image-cache-identity/)，看看“分类正确”为什么还不等于“数值检查通过”。

本文与交互示例使用 AI 编程工具辅助编写，并按页面所示步骤验证。
