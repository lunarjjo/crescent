"""Integration test VM Crescent — jalankan program nyata, cek output & error."""
import unittest

from crescent import (CrescentCompileError, CrescentRuntimeError,
                      CrescentSyntaxError, run_source)


def run(src):
    """Jalankan sumber, kembalikan seluruh output print sebagai string."""
    out = []
    value, _vm = run_source(src, print_fn=out.append)
    return "\n".join(out), value


class TestAritmetika(unittest.TestCase):
    def test_precedensi(self):
        out, _ = run("print 1 + 2 * 3")
        self.assertEqual(out, "7")

    def test_kurung(self):
        out, _ = run("print (1 + 2) * 3")
        self.assertEqual(out, "9")

    def test_divisi_float(self):
        out, _ = run("print 10 / 4")
        self.assertEqual(out, "2.5")

    def test_modulo(self):
        out, _ = run("print 17 % 5")
        self.assertEqual(out, "2")

    def test_float_format(self):
        out, _ = run("print 2.0 + 1.5")
        self.assertEqual(out, "3.5")
        out, _ = run("print 4.0")
        self.assertEqual(out, "4.0")

    def test_negasi(self):
        out, _ = run("print -5 + 3")
        self.assertEqual(out, "-2")

    def test_bilangan_besar(self):
        out, _ = run("print 99999999999999999999 * 2")
        self.assertEqual(out, "199999999999999999998")

    def test_string_konkatenasi(self):
        out, _ = run('print "lunar" + "jjo"')
        self.assertEqual(out, "lunarjjo")

    def test_string_plus_number_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run('print "a" + 1')


class TestNilai(unittest.TestCase):
    def test_nil_dan_bool(self):
        out, _ = run("print nil, true, false")
        self.assertEqual(out, "nil true false")

    def test_truthiness_hanya_nil_false(self):
        out, _ = run("""
if 0 { print "nol truthy" }
if "" { print "string kosong truthy" }
if nil { print "tidak" } else { print "nil falsy" }
""")
        self.assertEqual(out.splitlines(),
                         ["nol truthy", "string kosong truthy", "nil falsy"])

    def test_persamaan_bool_vs_number(self):
        out, _ = run("print true == 1, 1 == 1, \"a\" == \"a\"")
        self.assertEqual(out, "false true true")

    def test_persamaan_array_struktural(self):
        out, _ = run("print [1, 2] == [1, 2], [1] == [1, 2]")
        self.assertEqual(out, "true false")

    def test_logika_short_circuit_nilai(self):
        out, _ = run('print nil or "default", "x" or "y", 1 and 2, nil and 2')
        self.assertEqual(out, "default x 2 nil")

    def test_perbandingan_string(self):
        out, _ = run('print "abc" < "abd", "b" >= "a"')
        self.assertEqual(out, "true true")

    def test_perbandingan_campuran_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run('print 1 < "a"')


class TestVariabel(unittest.TestCase):
    def test_let_global(self):
        out, _ = run("let x = 42\nprint x")
        self.assertEqual(out, "42")

    def test_let_tanpa_nilai(self):
        out, _ = run("let x\nprint x")
        self.assertEqual(out, "nil")

    def test_assignment(self):
        out, _ = run("let x = 1\nx = x + 9\nprint x")
        self.assertEqual(out, "10")

    def test_variabel_tak_terdefinisi_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run("print tidakada")

    def test_assignment_tak_terdefinisi_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run("x = 5")

    def test_shadowing_scope(self):
        out, _ = run("""
let x = 1
{
  let x = 2
  print x
}
print x
""")
        self.assertEqual(out.splitlines(), ["2", "1"])

    def test_redeklarasi_scope_sama_error(self):
        with self.assertRaises(CrescentCompileError):
            run("{ let x = 1\nlet x = 2 }")

    def test_redeklarasi_global_diperbolehkan(self):
        # seperti assignment Python — global boleh didefinisikan ulang
        out, _ = run("let x = 1\nlet x = 2\nprint x")
        self.assertEqual(out, "2")

    def test_semicolon_opsional(self):
        out, _ = run("let a = 1; let b = 2\nprint a + b")
        self.assertEqual(out, "3")


class TestKontrol(unittest.TestCase):
    def test_if_else(self):
        out, _ = run("""
let x = 10
if x > 5 { print "besar" } else { print "kecil" }
if x < 5 { print "a" } else if x == 10 { print "pas" } else { print "b" }
""")
        self.assertEqual(out.splitlines(), ["besar", "pas"])

    def test_while(self):
        out, _ = run("""
let i = 0
let total = 0
while i < 5 {
  total = total + i
  i = i + 1
}
print total
""")
        self.assertEqual(out, "10")

    def test_while_break_continue(self):
        out, _ = run("""
let i = 0
while true {
  i = i + 1
  if i % 2 == 0 { continue }
  if i > 7 { break }
  print i
}
""")
        self.assertEqual(out.splitlines(), ["1", "3", "5", "7"])

    def test_for_array(self):
        out, _ = run("for x in [10, 20, 30] { print x }")
        self.assertEqual(out.splitlines(), ["10", "20", "30"])

    def test_for_map(self):
        out, _ = run("""
let total = 0
for k in {a: 1, b: 2} { total = total + 1 }
print total
""")

    def test_for_string(self):
        out, _ = run("for c in \"abc\" { print c }")
        self.assertEqual(out.splitlines(), ["a", "b", "c"])

    def test_for_dengan_break_continue(self):
        out, _ = run("""
for x in [1, 2, 3, 4, 5] {
  if x == 2 { continue }
  if x == 5 { break }
  print x
}
""")
        self.assertEqual(out.splitlines(), ["1", "3", "4"])

    def test_loop_dalam_loop_break(self):
        out, _ = run("""
for x in [1, 2] {
  for y in [1, 2, 3] {
    if y == 2 { break }
    print x * 10 + y
  }
}
""")
        self.assertEqual(out.splitlines(), ["11", "21"])

    def test_break_di_luar_loop_error(self):
        with self.assertRaises(CrescentCompileError):
            run("break")


class TestFungsi(unittest.TestCase):
    def test_fungsi_dasar(self):
        out, _ = run("""
fn tambah(a, b) { return a + b }
print tambah(3, 4)
""")
        self.assertEqual(out, "7")

    def test_rekursi_fibonacci(self):
        out, _ = run("""
fn fib(n) {
  if n < 2 { return n }
  return fib(n - 1) + fib(n - 2)
}
print fib(20)
""")
        self.assertEqual(out, "6765")

    def test_return_implisit_nil(self):
        out, _ = run("""
fn f() { let x = 1 }
print f()
""")
        self.assertEqual(out, "nil")

    def test_arity_error(self):
        with self.assertRaises(CrescentRuntimeError) as ctx:
            run("fn f(a, b) { return a }\nf(1)")
        self.assertIn("mengharapkan 2", str(ctx.exception))

    def test_return_di_script_error(self):
        with self.assertRaises(CrescentCompileError):
            run("return 1")

    def test_fungsi_sebagai_nilai(self):
        out, _ = run("""
fn buat(n) { return fn(x) { return x + n } }
let tambah5 = buat(5)
print tambah5(10)
""")
        self.assertEqual(out, "15")

    def test_closure_counter_berbagi(self):
        out, _ = run("""
fn buatCounter() {
  let n = 0
  return fn() {
    n = n + 1
    return n
  }
}
let c = buatCounter()
c()
c()
print c()
""")
        self.assertEqual(out, "3")

    def test_closure_per_instansi(self):
        out, _ = run("""
fn buatCounter() {
  let n = 0
  return fn() {
    n = n + 1
    return n
  }
}
let a = buatCounter()
let b = buatCounter()
a()
a()
print a(), b()
""")
        self.assertEqual(out, "3 1")

    def test_closure_per_iterasi(self):
        # seperti JS `let` — setiap iterasi menangkap sel sendiri
        out, _ = run("""
let fns = []
for i in [1, 2, 3] {
  push(fns, fn() { return i })
}
print fns[0](), fns[1](), fns[2]()
""")
        self.assertEqual(out, "1 2 3")

    def test_fungsi_lokal_rekursif(self):
        out, _ = run("""
fn luar() {
  fn faktorial(n) {
    if n <= 1 { return 1 }
    return n * faktorial(n - 1)
  }
  return faktorial(5)
}
print luar()
""")
        self.assertEqual(out, "120")

    def test_kedalaman_rekursi_error(self):
        with self.assertRaises(CrescentRuntimeError) as ctx:
            run("""
fn loop(x) { return loop(x + 1) }
loop(0)
""")
        self.assertIn("kedalaman", str(ctx.exception))

    def test_panggil_bukan_fungsi_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run("let x = 5\nx(1)")


class TestData(unittest.TestCase):
    def test_array_dasar(self):
        out, _ = run("let a = [1, 2, 3]\nprint a[0], a[2], len(a)")
        self.assertEqual(out, "1 3 3")

    def test_array_index_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run("let a = [1]\nprint a[5]")

    def test_array_set(self):
        out, _ = run("let a = [1, 2, 3]\na[1] = 99\nprint a")
        self.assertEqual(out, "[1, 99, 3]")

    def test_array_nested(self):
        out, _ = run("let m = [[1, 2], [3, 4]]\nprint m[1][0]")
        self.assertEqual(out, "3")

    def test_push_pop(self):
        out, _ = run("""
let a = []
push(a, 1)
push(a, 2)
let p = pop(a)
print a, p, len(a)
""")
        self.assertEqual(out, "[1] 2 1")

    def test_push_pop_semantik_referensi(self):
        # argumen dievaluasi kiri-ke-kanan seperti Python — aliasing terlihat
        out, _ = run("let a = [1, 2]\nprint a, pop(a)")
        self.assertEqual(out, "[1] 2")

    def test_map_dasar(self):
        out, _ = run('let m = {nama: "lunarjjo", umur: 1}\nprint m["nama"]')
        self.assertEqual(out, "lunarjjo")

    def test_map_missing_nil(self):
        out, _ = run('let m = {}\nprint m["tidakada"]')
        self.assertEqual(out, "nil")

    def test_map_set_get(self):
        out, _ = run("""
let m = {a: 1}
m["b"] = 2
m["a"] = 10
print m
""")
        self.assertEqual(out, '{"a": 10, "b": 2}')

    def test_map_keys_values_has_del(self):
        out, _ = run("""
let m = {x: 1, y: 2}
print len(m), has(m, "x"), has(m, "z")
del(m, "x")
print len(m), keys(m), values(m)
""")
        self.assertEqual(out.splitlines(),
                         ['2 true false', '1 ["y"] [2]'])

    def test_map_kunci_hitung(self):
        out, _ = run('let m = {[1 + 1]: "dua"}\nprint m[2]')
        self.assertEqual(out, "dua")

    def test_string_index(self):
        out, _ = run('let s = "crescent"\nprint s[0], len(s)')
        self.assertEqual(out, "c 8")

    def test_string_immutable_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run('let s = "abc"\ns[0] = "z"')


class TestBuiltin(unittest.TestCase):
    def test_str_num_type(self):
        out, _ = run("""
print str(12) + "!", num("42") + 1, type(1.5), type("a"), type([1]), type({})
""")
        self.assertEqual(out, "12! 43 number string array map")

    def test_min_max_abs_floor_ceil_sqrt(self):
        out, _ = run("""
print min(3, 1, 2), max(3, 1, 2), abs(-5), floor(2.7), ceil(2.1), sqrt(16)
""")
        self.assertEqual(out, "1 3 5 2 3 4.0")

    def test_range(self):
        out, _ = run("print range(3), range(1, 4), range(10, 0, -3)")
        self.assertEqual(out, "[0, 1, 2] [1, 2, 3] [10, 7, 4, 1]")

    def test_string_tools(self):
        out, _ = run("""
print upper("crescent"), lower("LUNA")
print split("a,b,c", ","), join(["x", "y"], "-")
print replace("lunarjjo", "jjo", "agent"), trim("  hi  ")
""")
        self.assertEqual(out.splitlines(),
                         ["CRESCENT luna",
                          '["a", "b", "c"] x-y',
                          "lunaragent hi"])

    def test_ord_chr(self):
        out, _ = run('print ord("a"), chr(98)')
        self.assertEqual(out, "97 b")

    def test_map_fn(self):
        out, _ = run("print map([1, 2, 3], fn(x) { return x * 2 })")
        self.assertEqual(out, "[2, 4, 6]")

    def test_filter_fn(self):
        out, _ = run("print filter([1, 2, 3, 4], fn(x) { return x % 2 == 0 })")
        self.assertEqual(out, "[2, 4]")

    def test_reduce_fn(self):
        out, _ = run("print reduce([1, 2, 3, 4], fn(a, x) { return a + x }, 0)")
        self.assertEqual(out, "10")

    def test_sort_default_dan_comparator(self):
        out, _ = run("""
print sort([3, 1, 2])
print sort(["pisang", "ape"], fn(a, b) { return len(a) - len(b) })
""")
        self.assertEqual(out.splitlines(), ['[1, 2, 3]', '["ape", "pisang"]'])

    def test_sort_tidak_mutasi(self):
        out, _ = run("let a = [3, 1]\nlet b = sort(a)\nprint a, b")
        self.assertEqual(out, "[3, 1] [1, 3]")

    def test_builtin_type_error(self):
        with self.assertRaises(CrescentRuntimeError):
            run('len(5)')

    def test_clock_random(self):
        out, _ = run("print type(clock()), type(random())")
        self.assertEqual(out, "number number")


class TestKesalahanPosisi(unittest.TestCase):
    def test_error_baris_sesuai(self):
        with self.assertRaises(CrescentRuntimeError) as ctx:
            run("let a = 1\nlet b = 2\nprint tidakada")
        self.assertIn("baris 3", str(ctx.exception))

    def test_traceback_fungsi(self):
        with self.assertRaises(CrescentRuntimeError) as ctx:
            run("""
fn dalam() { return tidakada }
fn luar() { return dalam() }
luar()
""")
        self.assertIn("fn dalam", str(ctx.exception))
        self.assertIn("fn luar", str(ctx.exception))

    def test_syntax_error_posisi(self):
        with self.assertRaises(CrescentSyntaxError) as ctx:
            run("let x = ")
        self.assertIn("baris 1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
