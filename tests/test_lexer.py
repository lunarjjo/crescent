"""Unit test lexer Crescent."""
import unittest

from crescent.errors import CrescentSyntaxError
from crescent.lexer import tokenize


def types(src):
    return [t.type for t in tokenize(src)]


class TestLexer(unittest.TestCase):
    def test_aritmetika_dasar(self):
        self.assertEqual(
            types("1 + 2 * 3"),
            ["NUMBER", "+", "NUMBER", "*", "NUMBER", "EOF"])

    def test_keyword_vs_ident(self):
        toks = tokenize("let bayar = true")
        self.assertEqual([t.type for t in toks],
                         ["let", "IDENT", "=", "true", "EOF"])

    def test_ident_mengandung_underscore_dan_digit(self):
        toks = tokenize("nilai_2")
        self.assertEqual(toks[0].type, "IDENT")

    def test_baris_baru_menghasilkan_token(self):
        self.assertEqual(types("a\nb"), ["IDENT", "NEWLINE", "IDENT", "EOF"])

    def test_baris_baru_selalu_jadi_token(self):
        # desain baru: lexer selalu emit NEWLINE; parser yang melompatinya
        self.assertEqual(
            types("f(1,\n  2)"),
            ["IDENT", "(", "NUMBER", ",", "NEWLINE", "NUMBER", ")", "EOF"])

    def test_komentar_diabaikan(self):
        self.assertEqual(
            types("// pesan\nx"), ["NEWLINE", "IDENT", "EOF"])

    def test_komentar_tidak_menelan_newline(self):
        self.assertEqual(
            types("a // trail\nb"),
            ["IDENT", "NEWLINE", "IDENT", "EOF"])

    def test_angka_int_dan_float(self):
        toks = tokenize("42 3.5 0.25")
        self.assertEqual([t.value for t in toks[:3]], [42, 3.5, 0.25])
        self.assertEqual(
            [type(v) for v in [t.value for t in toks[:3]]],
            [int, float, float])

    def test_titik_tanpa_digit_adalah_akses_properti(self):
        # sejak akses '.' ditambahkan: "1." = angka lalu operator titik
        self.assertEqual(
            types("1."),
            ["NUMBER", ".", "EOF"])

    def test_string_ganda_dan_tunggal(self):
        toks = tokenize('"a" \'b\'')
        self.assertEqual([t.value for t in toks[:2]], ["a", "b"])

    def test_string_escape(self):
        toks = tokenize(r'"a\nb\tc\\d\"e"')
        self.assertEqual(toks[0].value, 'a\nb\tc\\d"e')

    def test_escape_tak_dikenal_error(self):
        with self.assertRaises(CrescentSyntaxError):
            tokenize(r'"\q"')

    def test_string_tidak_ditutup_error(self):
        with self.assertRaises(CrescentSyntaxError):
            tokenize('"abc')

    def test_string_lintas_baris_error(self):
        with self.assertRaises(CrescentSyntaxError):
            tokenize('"abc\ndef"')

    def test_operator_dua_karakter(self):
        self.assertEqual(
            types("a == b != c <= d >= e"),
            ["IDENT", "==", "IDENT", "!=", "IDENT", "<=",
             "IDENT", ">=", "IDENT", "EOF"])

    def test_posisi_baris_kolom(self):
        toks = tokenize("a\n  bb")
        self.assertEqual((toks[2].line, toks[2].col), (2, 3))

    def test_karakter_tak_dikenal_error(self):
        with self.assertRaises(CrescentSyntaxError):
            tokenize("a @ b")

    def test_kurung_tak_seimbang_tidak_error_di_lexer(self):
        # lexer tidak memvalidasi keseimbangan — itu tugas parser
        self.assertEqual(types("(1"), ["(", "NUMBER", "EOF"])


if __name__ == "__main__":
    unittest.main()
