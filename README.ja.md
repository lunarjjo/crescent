# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · **日本語** · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> 小さな動的言語 — **レキサー → パーサー → バイトコードコンパイラ → 仮想マシン**。ゼロから構築、100% Python 標準ライブラリ、依存関係ゼロ。

Crescent は、プログラミング言語の仕組みを読みやすく学べる研究プロジェクトです。各段階 — トークン、AST、16ビットバイトコード、セルベースのフレーム、クロージャ — すべて手書き。言語自体も快適：本物のクロージャ、リテラルデータ構造、関数型標準ライブラリ（map/filter/reduce/sort）、対話REPL、位置情報付きエラー。

## 特徴

- **完全パイプライン** — レキサー、パーサー、バイトコードコンパイラ、VM（38オペコード）
- **本物のクロージャ** — セルベースのキャプチャ、反復ごとのループ変数
- **関数型標準ライブラリ** — 比較関数付き map / filter / reduce / sort（32組込み）
- **REPL + 逆アセンブラ** — --tokens / --ast / --bytecode フラグ
- **140テスト成功** — レキサー、パーサー、VM、REPL、CLI + 決定論的サンプル
- **依存関係ゼロ** — 100% Python 標準ライブラリ（3.8+）、フォルダをコピーするだけ

## クイックスタート

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## ライセンス

MIT — see [LICENSE](LICENSE).

---

*この翻訳は要点のみをカバーしています。完全なドキュメントは [英語の README](README.md) を参照してください。*
