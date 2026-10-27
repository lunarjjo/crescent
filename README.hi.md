# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · **हिन्दी**</sub>

</div>

> एक छोटी डायनामिक भाषा — **lexer → parser → bytecode कंपाइलर → वर्चुअल मशीन** — बिल्कुल शुरू से बनी, 100% Python stdlib, शून्य डिपेंडेंसी।

Crescent यह समझने की एक पढ़ने-योग्य पढ़ाई है कि प्रोग्रामिंग भाषाएँ कैसे काम करती हैं: हर चरण — टोकन, AST, 16-बिट bytecode, cell-आधारित फ़्रेम, closures — हाथ से लिखा गया। भाषा भी अच्छी है: असली closures, लिटरल डेटा संरचनाएँ, फंक्शनल stdlib (map/filter/reduce/sort), इंटरैक्टिव REPL और स्थिति-सहित त्रुटि संदेश।

## विशेषताएँ

- **पूरा पाइपलाइन** — lexer, parser, bytecode कंपाइलर, VM (38 opcodes)
- **असली closures** — cell-आधारित कैप्चर, हर इटरेशन का अपना लूप वेरिएबल
- **फंक्शनल stdlib** — comparator के साथ map / filter / reduce / sort (32 builtins)
- **REPL + disassembler** — --tokens / --ast / --bytecode फ़्लैग
- **140 टेस्ट हरे** — lexer, parser, VM, REPL, CLI + डिटरमिनिस्टिक उदाहरण
- **शून्य डिपेंडेंसी** — 100% Python stdlib (3.8+), बस फ़ोल्डर कॉपी करें

## त्वरित शुरुआत

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## लाइसेंस

MIT — see [LICENSE](LICENSE).

---

*यह अनुवाद केवल मुख्य बातें देता है। पूरे दस्तावेज़ के लिए [अंग्रेज़ी README](README.md) देखें।*
