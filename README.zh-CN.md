# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · **简体中文** · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> 一门小巧的动态语言：**词法器 → 解析器 → 字节码编译器 → 虚拟机** —— 从零构建，100% Python 标准库，零依赖。

Crescent 是一份可读性很强的「编程语言如何工作」研究：每个阶段 —— 词法、AST、16 位字节码、基于 cell 的帧、闭包 —— 全部手写。语言本身也很好用：真正的闭包、字面量数据结构、函数式标准库（map/filter/reduce/sort）、交互式 REPL，以及带位置信息的错误提示。

## 特性

- **完整流水线** —— 词法器、解析器、字节码编译器、虚拟机（38 个操作码）
- **真闭包** —— 基于 cell 的捕获，循环变量每次迭代独立
- **函数式标准库** —— 带比较器的 map / filter / reduce / sort（32 个内建）
- **REPL + 反汇编器** —— --tokens / --ast / --bytecode 调试标志
- **140 个测试全绿** —— 词法、解析、虚拟机、REPL、CLI + 确定性示例
- **零依赖** —— 100% Python 标准库（3.8+），复制文件夹即用

## 快速开始

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## 许可证

MIT — see [LICENSE](LICENSE).

---

*本翻译仅覆盖要点，完整文档请参见[英文 README](README.md)。*
