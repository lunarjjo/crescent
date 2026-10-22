"""REPL Crescent — interaktif, multiline, dengan globals persisten."""
from .compiler import compile_source
from .errors import CrescentError
from .vm import VM

PROMPT = "\U0001f319> "
CONT_PROMPT = ".... "


def needs_more(src):
    """True bila sumber belum lengkap (bracket terbuka / string menggantung)."""
    i = 0
    depth = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if c in ('"', "'"):
            quote = c
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    break
                i += 1
            if i >= n:
                return True  # string belum ditutup
            i += 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        i += 1
    return depth > 0


def repl(stdin=None, stdout=None):
    """Jalankan REPL. stdin/stdout bisa disuntik untuk pengujian."""
    import sys
    inp = stdin if stdin is not None else sys.stdin
    out = stdout if stdout is not None else sys.stdout
    vm = VM()
    buffer = []
    write = out.write
    write("Crescent REPL — ketik program, Ctrl-D/Ctrl-C untuk keluar\n")
    while True:
        try:
            line = inp.readline()
        except KeyboardInterrupt:
            write("\n")
            break
        if not line:
            write("\n")
            break
        stripped = line.strip()
        if not buffer and stripped in (".exit", ".quit", "exit", "quit"):
            break
        buffer.append(line)
        source = "".join(buffer)
        if needs_more(source):
            write(CONT_PROMPT if not source.endswith("\n") else ".... ")
            continue
        buffer = []
        source = source.rstrip()
        if not source.strip():
            continue
        try:
            fn = compile_source(source, repl=True)
            vm.run_function(fn)
        except CrescentError as e:
            write("{0}\n".format(e))
        except RecursionError:
            write("RecursionError: kedalaman host tercapai\n")
        except KeyboardInterrupt:
            write("\n(terputus)\n")
    return 0
