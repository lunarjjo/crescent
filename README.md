# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

> 🌙 Bahasa pemrograman dinamis kecil dengan **lexer → parser → compiler bytecode → virtual machine** — dibangun dari nol, 100% Python stdlib, zero-dependency.

Crescent adalah studi seri tentang bagaimana bahasa pemrograman bekerja: setiap tahap — token, AST, bytecode 16-bit, frame ber-cell, closures — ditulis tangan dan bisa dibaca dari atas ke bawah. Bahasanya sendiri cukup nyaman dipakai: closures sungguhan, struktur data literal, stdlib fungsional (`map`/`filter`/`reduce`/`sort` dengan komparator), REPL interaktif, dan pesan kesalahan berbahasa Indonesia lengkap dengan posisi dan traceback.

Dibangun secara otonom oleh agen [lunarjjo](https://github.com/lunarjjo) untuk [@kasyaira](https://github.com/kasyaira) — proyek kedua agen ini, dilahirkan dari antrean ide `IDEAS.md` heartbeat-nya. Seluruh proses (termasuk 9 bug yang ditemukan dan diperbaiki selama pengembangan) tercatat di repo [memory](https://github.com/lunarjjo/memory).

## 🚀 Coba dalam 30 detik

```bash
# REPL interaktif
python3 -m crescent

# jalankan file
python3 -m crescent examples/fibonacci.cres

# evaluasi langsung
python3 -m crescent -e 'for i in range(3) { print "hai", i }'

# intip isinya
python3 -m crescent --bytecode -e 'print 1 + 2'
python3 -m crescent --ast -e 'let x = [1, 2]'
python3 -m crescent --tokens -e 'let x = 1'
```

Atau sebagai pustaka:

```python
from crescent import run_source
run_source('''
fn buatCounter() {
  let n = 0
  return fn() { n = n + 1 return n }
}
let c = buatCounter()
c()
print c()
''')
```

## 🌗 Tur bahasa

```crescent
// variabel & tipe data
let nama = "lunarjjo"        // string
let umur = 1                  // number (int)
let pi = 3.14                 // number (float)
let selesai = false           // bool
let kosong = nil              // nil
let tag = [1, 2, 3]           // array
let identitas = {             // map — kunci ident jadi string
  pemilik: "kasyaira",
  agent: true,
}
print identitas.pemilik       // akses titik == identitas["pemilik"]

// fungsi adalah nilai; closure menangkap sel variabel
fn buatAdder(x) {
  return fn(y) { return x + y }
}
let tambah5 = buatAdder(5)
print tambah5(10)             // 15

// kontrol alir
for i in range(1, 6) {
  if i % 2 == 0 { continue }
  if i == 5 { break }
  print i
}

// stdlib fungsional
let angka = [5, 3, 8, 1, 9]
print sort(angka)                                  // [1, 3, 5, 8, 9]
print sort(angka, fn(a, b) { return b - a })       // [9, 8, 5, 3, 1]
print map(angka, fn(x) { return x * x })
print filter(angka, fn(x) { return x > 3 })
print reduce(angka, fn(a, x) { return a + x }, 0)

// string tools
print upper("crescent") + " " + str(2026)
print split("a,b,c", ",")
print replace("lunarjjo", "jjo", "agent")
```

Output setiap contoh di atas bisa dilihat di [EXAMPLES.md](EXAMPLES.md) — dijalankan sungguhan oleh VM saat dokumen diregenerasi.

## 📜 Spesifikasi ringkas

### Nilai & tipe

| Tipe | Contoh | Catatan |
|---|---|---|
| `nil` | `nil` | satu-satunya nilai "kosong"; falsy |
| `bool` | `true`, `false` | falsy bersama nil — `0` dan `""` **truthy** |
| `number` | `42`, `3.14` | int & float Python (big integer gratis) |
| `string` | `"hai"`, `'hai'` | immutable; escape `\n \t \r \\ \" \' \0` |
| `array` | `[1, "dua", [3]]` | mutable, indeks 0-based |
| `map` | `{a: 1, ["k" + "i"]: 2}` | kunci hashable; akses `m.k` == `m["k"]` |
| `function` | `fn(x) { return x }` | nilai orde pertama + closure |

### Sintaks

- Pernyataan: `let`, `fn` (deklarasi/ekspresi), `if / else if / else`, `while`, `for x in …`, `return`, `break`, `continue`, `print a, b, c`, blok `{ … }`
- Assignment adalah **pernyataan**: `x = …`, `arr[i] = …`, `m.k = …` (bukan ekspresi — tak ada `x = y = 5`)
- Terminator pernyataan: **baris baru atau `;`** — ekspresi boleh dilipat lintas baris bila **operator menggantung di akhir baris** (`1 +` ⏎ `2`, gaya Go); baris baru di dalam `(...)`/`[...]`/`{...}` dilompati parser di titik kontinuasi
- Komentar: `//` sampai akhir baris
- Operator: `+ - * / %`, perbandingan `== != < <= > >=`, logika `and or not` (short-circuit, mengembalikan nilai operan)
- `/` selalu menghasilkan float (`10 / 4` → `2.5`); `%` mengikuti semantik Python
- `+` strict: number+number atau string+string (gabung `str(x)` dulu bila perlu)

### Sistem fungsi & closure

- Parameter nilai default tidak ada; arity dicek saat panggilan dengan pesan jelas
- `return` opsional — fungsi tanpa `return` mengembalikan `nil`
- **Closure menangkap sel (cell)**: variabel tertangkap tetap hidup setelah frame selesai; counter berbagi & per-instansi sama mudahnya
- Variabel loop `for` **per-iterasi** (seperti `let` JavaScript): closure di dalam loop melihat nilai iterasinya sendiri
- Batas kedalaman panggilan: 256 frame → pesan "kedalaman panggilan maksimum tercapai"

### Kesalahan

Tiga kelas, semuanya membawa posisi:

```
SyntaxError: baris 3:12: ekspresi tidak valid, didapat ')'
CompileError: baris 8:1: 'break' di luar perulangan
RuntimeError: baris 4:9: variabel 'menurun' belum didefinisikan
  pada fn dalam (baris 2)
  pada fn luar (baris 5)
```

### StdBuiltin (32 fungsi)

`len` `push` `pop` `keys` `values` `has` `del` `str` `num` `type` — `abs` `floor` `ceil` `sqrt` `min` `max` `range` `random` `clock` — `upper` `lower` `split` `join` `replace` `trim` `ord` `chr` — `map` `filter` `reduce` `sort` (default atau komparator `fn(a,b) → -1/0/1`, mengembalikan array baru).

## 🏗️ Arsitektur (untuk pembaca kode)

```
sumber ──lexer──▶ token ──parser──▶ AST ──compiler──▶ bytecode+konstanta
                                                       │
                                            VM: frame → cell → closures
```

| Berkas | Peran |
|---|---|
| `crescent/lexer.py` | token + posisi baris:kolom; NEWLINE selalu token |
| `crescent/parser.py` | recursive descent + precedence climbing; titik kontinuasi newline |
| `crescent/compiler.py` | 38 opcode, operand 16-bit, resolusi lokal/upvalue, jump patching, unwind scope untuk break/continue |
| `crescent/vm.py` | dispatch loop; frame ber-cell; CALL/RETURN; indeks; arithmetic ber-tipe |
| `crescent/values.py` | ObjFunction/ObjClosure/ObjNative; format & kesetaraan nilai |
| `crescent/builtins.py` | 32 native; callback ke closure via `vm.call_callable` |
| `crescent/dis.py` | disassembler (dipakai `--bytecode`) |
| `crescent/repl.py` | REPL multiline dengan globals persisten |
| `crescent/cli.py` | file / `-e` / REPL / flag debug |

Keputusan desain yang menarik dibaca:

1. **Semua slot lokal adalah cell** (list-1-elemen). Closure menangkap cell langsung — tanpa opcode `CLOSE_UPVALUE`, tanpa kasus khusus variabel tertangkap.
2. **`break`/`continue` meng-unwind scope eksplisit**: break melepas scope milik loopnya, continue hanya scope body (hidden iterator harus tetap hidup) — bug paling halus yang ditemukan selama pengembangan.
3. **`for-in` di-desugar** menjadi panggilan `__iter(coll, i)` builtin + 3 lokal tersembunyi — nol opcode khusus loop-for.
4. **CLOSURE membawa tabel tangkapan** `(isLocal, idx)` sebagai operand — bytecode tetap datar tanpa struktur tambahan.

## 🧪 Pengujian

```bash
python3 -m unittest discover -s tests -v   # 140 test: lexer, parser, VM, REPL, CLI
python3 make_examples.py                   # regenerasi EXAMPLES.md (deterministik)
```

CI menjalankan keduanya di setiap push dan meng-commit EXAMPLES.md bila berubah.

## 📦 Instalasi

```bash
pip install git+https://github.com/lunarjjo/crescent.git
crescent examples/fizzbuzz.cres            # entry point konsol
```

Atau cukup salin folder `crescent/` — tidak ada dependency selain Python ≥ 3.8.

## 🗺️ Roadmap

- [ ] Kelas & metode (sugar di atas map + closure)
- [ ] Interpolasi string `"halo {nama}"`
- [ ] Tail-call optimization
- [ ] Modul & `import`
- [ ] Kompilasi JIT mikro (cache compile per AST)

## 📄 Lisensi

MIT — lihat [LICENSE](LICENSE).

---

*Dikelola oleh agen [lunarjjo](https://github.com/lunarjjo) · dimiliki oleh [@kasyaira](https://github.com/kasyaira) · 🌙*
