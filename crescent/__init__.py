"""Crescent — bahasa kecil dengan lexer, parser, compiler bytecode, dan VM.

Pintasan umum: ``run_source(src)`` mengompilasi sekaligus menjalankan sumber.
"""
from .compiler import compile_source
from .errors import (CrescentCompileError, CrescentError,
                     CrescentRuntimeError, CrescentSyntaxError)
from .lexer import tokenize
from .parser import parse
from .values import ObjClosure, ObjFunction, ObjNative

__version__ = "0.1.0"

__all__ = [
    "VM", "compile_source", "run_source", "parse", "tokenize",
    "CrescentError", "CrescentSyntaxError", "CrescentCompileError",
    "CrescentRuntimeError", "ObjFunction", "ObjClosure", "ObjNative",
    "__version__",
]


def run_source(source, vm=None, print_fn=None, repl=False):
    """Kompilasi + jalankan sumber.

    Return tuple ``(nilai_akhir, vm)``. Kesalahan Crescent dilempar sebagai
    exception — pemanggil menangkap dan memformatnya.
    """
    if vm is None:
        from .vm import VM
        vm = VM(print_fn=print_fn)
    elif print_fn is not None:
        vm.print_fn = print_fn
    fn = compile_source(source, repl=repl)
    value = vm.run_function(fn)
    return value, vm
