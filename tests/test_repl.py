"""Test REPL Crescent — via subprocess, seperti pengalaman user nyata."""
import io
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_repl_script(lines):
    """Kirim baris-baris ke REPL lewat stdin; kembalikan output penuh."""
    proc = subprocess.run(
        [sys.executable, "-m", "crescent"],
        input="\n".join(lines) + "\n",
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    return proc.stdout, proc.stderr, proc.returncode


class TestREPL(unittest.TestCase):
    def test_ekspresi_auto_print(self):
        out, err, code = run_repl_script(["1 + 2 * 3"])
        self.assertEqual(code, 0)
        self.assertIn("7", out)

    def test_globals_persisten_antar_baris(self):
        out, err, code = run_repl_script([
            "let x = 42",
            "x + 1",
        ])
        self.assertEqual(code, 0)
        self.assertIn("43", out)

    def test_fungsi_multiline(self):
        out, err, code = run_repl_script([
            "fn fib(n) {",
            "  if n < 2 { return n }",
            "  return fib(n - 1) + fib(n - 2)",
            "}",
            "fib(10)",
        ])
        self.assertEqual(code, 0)
        self.assertIn("55", out)

    def test_array_multiline(self):
        out, err, code = run_repl_script([
            "let a = [1,",
            "  2,",
            "  3]",
            "len(a)",
        ])
        self.assertEqual(code, 0)
        self.assertIn("3", out)

    def test_error_tidak_mematikan_repl(self):
        out, err, code = run_repl_script([
            "print tidakada",
            "1 + 1",
        ])
        self.assertEqual(code, 0)
        self.assertIn("belum didefinisikan", out + err)
        self.assertIn("2", out)

    def test_perintah_keluar(self):
        out, err, code = run_repl_script([".exit"])
        self.assertEqual(code, 0)


class TestCLI(unittest.TestCase):
    def test_eval_flag(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "-e", 'print "halo" + " dunia"'],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "halo dunia")

    def test_error_exit_code(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "-e", "print tidakada"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("belum didefinisikan", proc.stderr)

    def test_flag_bytecode(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "--bytecode", "-e", "print 1"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("CONST", proc.stdout)
        self.assertIn("PRINT_N", proc.stdout)

    def test_flag_tokens(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "--tokens", "-e", "let x = 1"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("let", proc.stdout)

    def test_flag_ast(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "--ast", "-e", "print 1"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("PrintStmt", proc.stdout)

    def test_flag_version(self):
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "--version"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("crescent", proc.stdout)

    def test_file_program(self):
        with open(os.path.join(ROOT, "examples", "fizzbuzz.cres"),
                  encoding="utf-8") as f:
            src = f.read()
        proc = subprocess.run(
            [sys.executable, "-m", "crescent", "-e", src],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("FizzBuzz", proc.stdout)


if __name__ == "__main__":
    unittest.main()
