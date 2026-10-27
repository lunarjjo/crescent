# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · **Deutsch** · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> Eine kleine dynamische Sprache mit **Lexer → Parser → Bytecode-Compiler → Virtueller Maschine** — von Grund auf gebaut, 100% Python-stdlib, ohne Abhängigkeiten.

Crescent ist eine gut lesbare Studie darüber, wie Programmiersprachen funktionieren: jede Stufe — Tokens, AST, 16-Bit-Bytecode, Cell-Frames, Closures — ist handgeschrieben. Die Sprache selbst ist angenehm: echte Closures, literale Datenstrukturen, eine funktionale Stdlib (map/filter/reduce/sort), ein interaktives REPL und Fehlermeldungen mit Position.

## Funktionen

- **Komplette Pipeline** — Lexer, Parser, Bytecode-Compiler, VM (38 Opcodes)
- **Echte Closures** — Cell-basierte Captures, Schleifenvariablen pro Iteration
- **Funktionale Stdlib** — map / filter / reduce / sort mit Komparatoren (32 Builtins)
- **REPL + Disassembler** — Flags --tokens / --ast / --bytecode
- **140 grüne Tests** — Lexer, Parser, VM, REPL, CLI + deterministische Beispiele
- **Null Abhängigkeiten** — 100% Python-stdlib (3.8+), einfach den Ordner kopieren

## Schnellstart

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## Lizenz

MIT — see [LICENSE](LICENSE).

---

*Diese Übersetzung deckt das Wesentliche ab. Die vollständige Dokumentation findest du im [englischen README](README.md).*
