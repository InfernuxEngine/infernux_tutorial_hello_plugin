# Infernux 教程：Hello Plugin

[插件编写教程](https://infernux-engine.com/learn/plugin-authoring.html)的最小示例。
在 Editor Play 和导出的 Player 中读取包内文本资源，并添加支持中英文的 Editor 面板。
引擎要求 >=0.4.1,<0.5；reference 为 `chenlizheme/tutorial_hello_plugin`。

运行 `python package.py build dist/plugin.inxpkg` 打包。
运行 `python .infernux-dev/validate.py` 和 `python -m unittest discover -s tests` 检查。
保留官方模板的工作流，由版本 tag 发布不可覆盖的归档及 release 元信息。
0.1.11 更新消息资源，已有资产 GUID 保持不变。本示例不加入官方插件目录。
