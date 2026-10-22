"""CLI Crescent — jalankan file / -e / REPL, plus mode debug."""
import argparse
import sys

from . import __version__


def build_parser():
    ap = argparse.ArgumentParser(
        prog="crescent",
        description="Bahasa Crescent — lexer, parser, compiler bytecode, VM "
                    "(100% Python stdlib).",
    )
    ap.add_argument("file", nargs="?", help="file .cres untuk dijalankan")
    ap.add_argument("-e", "--eval", metavar="KODE",
                    help="evaluasi kode dari string")
    ap.add_argument("--tokens", action="store_true",
                    help="tampilkan token lalu keluar (debug)")
    ap.add_argument("--ast", action="store_true",
                    help="tampilkan AST lalu keluar (debug)")
    ap.add_argument("--bytecode", action="store_true",
                    help="tampilkan bytecode lalu keluar (debug)")
    ap.add_argument("--version", action="store_true",
                    help="tampilkan versi")
    return ap


def read_source(args):
    if args.eval is not None:
        return args.eval
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    return None


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.version:
        print("crescent {0}".format(__version__))
        return 0

    source = read_source(args)
    if source is None:
        from .repl import repl
        return repl()

    from .errors import CrescentError
    try:
        if args.tokens:
            from .lexer import tokenize
            for t in tokenize(source):
                print("{0:4} {1:<10} {2!r}".format(t.line, t.type, t.value))
            return 0
        if args.ast:
            from .parser import parse
            program = parse(source)
            for s in program.stmts:
                print(s)
            return 0

        from .compiler import compile_source
        fn = compile_source(source)

        if args.bytecode:
            from .dis import disassemble_function
            print(disassemble_function(fn))
            return 0

        from .vm import VM
        vm = VM()
        vm.run_function(fn)
    except CrescentError as e:
        print(str(e), file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print("file tidak ditemukan: {0}".format(e), file=sys.stderr)
        return 1
    return 0
