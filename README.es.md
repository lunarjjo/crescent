# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · **Español** · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> Un pequeño lenguaje dinámico con **lexer → parser → compilador de bytecode → máquina virtual** — construido desde cero, 100% stdlib de Python, sin dependencias.

Crescent es un estudio legible de cómo funcionan los lenguajes de programación: cada etapa — tokens, AST, bytecode de 16 bits, frames con celdas, closures — está escrita a mano. El lenguaje también es agradable: closures reales, estructuras literales, una stdlib funcional (map/filter/reduce/sort), un REPL interactivo y errores con posición exacta.

## Características

- **Pipeline completo** — lexer, parser, compilador bytecode, VM (38 opcodes)
- **Closures reales** — capturas por celdas, variables de bucle por iteración
- **Stdlib funcional** — map / filter / reduce / sort con comparadores (32 builtins)
- **REPL + desensamblador** — flags --tokens / --ast / --bytecode
- **140 tests en verde** — lexer, parser, VM, REPL, CLI + ejemplos deterministas
- **Sin dependencias** — 100% stdlib de Python (3.8+), solo copia la carpeta

## Inicio rápido

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## Licencia

MIT — see [LICENSE](LICENSE).

---

*Esta traducción cubre lo esencial. Consulta el [README en inglés](README.md) para la documentación completa.*
