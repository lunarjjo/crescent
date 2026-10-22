"""Compiler Crescent — AST menjadi bytecode 16-bit untuk stack VM.

Desain penting:

- **Semuanya cell**: setiap slot lokal frame adalah list-1-elemen ``[nilai]``.
  Closure menangkap cell secara langsung, sehingga variabel yang ditangkap
  tetap hidup meski scope-nya sudah berakhir — tanpa opcode penutupan.
- **SCOPE_END n**: memotong n cell terakhir frame — keluar scope di runtime.
- **break/continue** meng-unwind scope secara eksplisit sebelum melompat.
- **for-in** di-desugar menjadi loop ``__iter`` + lokal tersembunyi
  ``__crescent_it / __crescent_i / __crescent_n``.
- Semua operand instruksi selebar 16-bit (2 byte, big-endian).
"""
from . import nodes as N
from .errors import CrescentCompileError
from .values import ObjFunction

# ---------------------------------------------------------------- opcodes

OPNAMES = [
    "CONST", "NIL", "TRUE", "FALSE", "POP",
    "DEFINE_GLOBAL", "GET_GLOBAL", "SET_GLOBAL",
    "GET_LOCAL", "SET_LOCAL", "LOCAL_INIT", "SCOPE_END",
    "GET_UPVAL", "SET_UPVAL",
    "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "LOOP",
    "EQUAL", "NOT_EQUAL", "LESS", "LESS_EQ", "GREATER", "GREATER_EQ",
    "ADD", "SUB", "MUL", "DIV", "MOD", "NOT", "NEG",
    "PRINT_N",
    "ARRAY", "MAP", "INDEX_GET", "INDEX_SET",
    "CALL", "CLOSURE", "RETURN",
]
OP = {name: i for i, name in enumerate(OPNAMES)}

# jumlah operand tetap per instruksi (CLOSURE variabel — ditangani khusus)
NARGS = {
    "CONST": 1, "DEFINE_GLOBAL": 1, "GET_GLOBAL": 1, "SET_GLOBAL": 1,
    "GET_LOCAL": 1, "SET_LOCAL": 1, "SCOPE_END": 1,
    "GET_UPVAL": 1, "SET_UPVAL": 1,
    "JUMP": 1, "JUMP_IF_FALSE": 1, "JUMP_IF_TRUE": 1, "LOOP": 1,
    "PRINT_N": 1, "ARRAY": 1, "MAP": 1, "CALL": 1,
}

IT, IX, INX = "__crescent_it", "__crescent_i", "__crescent_n"
ITER_FN = "__iter"


class Chunk:
    """Kumpulan bytecode + konstanta + pelacak baris."""

    def __init__(self):
        self.code = []
        self.consts = []
        self.lines = []

    def here(self):
        return len(self.code)

    def emit(self, name, line, *operands):
        self.code.append(OP[name])
        self.lines.append(line)
        for o in operands:
            self.code.append((o >> 8) & 0xFF)
            self.lines.append(line)
            self.code.append(o & 0xFF)
            self.lines.append(line)

    def patch(self, at, value):
        self.code[at] = (value >> 8) & 0xFF
        self.code[at + 1] = value & 0xFF

    def constant(self, value):
        if isinstance(value, ObjFunction):
            self.consts.append(value)
            return len(self.consts) - 1
        if type(value) is int:
            key = ("i", value)
        elif type(value) is float:
            key = ("f", value)
        else:
            key = ("s", value)
        if not hasattr(self, "_const_index"):
            self._const_index = {}
        if key not in self._const_index:
            self._const_index[key] = len(self.consts)
            self.consts.append(value)
        return self._const_index[key]


class LoopCtx:
    __slots__ = ("loop_start", "unwind_mark", "cont_mark",
                 "land_scope_end", "breaks", "exit_jump")

    def __init__(self, loop_start, unwind_mark, cont_mark, land_scope_end):
        self.loop_start = loop_start
        self.unwind_mark = unwind_mark   # target unwind utk BREAK (loop scope ikut)
        self.cont_mark = cont_mark       # target unwind utk CONTINUE (loop scope tetap)
        self.land_scope_end = land_scope_end
        self.breaks = []
        self.exit_jump = None


class FnState:
    __slots__ = ("fn", "kind", "locals", "scopes", "upvals", "loops", "parent")

    def __init__(self, name, kind, parent=None):
        self.fn = ObjFunction(name, 0, Chunk())
        self.kind = kind
        self.locals = [name or ""]
        self.scopes = []
        self.upvals = []
        self.loops = []
        self.parent = parent


class Compiler:
    """Kompilasi Program → ObjFunction (script)."""

    def __init__(self, repl=False):
        self.states = [FnState("", "script")]
        self.repl = repl

    # ------------------------------------------------------------ util

    @property
    def state(self):
        return self.states[-1]

    @property
    def chunk(self):
        return self.state.fn.chunk

    def err(self, msg, line):
        raise CrescentCompileError(msg, line)

    def emit(self, name, line, *operands):
        self.chunk.emit(name, line, *operands)

    def emit_jump(self, name, line):
        """Emit lompatan dengan operand placeholder; kembalikan posisi operand."""
        self.emit(name, line, 0xFFFF)
        return self.chunk.here() - 2

    def patch_jump(self, at):
        offset = self.chunk.here() - (at + 2)
        if offset > 0xFFFF:
            self.err("terlalu banyak bytecode untuk dilompati", 0)
        self.chunk.patch(at, offset)

    def emit_loop(self, line, start):
        self.emit("LOOP", line, 0xFFFF)
        at = self.chunk.here() - 2
        offset = self.chunk.here() - start
        self.chunk.patch(at, offset)

    def begin_scope(self):
        self.state.scopes.append(len(self.state.locals))

    def end_scope(self):
        mark = self.state.scopes.pop()
        n = len(self.state.locals) - mark
        del self.state.locals[mark:]
        if n:
            self.emit("SCOPE_END", 0, n)

    def declare_local(self, name, line):
        state = self.state
        mark = state.scopes[-1] if state.scopes else 0
        for i in range(mark, len(state.locals)):
            if state.locals[i] == name:
                self.err("variabel '{0}' sudah dideklarasikan di scope ini"
                         .format(name), line)
        state.locals.append(name)
        return len(state.locals) - 1

    # ------------------------------------------------- resolusi nama

    def resolve_local(self, state, name):
        for i in range(len(state.locals) - 1, -1, -1):
            if state.locals[i] == name:
                return i
        return None

    def resolve_upval_for(self, state, name):
        for idx, u in enumerate(state.upvals):
            if u[2] == name:
                return idx
        if state.parent is None:
            return None
        parent = state.parent
        for i in range(len(parent.locals) - 1, -1, -1):
            if parent.locals[i] == name:
                state.upvals.append((True, i, name))
                return len(state.upvals) - 1
        up = self.resolve_upval_for(parent, name)
        if up is None:
            return None
        state.upvals.append((False, up, name))
        return len(state.upvals) - 1

    # ------------------------------------------------------ program

    def compile(self, program):
        for stmt in program.stmts:
            self.stmt(stmt)
        self.emit("NIL", 1)
        self.emit("RETURN", 1)
        return self.states[0].fn

    # --------------------------------------------------- statements

    def stmt(self, node):
        if isinstance(node, N.LetStmt):
            self.stmt_let(node)
        elif isinstance(node, N.FnDecl):
            self.stmt_fn_decl(node)
        elif isinstance(node, N.IfStmt):
            self.stmt_if(node)
        elif isinstance(node, N.WhileStmt):
            self.stmt_while(node)
        elif isinstance(node, N.ForStmt):
            self.stmt_for(node)
        elif isinstance(node, N.ReturnStmt):
            self.stmt_return(node)
        elif isinstance(node, N.BreakStmt):
            self.stmt_break(node)
        elif isinstance(node, N.ContinueStmt):
            self.stmt_continue(node)
        elif isinstance(node, N.PrintStmt):
            for e in node.exprs:
                self.expr(e)
            self.emit("PRINT_N", node.line, len(node.exprs))
        elif isinstance(node, N.Block):
            self.begin_scope()
            for s in node.stmts:
                self.stmt(s)
            self.end_scope()
        elif isinstance(node, N.ExprStmt):
            if isinstance(node.expr, N.Assign):
                # assignment adalah pernyataan: nilai habis oleh SET_*
                self.expr_assign(node.expr)
            else:
                self.expr(node.expr)
                if self.repl and len(self.states) == 1:
                    self.emit("PRINT_N", node.line, 1)
                else:
                    self.emit("POP", node.line)
        else:
            self.err("pernyataan tidak dikenal: {0}".format(
                type(node).__name__), node.line)

    def stmt_let(self, node):
        state = self.state
        if state.scopes:
            if node.expr:
                self.expr(node.expr)
            else:
                self.emit("NIL", node.line)
            self.emit("LOCAL_INIT", node.line)
            self.declare_local(node.name, node.line)
        else:
            if node.expr:
                self.expr(node.expr)
            else:
                self.emit("NIL", node.line)
            self.emit("DEFINE_GLOBAL", node.line,
                      self.chunk.constant(node.name))

    def stmt_fn_decl(self, node):
        state = self.state
        if state.scopes:
            # fungsi lokal: sediakan cell dulu agar bisa merekursi dirinya
            self.emit("NIL", node.line)
            self.emit("LOCAL_INIT", node.line)
            slot = len(state.locals)
            state.locals.append(node.name)
            self.compile_fn_expr(node)
            self.emit("SET_LOCAL", node.line, slot)
        else:
            self.compile_fn_expr(node)
            self.emit("DEFINE_GLOBAL", node.line,
                      self.chunk.constant(node.name))

    def stmt_return(self, node):
        state = self.state
        if state.kind == "script":
            self.err("'return' hanya di dalam fungsi", node.line)
        if node.expr:
            self.expr(node.expr)
        else:
            self.emit("NIL", node.line)
        self.emit("RETURN", node.line)

    def stmt_break(self, node):
        state = self.state
        if not state.loops:
            self.err("'break' di luar perulangan", node.line)
        ctx = state.loops[-1]
        unw = len(state.locals) - ctx.unwind_mark
        if unw:
            self.emit("SCOPE_END", node.line, unw)
        ctx.breaks.append(self.emit_jump("JUMP", node.line))

    def stmt_continue(self, node):
        state = self.state
        if not state.loops:
            self.err("'continue' di luar perulangan", node.line)
        ctx = state.loops[-1]
        unw = len(state.locals) - ctx.cont_mark
        if unw:
            self.emit("SCOPE_END", node.line, unw)
        self.emit_loop(node.line, ctx.loop_start)

    def stmt_if(self, node):
        self.expr(node.cond)
        jelse = self.emit_jump("JUMP_IF_FALSE", node.line)
        self.emit("POP", node.line)
        self.stmt(node.then)
        jend = self.emit_jump("JUMP", node.line)
        self.patch_jump(jelse)
        self.emit("POP", node.line)
        if node.orelse is not None:
            self.stmt(node.orelse)
        self.patch_jump(jend)

    def stmt_while(self, node):
        state = self.state
        start = self.chunk.here()
        ctx = LoopCtx(start, unwind_mark=len(state.locals),
                      cont_mark=len(state.locals), land_scope_end=False)
        state.loops.append(ctx)
        self.expr(node.cond)
        ctx.exit_jump = self.emit_jump("JUMP_IF_FALSE", node.line)
        self.emit("POP", node.line)
        self.stmt(node.body)
        self.emit_loop(node.line, start)
        self.patch_jump(ctx.exit_jump)
        self.emit("POP", node.line)
        state.loops.pop()
        for b in ctx.breaks:
            self.patch_jump(b)

    def stmt_for(self, node):
        state = self.state
        line = node.line
        enclosing = len(state.locals)          # sebelum scope milik loop
        self.begin_scope()                       # scope for: 3 lokal tersembunyi

        self.expr(node.iter)
        self.emit("LOCAL_INIT", line)
        slot_it = len(state.locals)
        state.locals.append(IT)

        self.emit("CONST", line, self.chunk.constant(0))
        self.emit("LOCAL_INIT", line)
        slot_i = len(state.locals)
        state.locals.append(IX)

        self.emit("NIL", line)
        self.emit("LOCAL_INIT", line)
        slot_n = len(state.locals)
        state.locals.append(INX)

        ctx = LoopCtx(0, unwind_mark=enclosing,
                      cont_mark=len(state.locals), land_scope_end=True)
        state.loops.append(ctx)
        start = self.chunk.here()
        ctx.loop_start = start

        # __n = __iter(__it, __i)
        self.emit("GET_GLOBAL", line, self.chunk.constant(ITER_FN))
        self.emit("GET_LOCAL", line, slot_it)
        self.emit("GET_LOCAL", line, slot_i)
        self.emit("CALL", line, 2)
        self.emit("SET_LOCAL", line, slot_n)

        self.emit("GET_LOCAL", line, slot_n)
        ctx.exit_jump = self.emit_jump("JUMP_IF_FALSE", line)
        self.emit("POP", line)

        self.begin_scope()                       # scope body: var loop
        self.emit("GET_LOCAL", line, slot_n)
        self.emit("CONST", line, self.chunk.constant(1))
        self.emit("INDEX_GET", line)
        self.emit("LOCAL_INIT", line)
        self.declare_local(node.var, line)

        self.emit("GET_LOCAL", line, slot_n)
        self.emit("CONST", line, self.chunk.constant(0))
        self.emit("INDEX_GET", line)
        self.emit("SET_LOCAL", line, slot_i)

        for s in node.body.stmts:
            self.stmt(s)

        self.end_scope()

        self.emit_loop(line, start)
        self.patch_jump(ctx.exit_jump)
        self.emit("POP", line)                   # nil dari __iter
        state.loops.pop()
        self.end_scope()                         # lepaskan __it/__i/__n
        for b in ctx.breaks:
            self.patch_jump(b)

    # --------------------------------------------------- expressions

    def compile_fn_expr(self, node):
        name = node.name or "<anon>"
        child = FnState(name, "fn", parent=self.state)
        child.fn.arity = len(node.params)
        child.locals = [name] + list(node.params)
        child.scopes = [1 + len(node.params)]
        self.states.append(child)
        for s in node.body.stmts:
            self.stmt(s)
        self.emit("NIL", node.line)
        self.emit("RETURN", node.line)
        self.states.pop()

        fn = child.fn
        cidx = self.chunk.constant(fn)
        nup = len(child.upvals)
        flat = []
        for is_local, idx, _ in child.upvals:
            flat.append(1 if is_local else 0)
            flat.append(idx)
        self.emit("CLOSURE", node.line, cidx, nup, *flat)

    def expr(self, node):
        if isinstance(node, N.Literal):
            v = node.value
            if v is None:
                self.emit("NIL", node.line)
            elif v is True:
                self.emit("TRUE", node.line)
            elif v is False:
                self.emit("FALSE", node.line)
            else:
                self.emit("CONST", node.line, self.chunk.constant(v))
        elif isinstance(node, N.Ident):
            self.expr_ident(node)
        elif isinstance(node, N.Unary):
            self.expr(node.operand)
            self.emit("NEG" if node.op == "-" else "NOT", node.line)
        elif isinstance(node, N.Binary):
            self.expr(node.left)
            self.expr(node.right)
            self.emit({
                "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD",
                "==": "EQUAL", "!=": "NOT_EQUAL",
                "<": "LESS", "<=": "LESS_EQ", ">": "GREATER", ">=": "GREATER_EQ",
            }[node.op], node.line)
        elif isinstance(node, N.Logical):
            self.expr(node.left)
            jump = self.emit_jump(
                "JUMP_IF_FALSE" if node.op == "and" else "JUMP_IF_TRUE",
                node.line)
            self.emit("POP", node.line)
            self.expr(node.right)
            self.patch_jump(jump)
        elif isinstance(node, N.Assign):
            self.expr_assign(node)
        elif isinstance(node, N.Call):
            self.expr(node.callee)
            for a in node.args:
                self.expr(a)
            self.emit("CALL", node.line, len(node.args))
        elif isinstance(node, N.Index):
            self.expr(node.obj)
            self.expr(node.index)
            self.emit("INDEX_GET", node.line)
        elif isinstance(node, N.ArrayLit):
            for item in node.items:
                self.expr(item)
            self.emit("ARRAY", node.line, len(node.items))
        elif isinstance(node, N.MapLit):
            for key, value in node.pairs:
                self.expr(key)
                self.expr(value)
            self.emit("MAP", node.line, len(node.pairs))
        elif isinstance(node, N.FnExpr):
            self.compile_fn_expr(node)
        else:
            self.err("ekspresi tidak dikenal: {0}".format(
                type(node).__name__), node.line)

    def expr_ident(self, node):
        state = self.state
        slot = self.resolve_local(state, node.name)
        if slot is not None:
            self.emit("GET_LOCAL", node.line, slot)
            return
        up = self.resolve_upval_for(state, node.name)
        if up is not None:
            self.emit("GET_UPVAL", node.line, up)
            return
        self.emit("GET_GLOBAL", node.line, self.chunk.constant(node.name))

    def expr_assign(self, node):
        state = self.state
        target = node.target
        if isinstance(target, N.Ident):
            slot = self.resolve_local(state, target.name)
            self.expr(node.value)
            if slot is not None:
                self.emit("SET_LOCAL", node.line, slot)
                return
            up = self.resolve_upval_for(state, target.name)
            if up is not None:
                self.emit("SET_UPVAL", node.line, up)
                return
            self.emit("SET_GLOBAL", node.line, self.chunk.constant(target.name))
        elif isinstance(target, N.Index):
            self.expr(target.obj)
            self.expr(target.index)
            self.expr(node.value)
            self.emit("INDEX_SET", node.line)
        else:
            self.err("target assignment tidak valid", node.line)


def compile_source(source, repl=False):
    """Pintasan penuh: token → parse → compile. Return ObjFunction script."""
    from .parser import parse
    return Compiler(repl=repl).compile(parse(source))
