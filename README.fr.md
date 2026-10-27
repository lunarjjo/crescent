# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · **Français** · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> Un petit langage dynamique avec **lexer → parser → compilateur bytecode → machine virtuelle** — construit from scratch, 100% stdlib Python, zéro dépendance.

Crescent est une étude lisible du fonctionnement des langages : chaque étape — tokens, AST, bytecode 16 bits, frames à cellules, closures — est écrite à la main. Le langage est aussi agréable : de vraies closures, des structures littérales, une stdlib fonctionnelle (map/filter/reduce/sort), un REPL interactif et des erreurs positionnées.

## Caractéristiques

- **Pipeline complet** — lexer, parser, compilateur bytecode, VM (38 opcodes)
- **Vraies closures** — captures par cellules, variables de boucle par itération
- **Stdlib fonctionnelle** — map / filter / reduce / sort avec comparateurs (32 builtins)
- **REPL + désassembleur** — options --tokens / --ast / --bytecode
- **140 tests au vert** — lexer, parser, VM, REPL, CLI + exemples déterministes
- **Zéro dépendance** — 100% stdlib Python (3.8+), copiez juste le dossier

## Démarrage rapide

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## Licence

MIT — see [LICENSE](LICENSE).

---

*Cette traduction couvre l'essentiel. Voir le [README anglais](README.md) pour la documentation complète.*
