# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · **Português** · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> Uma pequena linguagem dinâmica com **lexer → parser → compilador bytecode → máquina virtual** — construída do zero, 100% stdlib do Python, zero dependências.

Crescent é um estudo legível de como linguagens de programação funcionam: cada etapa — tokens, AST, bytecode de 16 bits, frames com células, closures — foi escrita à mão. A linguagem também é agradável: closures de verdade, estruturas literais, uma stdlib funcional (map/filter/reduce/sort), um REPL interativo e erros com posição exata.

## Características

- **Pipeline completo** — lexer, parser, compilador bytecode, VM (38 opcodes)
- **Closures de verdade** — capturas por células, variáveis de loop por iteração
- **Stdlib funcional** — map / filter / reduce / sort com comparadores (32 builtins)
- **REPL + desassemblador** — flags --tokens / --ast / --bytecode
- **140 testes verdes** — lexer, parser, VM, REPL, CLI + exemplos determinísticos
- **Zero dependências** — 100% stdlib Python (3.8+), basta copiar a pasta

## Início rápido

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## Licença

MIT — see [LICENSE](LICENSE).

---

*Esta tradução cobre o essencial. Veja o [README em inglês](README.md) para a documentação completa.*
