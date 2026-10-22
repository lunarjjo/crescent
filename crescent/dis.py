"""Disassembler Crescent — cetak bytecode dalam bentuk terbaca manusia.

Dipakai CLI (``crescent --bytecode file.cres``) dan untuk debugging.
"""
from .compiler import OP, OPNAMES


def disassemble(chunk, name="script"):
    lines = []
    lines.append("== {0} ({1} instruksi, {2} konstanta) ==".format(
        name, len(chunk.code), len(chunk.consts)))
    ip = 0
    code = chunk.code
    n = len(code)
    while ip < n:
        op = code[ip]
        name_op = OPNAMES[op] if op < len(OPNAMES) else "?{0}".format(op)
        line = chunk.lines[ip]
        prefix = "{0:4d} L{1:<3} {2:<14}".format(ip, line, name_op)

        if name_op == "CLOSURE":
            cidx = (code[ip + 1] << 8) | code[ip + 2]
            nup = (code[ip + 3] << 8) | code[ip + 4]
            detail = "fn #{0} ({1} upvalue)".format(cidx, nup)
            width = 5
            for _ in range(nup):
                is_local = (code[ip + width] << 8) | code[ip + width + 1]
                idx = (code[ip + width + 2] << 8) | code[ip + width + 3]
                tag = "local" if is_local else "upval"
                detail += " [{0}:{1}]".format(tag, idx)
                width += 4
            lines.append(prefix + detail)
            ip += width
            continue

        if name_op in ("CONST", "DEFINE_GLOBAL", "GET_GLOBAL", "SET_GLOBAL"):
            idx = (code[ip + 1] << 8) | code[ip + 2]
            val = chunk.consts[idx] if idx < len(chunk.consts) else "?"
            if isinstance(val, str):
                show = '"{0}"'.format(val)
            else:
                show = repr(val)
            lines.append(prefix + "#{0} = {1}".format(idx, show))
            ip += 3
        elif name_op in ("GET_LOCAL", "SET_LOCAL", "GET_UPVAL", "SET_UPVAL",
                         "SCOPE_END"):
            idx = (code[ip + 1] << 8) | code[ip + 2]
            lines.append(prefix + str(idx))
            ip += 3
        elif name_op in ("JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"):
            off = (code[ip + 1] << 8) | code[ip + 2]
            lines.append(prefix + "-> {0}".format(ip + 3 + off))
            ip += 3
        elif name_op == "LOOP":
            off = (code[ip + 1] << 8) | code[ip + 2]
            lines.append(prefix + "-> {0}".format(ip + 3 - off))
            ip += 3
        elif name_op in ("PRINT_N", "ARRAY", "MAP", "CALL"):
            cnt = (code[ip + 1] << 8) | code[ip + 2]
            lines.append(prefix + str(cnt))
            ip += 3
        else:
            lines.append(prefix)
            ip += 1

    if chunk.consts:
        lines.append("-- konstanta --")
        for i, c in enumerate(chunk.consts):
            if hasattr(c, "chunk"):
                lines.append("  #{0} = fungsi {1}".format(i, c))
            else:
                lines.append("  #{0} = {1!r}".format(i, c))
    return "\n".join(lines)


def disassemble_function(fn):
    out = [disassemble(fn.chunk, fn.name or "<script>")]
    for c in fn.chunk.consts:
        if hasattr(c, "chunk"):
            out.append(disassemble_function(c))
    return "\n".join(out)
