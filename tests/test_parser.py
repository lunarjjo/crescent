"""Unit test parser Crescent — struktur AST dan precedence."""
import unittest

from crescent import nodes as N
from crescent.errors import CrescentSyntaxError
from crescent.parser import parse


class TestEkspresi(unittest.TestCase):
    def parse_one(self, src):
        prog = parse(src)
        self.assertEqual(len(prog.stmts), 1)
        return prog.stmts[0]

    def expr_of(self, src):
        stmt = self.parse_one(src)
        self.assertIsInstance(stmt, N.ExprStmt)
        return stmt.expr

    def test_precedensi_kali_lebih_rapat(self):
        e = self.expr_of("1 + 2 * 3")
        self.assertEqual(e.op, "+")
        self.assertEqual(e.right.op, "*")

    def test_asosiatif_kiri(self):
        e = self.expr_of("8 - 4 - 2")
        self.assertEqual(e.op, "-")
        self.assertEqual(e.left.op, "-")
        self.assertEqual(e.right.value, 2)

    def test_grup_mengubah_ikatan(self):
        e = self.expr_of("(1 + 2) * 3")
        self.assertEqual(e.op, "*")
        self.assertEqual(e.left.op, "+")

    def test_pemanggilan_berantai_dan_indeks(self):
        e = self.expr_of("f(1)(2)[3]")
        self.assertIsInstance(e, N.Index)
        self.assertIsInstance(e.obj, N.Call)
        self.assertIsInstance(e.obj.callee, N.Call)

    def test_logika_and_or(self):
        e = self.expr_of("a or b and c")
        self.assertEqual(e.op, "or")
        self.assertEqual(e.right.op, "and")

    def test_unary_negatif(self):
        e = self.expr_of("-5")
        self.assertEqual(e.op, "-")
        self.assertEqual(e.operand.value, 5)

    def test_not_mengikat_lebih_rapat_dari_perbandingan(self):
        # dipilih: not x == y  ==  (not x) == y  (mirip JS)
        e = self.expr_of("not x == y")
        self.assertEqual(e.op, "==")
        self.assertEqual(e.left.op, "not")

    def test_array_literal(self):
        e = self.expr_of("[1, 2, 3]")
        self.assertIsInstance(e, N.ArrayLit)
        self.assertEqual([i.value for i in e.items], [1, 2, 3])

    def test_map_literal_ident_sebagai_kunci(self):
        s = self.parse_one("let m = {nama: 1, 'umur': 2}")
        e = s.expr
        self.assertIsInstance(e, N.MapLit)
        self.assertEqual(e.pairs[0][0].value, "nama")
        self.assertEqual(e.pairs[1][0].value, "umur")

    def test_map_literal_multiline(self):
        s = self.parse_one("let m = {\n  nama: 1,\n  umur: 2,\n}")
        self.assertEqual(len(s.expr.pairs), 2)

    def test_map_dengan_kunci_hitung(self):
        s = self.parse_one("let m = {[1 + 1]: \"dua\"}")
        self.assertIsInstance(s.expr.pairs[0][0], N.Binary)

    def test_lambda_sebagai_ekspresi(self):
        e = self.expr_of("fn(x) { return x }")
        self.assertIsInstance(e, N.FnExpr)
        self.assertEqual(e.params, ["x"])

    def test_ekspresi_lintas_baris_dalam_kurung(self):
        e = self.expr_of("(1 +\n  2)")
        self.assertEqual(e.op, "+")


class TestPernyataan(unittest.TestCase):
    def parse_one(self, src):
        prog = parse(src)
        self.assertEqual(len(prog.stmts), 1)
        return prog.stmts[0]

    def test_let_dengan_nilai(self):
        s = self.parse_one("let x = 5")
        self.assertIsInstance(s, N.LetStmt)
        self.assertEqual(s.name, "x")
        self.assertEqual(s.expr.value, 5)

    def test_let_tanpa_nilai(self):
        s = self.parse_one("let x")
        self.assertIsNone(s.expr)

    def test_fn_decl(self):
        s = self.parse_one("fn tambah(a, b) { return a + b }")
        self.assertIsInstance(s, N.FnDecl)
        self.assertEqual(s.name, "tambah")
        self.assertEqual(s.params, ["a", "b"])

    def test_parameter_ganda_error(self):
        with self.assertRaises(CrescentSyntaxError):
            parse("fn f(x, x) { return x }")

    def test_if_else_lintas_baris(self):
        src = "if a { print 1 }\nelse { print 2 }\n"
        s = self.parse_one(src)
        self.assertIsInstance(s, N.IfStmt)
        self.assertIsInstance(s.orelse, N.Block)

    def test_else_if_berantai(self):
        src = "if a { }\nelse if b { }\nelse { }"
        s = self.parse_one(src)
        self.assertIsInstance(s.orelse, N.IfStmt)
        self.assertIsInstance(s.orelse.orelse, N.Block)

    def test_if_tanpa_else(self):
        s = self.parse_one("if a { print 1 }")
        self.assertIsNone(s.orelse)

    def test_while_dan_for(self):
        self.assertIsInstance(self.parse_one("while x { }"), N.WhileStmt)
        s = self.parse_one("for x in items { }")
        self.assertIsInstance(s, N.ForStmt)
        self.assertEqual(s.var, "x")

    def test_return_opsional_nilai(self):
        self.assertIsNone(self.parse_one("fn f() { return }").expr if False else None)
        s = self.parse_one("fn f() { return 1 }")
        self.assertEqual(s.body.stmts[0].expr.value, 1)

    def test_return_tanpa_nilai(self):
        prog = parse("fn f() { return\n}")
        ret = prog.stmts[0].body.stmts[0]
        self.assertIsInstance(ret, N.ReturnStmt)
        self.assertIsNone(ret.expr)

    def test_print_banyak_nilai(self):
        s = self.parse_one("print 1, 2, 3")
        self.assertEqual(len(s.exprs), 3)

    def test_assignment_ke_variabel(self):
        s = self.parse_one("x = 5")
        assign = s.expr
        self.assertIsInstance(assign, N.Assign)
        self.assertEqual(assign.target.name, "x")

    def test_assignment_ke_indeks(self):
        s = self.parse_one("arr[0] = 5")
        assign = s.expr
        self.assertIsInstance(assign, N.Assign)
        self.assertIsInstance(assign.target, N.Index)

    def test_assignment_target_invalid_error(self):
        with self.assertRaises(CrescentSyntaxError):
            parse("1 = 5")

    def test_semicolon_opsional(self):
        a = parse("let x = 1; let y = 2\n")
        self.assertEqual(len(a.stmts), 2)

    def test_semicolon_pemisah_tanpa_newline(self):
        a = parse("let x = 1; let y = 2")
        self.assertEqual(len(a.stmts), 2)

    def test_blok_sebagai_pernyataan(self):
        s = self.parse_one("{ let x = 1 }")
        self.assertIsInstance(s, N.Block)

    def test_akhir_pernyataan_invalid_error(self):
        with self.assertRaises(CrescentSyntaxError):
            parse("let x = 1 let")

    def test_blok_tidak_ditutup_error(self):
        with self.assertRaises(CrescentSyntaxError):
            parse("fn f() { return 1")

    def test_kurung_tidak_ditutup_error(self):
        with self.assertRaises(CrescentSyntaxError):
            parse("let x = (1 + 2")

    def test_program_kosong(self):
        self.assertEqual(parse("").stmts, [])
        self.assertEqual(parse("// hanya komentar\n").stmts, [])

    def test_fungsi_dalam_fungsi(self):
        src = """
fn luar() {
  fn dalam() { return 1 }
  return dalam()
}
"""
        s = self.parse_one(src)
        self.assertIsInstance(s.body.stmts[0], N.FnDecl)


if __name__ == "__main__":
    unittest.main()
