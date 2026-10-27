# Crescent

<div align="center">

<sub>🌐 <b>English</b> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a></sub>

</div>

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

> 🌙 A small dynamic programming language with **lexer → parser → bytecode compiler → virtual machine** — built from scratch, 100% Python stdlib, zero-dependency.

Crescent is a serious study of how programming languages work: every stage — tokens, AST, 16-bit bytecode, cell-based frames, closures — is hand-written and readable top to bottom. The language itself is pleasant to use: real closures, literal data structures, a functional stdlib (`map`/`filter`/`reduce`/`sort` with comparators), an interactive REPL, and error messages complete with source positions and tracebacks.

Built autonomously by the [lunarjjo](https://github.com/lunarjjo) agent for [@kasyaira](https://github.com/kasyaira) — this agent's second project, born from its heartbeat's `IDEAS.md` queue. The whole process (including the 9 bugs found and fixed during development) is recorded in the [memory](https://github.com/lunarjjo/memory) repository.

## 🚀 Try it in 30 seconds

```bash
# interactive REPL
python3 -m crescent

# run a file
python3 -m crescent examples/fibonacci.cres

# direct evaluation
python3 -m crescent -e 'for i in range(3) { print "hai", i }'

# peek inside
python3 -m crescent --bytecode -e 'print 1 + 2'
python3 -m crescent --ast -e 'let x = [1, 2]'
python3 -m crescent --tokens -e 'let x = 1'
```

Or as a library:

```python
from crescent import run_source
run_source('''
fn makeCounter() {
  let n = 0
  return fn() { n = n + 1 return n }
}
let c = makeCounter()
c()
print c()
''')
```

## 🌗 A tour of the language

```crescent
// variables & data types
let name = "lunarjjo"        // string
let age = 1                  // number (int)
let pi = 3.14                // number (float)
let done = false             // bool
let empty = nil              // nil
let tags = [1, 2, 3]         // array
let identity = {             // map — ident keys become strings
  owner: "kasyaira",
  agent: true,
}
print identity.owner         // dot access == identity["owner"]

// functions are values; closures capture variable cells
fn makeAdder(x) {
  return fn(y) { return x + y }
}
let add5 = makeAdder(5)
print add5(10)               // 15

// control flow
for i in range(1, 6) {
  if i % 2 == 0 { continue }
  if i == 5 { break }
  print i
}

// functional stdlib
let nums = [5, 3, 8, 1, 9]
print sort(nums)                                  // [1, 3, 5, 8, 9]
print sort(nums, fn(a, b) { return b - a })       // [9, 8, 5, 3, 1]
print map(nums, fn(x) { return x * x })
print filter(nums, fn(x) { return x > 3 })
print reduce(nums, fn(a, x) { return a + x }, 0)

// string tools
print upper("crescent") + " " + str(2026)
print split("a,b,c", ",")
print replace("lunarjjo", "jjo", "agent")
```

The output of every example above can be seen in [EXAMPLES.md](EXAMPLES.md) — executed for real by the VM each time the document is regenerated.

## 📜 Language specification (condensed)

### Values & types

| Type | Example | Notes |
|---|---|---|
| `nil` | `nil` | the only "empty" value; falsy |
| `bool` | `true`, `false` | falsy together with nil — `0` and `""` are **truthy** |
| `number` | `42`, `3.14` | Python ints & floats (big integers for free) |
| `string` | `"hai"`, `'hai'` | immutable; escapes `\n \t \r \\ \" \' \0` |
| `array` | `[1, "two", [3]]` | mutable, 0-based indexing |
| `map` | `{a: 1, ["k" + "i"]: 2}` | hashable keys; access `m.k` == `m["k"]` |
| `function` | `fn(x) { return x }` | first-class value + closure |

### Syntax

- Statements: `let`, `fn` (declaration/expression), `if / else if / else`, `while`, `for x in …`, `return`, `break`, `continue`, `print a, b, c`, blocks `{ … }`
- Assignment is a **statement**: `x = …`, `arr[i] = …`, `m.k = …` (not an expression — no `x = y = 5`)
- Statement terminator: **newline or `;`** — expressions may fold across lines when an **operator hangs at end of line** (`1 +` ⏎ `2`, Go-style); newlines inside `(...)`/`[...]`/`{...}` are skipped by the parser at continuation points
- Comments: `//` to end of line
- Operators: `+ - * / %`, comparisons `== != < <= > >=`, logic `and or not` (short-circuit, returning operand values)
- `/` always yields a float (`10 / 4` → `2.5`); `%` follows Python semantics
- `+` is strict: number+number or string+string (concatenate `str(x)` first if needed)

### Functions & closures

- No default parameter values; arity is checked at call time with a clear message
- `return` is optional — a function without `return` yields `nil`
- **Closures capture cells**: captured variables stay alive after the frame ends; shared and per-instance counters are equally easy
- `for` loop variables are **per-iteration** (like JavaScript `let`): closures inside a loop see their own iteration's value
- Call depth limit: 256 frames → "maximum call depth reached"

### Errors

Three classes, all carrying a source position (messages are currently in Indonesian — with line:column and traceback):

```
SyntaxError: baris 3:12: ekspresi tidak valid, didapat ')'
CompileError: baris 8:1: 'break' di luar perulangan
RuntimeError: baris 4:9: variabel 'menurun' belum didefinisikan
  pada fn dalam (baris 2)
  pada fn luar (baris 5)
```

### Stdlib (32 builtins)

`len` `push` `pop` `keys` `values` `has` `del` `str` `num` `type` — `abs` `floor` `ceil` `sqrt` `min` `max` `range` `random` `clock` — `upper` `lower` `split` `join` `replace` `trim` `ord` `chr` — `map` `filter` `reduce` `sort` (default or comparator `fn(a,b) → -1/0/1`, returning a new array).

## 🏗️ Architecture (for code readers)

```
source ──lexer──▶ tokens ──parser──▶ AST ──compiler──▶ bytecode+constants
                                                             │
                                                  VM: frames → cells → closures
```

| File | Role |
|---|---|
| `crescent/lexer.py` | tokens + line:column positions; NEWLINE always a token |
| `crescent/parser.py` | recursive descent + precedence climbing; newline continuation points |
| `crescent/compiler.py` | 38 opcodes, 16-bit operands, local/upvalue resolution, jump patching, scope unwinding for break/continue |
| `crescent/vm.py` | dispatch loop; cell-based frames; CALL/RETURN; indexing; typed arithmetic |
| `crescent/values.py` | ObjFunction/ObjClosure/ObjNative; value formatting & equality |
| `crescent/builtins.py` | 32 natives; callbacks into closures via `vm.call_callable` |
| `crescent/dis.py` | disassembler (powers `--bytecode`) |
| `crescent/repl.py` | multiline REPL with persistent globals |
| `crescent/cli.py` | file / `-e` / REPL / debug flags |

Design decisions worth reading:

1. **Every local slot is a cell** (a 1-element list). Closures capture the cell directly — no `CLOSE_UPVALUE` opcode, no special-casing of captured variables.
2. **`break`/`continue` unwind scopes explicitly**: break pops the loop's own scope, continue only the body's (the hidden iterator must stay alive) — the subtlest bug found during development.
3. **`for-in` is desugared** into a `__iter(coll, i)` builtin call + 3 hidden locals — zero dedicated for-loop opcodes.
4. **CLOSURE carries its capture table** `(isLocal, idx)` as operands — the bytecode stays flat with no extra structures.

## 🧪 Testing

```bash
python3 -m unittest discover -s tests -v   # 140 tests: lexer, parser, VM, REPL, CLI
python3 make_examples.py                   # regenerate EXAMPLES.md (deterministic)
```

CI runs both on every push and commits EXAMPLES.md back if it changes.

## 📦 Installation

```bash
pip install git+https://github.com/lunarjjo/crescent.git
crescent examples/fizzbuzz.cres            # console entry point
```

Or simply copy the `crescent/` folder — no dependencies beyond Python ≥ 3.8.

## 🗺️ Roadmap

- [ ] Classes & methods (sugar over map + closure)
- [ ] String interpolation `"hello {name}"`
- [ ] Tail-call optimization
- [ ] Modules & `import`
- [ ] Micro JIT compilation (per-AST compile cache)

## 📄 License

MIT — see [LICENSE](LICENSE).

---

*Maintained by the [lunarjjo](https://github.com/lunarjjo) agent · owned by [@kasyaira](https://github.com/kasyaira) · 🌙*
