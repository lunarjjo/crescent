# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · **Русский** · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> Небольшой динамический язык: **лексер → парсер → компилятор байткода → виртуальная машина** — с нуля, 100% stdlib Python, без зависимостей.

Crescent — читаемое исследование того, как устроены языки программирования: каждый этап — токены, AST, 16-битный байткод, cell-фреймы, замыкания — написан вручную. Сам язык приятен: настоящие замыкания, литеральные структуры, функциональная stdlib (map/filter/reduce/sort), интерактивный REPL и ошибки с точной позицией.

## Возможности

- **Полный конвейер** — лексер, парсер, компилятор байткода, ВМ (38 опкодов)
- **Настоящие замыкания** — cell-захваты, переменные цикла на каждую итерацию
- **Функциональная stdlib** — map / filter / reduce / sort с компараторами (32 встроенных)
- **REPL + дизассемблер** — флаги --tokens / --ast / --bytecode
- **140 зелёных тестов** — лексер, парсер, ВМ, REPL, CLI + детерминированные примеры
- **Без зависимостей** — 100% stdlib Python (3.8+), просто скопируйте папку

## Быстрый старт

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## Лицензия

MIT — see [LICENSE](LICENSE).

---

*Этот перевод описывает самое главное. Полная документация — в [английском README](README.md).*
