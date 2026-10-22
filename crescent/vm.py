"""Virtual machine Crescent — dispatch loop atas bytecode.

Setiap frame punya daftar ``slots`` berisi cell (list-1-elemen). Closure
menangkap cell langsung sehingga variabel tertangkap tetap hidup meski
frame/scope pembuatnya sudah selesai.
"""
from .compiler import OP, OPNAMES
from .errors import CrescentRuntimeError
from .values import (ObjClosure, ObjNative, crescent_eq, fmt, truthy,
                     type_name)

MAX_FRAMES = 256


class Frame:
    __slots__ = ("closure", "ip", "slots")

    def __init__(self, closure):
        self.closure = closure
        self.ip = 0
        self.slots = [[closure]]  # slot 0 = cell berisi closure (rekursi)

    @property
    def code(self):
        return self.closure.fn.chunk.code

    @property
    def consts(self):
        return self.closure.fn.chunk.consts

    @property
    def lines(self):
        return self.closure.fn.chunk.lines


def _is_num(v):
    t = type(v)
    return t is int or t is float


class VM:
    def __init__(self, print_fn=None):
        self.globals = {}
        self.stack = []
        self.frames = []
        self.print_fn = print_fn if print_fn is not None else print
        from .builtins import install_builtins
        install_builtins(self)

    # ------------------------------------------------------------ error

    def rt(self, msg, line):
        raise CrescentRuntimeError(msg, line)

    def rt_here(self, msg, frame, ip):
        line = frame.lines[ip - 1] if ip >= 1 else 0
        err = CrescentRuntimeError(msg, line)
        trace = [(frame.closure.fn.name, line)]
        for f in reversed(self.frames[:-1]):
            fline = f.lines[f.ip - 1] if f.ip else 0
            trace.append((f.closure.fn.name, fline))
        err.traceback = trace
        raise err

    # ---------------------------------------------------------- public

    def run_function(self, fn):
        closure = ObjClosure(fn, [])
        self.frames = [Frame(closure)]
        return self._dispatch(1)

    def call_callable(self, callee, args, line=0):
        """Panggil closure/native dari host (dipakai sort/map/filter/reduce)."""
        if isinstance(callee, ObjClosure):
            self._check_arity(callee, len(args), line)
            frame = Frame(callee)
            for a in args:
                frame.slots.append([a])
            self.frames.append(frame)
            return self._dispatch(len(self.frames))
        if isinstance(callee, ObjNative):
            self._check_native(callee, len(args), line)
            return callee.fn(self, *args)
        self.rt("nilai tidak dapat dipanggil: {0}".format(type_name(callee)),
                line)

    def _check_arity(self, closure, n, line):
        want = closure.fn.arity
        if n != want:
            self.rt("fungsi '{0}' mengharapkan {1} argumen, diberikan {2}"
                    .format(closure.fn.name, want, n), line)

    def _check_native(self, native, n, line):
        if native.arity >= 0:
            if n != native.arity:
                self.rt("fungsi '{0}' mengharapkan {1} argumen, diberikan {2}"
                        .format(native.name, native.arity, n), line)
        elif n < native.min_arity:
            self.rt("fungsi '{0}' mengharapkan minimal {1} argumen, "
                    "diberikan {2}".format(native.name, native.min_arity, n),
                    line)

    # -------------------------------------------------------- dispatch

    def _dispatch(self, base):
        stack = self.stack
        frames = self.frames
        while len(frames) >= base:
            frame = frames[-1]
            code = frame.code
            consts = frame.consts
            lines = frame.lines
            ip = frame.ip
            try:
                while True:
                    op = code[ip]
                    ip += 1

                    if op == OP["CONST"]:
                        stack.append(consts[(code[ip] << 8) | code[ip + 1]])
                        ip += 2
                    elif op == OP["NIL"]:
                        stack.append(None)
                    elif op == OP["TRUE"]:
                        stack.append(True)
                    elif op == OP["FALSE"]:
                        stack.append(False)
                    elif op == OP["POP"]:
                        stack.pop()
                    elif op == OP["DEFINE_GLOBAL"]:
                        name = consts[(code[ip] << 8) | code[ip + 1]]
                        ip += 2
                        self.globals[name] = stack.pop()
                    elif op == OP["GET_GLOBAL"]:
                        name = consts[(code[ip] << 8) | code[ip + 1]]
                        ip += 2
                        if name not in self.globals:
                            self.rt_here(
                                "variabel '{0}' belum didefinisikan".format(name),
                                frame, ip)
                        stack.append(self.globals[name])
                    elif op == OP["SET_GLOBAL"]:
                        name = consts[(code[ip] << 8) | code[ip + 1]]
                        ip += 2
                        if name not in self.globals:
                            self.rt_here(
                                "variabel '{0}' belum didefinisikan "
                                "(gunakan let)".format(name), frame, ip)
                        self.globals[name] = stack.pop()
                    elif op == OP["GET_LOCAL"]:
                        slot = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        stack.append(frame.slots[slot][0])
                    elif op == OP["SET_LOCAL"]:
                        slot = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        frame.slots[slot][0] = stack.pop()
                    elif op == OP["LOCAL_INIT"]:
                        frame.slots.append([stack.pop()])
                    elif op == OP["SCOPE_END"]:
                        n = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        del frame.slots[len(frame.slots) - n:]
                    elif op == OP["GET_UPVAL"]:
                        idx = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        stack.append(frame.closure.cells[idx][0])
                    elif op == OP["SET_UPVAL"]:
                        idx = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        frame.closure.cells[idx][0] = stack.pop()
                    elif op == OP["JUMP"]:
                        off = (code[ip] << 8) | code[ip + 1]
                        ip += 2 + off
                    elif op == OP["JUMP_IF_FALSE"]:
                        off = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        if not truthy(stack[-1]):
                            ip += off
                    elif op == OP["JUMP_IF_TRUE"]:
                        off = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        if truthy(stack[-1]):
                            ip += off
                    elif op == OP["LOOP"]:
                        off = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        ip -= off
                    elif op == OP["EQUAL"] or op == OP["NOT_EQUAL"]:
                        b = stack.pop()
                        a = stack.pop()
                        res = crescent_eq(a, b)
                        stack.append(res if op == OP["EQUAL"] else not res)
                    elif op in (OP["LESS"], OP["LESS_EQ"],
                                OP["GREATER"], OP["GREATER_EQ"]):
                        b = stack.pop()
                        a = stack.pop()
                        if not ((_is_num(a) and _is_num(b))
                                or (type(a) is str and type(b) is str)):
                            self.rt_here(
                                "perbandingan mengharapkan number-number "
                                "atau string-string, didapat {0} dan {1}"
                                .format(type_name(a), type_name(b)), frame, ip)
                        if op == OP["LESS"]:
                            stack.append(a < b)
                        elif op == OP["LESS_EQ"]:
                            stack.append(a <= b)
                        elif op == OP["GREATER"]:
                            stack.append(a > b)
                        else:
                            stack.append(a >= b)
                    elif op == OP["ADD"]:
                        b = stack.pop()
                        a = stack.pop()
                        if _is_num(a) and _is_num(b):
                            stack.append(a + b)
                        elif type(a) is str and type(b) is str:
                            stack.append(a + b)
                        else:
                            self.rt_here(
                                "operand '+' harus number+number atau "
                                "string+string, didapat {0} dan {1}".format(
                                    type_name(a), type_name(b)), frame, ip)
                    elif op in (OP["SUB"], OP["MUL"], OP["DIV"], OP["MOD"]):
                        b = stack.pop()
                        a = stack.pop()
                        if not (_is_num(a) and _is_num(b)):
                            name = OPNAMES[op]
                            self.rt_here(
                                "operand '{0}' mengharapkan number, didapat "
                                "{1} dan {2}".format(
                                    name.lower(), type_name(a), type_name(b)),
                                frame, ip)
                        if op == OP["SUB"]:
                            stack.append(a - b)
                        elif op == OP["MUL"]:
                            stack.append(a * b)
                        else:
                            if b == 0:
                                self.rt_here(
                                    "pembagian dengan nol", frame, ip)
                            if op == OP["DIV"]:
                                stack.append(a / b)
                            else:
                                stack.append(a % b)
                    elif op == OP["NOT"]:
                        stack.append(not truthy(stack.pop()))
                    elif op == OP["NEG"]:
                        v = stack.pop()
                        if not _is_num(v):
                            self.rt_here(
                                "negasi mengharapkan number, didapat {0}"
                                .format(type_name(v)), frame, ip)
                        stack.append(-v)
                    elif op == OP["PRINT_N"]:
                        n = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        vals = [stack.pop() for _ in range(n)][::-1]
                        self.print_fn(" ".join(fmt(v) for v in vals))
                    elif op == OP["ARRAY"]:
                        n = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        arr = [stack.pop() for _ in range(n)][::-1]
                        stack.append(arr)
                    elif op == OP["MAP"]:
                        npairs = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        m = {}
                        for _ in range(npairs):
                            v = stack.pop()
                            k = stack.pop()
                            try:
                                m[k] = v
                            except TypeError:
                                self.rt_here(
                                    "kunci map harus hashable, didapat {0}"
                                    .format(type_name(k)), frame, ip)
                        stack.append(m)
                    elif op == OP["INDEX_GET"]:
                        idx = stack.pop()
                        obj = stack.pop()
                        stack.append(self._index_get(obj, idx, frame, ip))
                    elif op == OP["INDEX_SET"]:
                        value = stack.pop()
                        idx = stack.pop()
                        obj = stack.pop()
                        self._index_set(obj, idx, value, frame, ip)
                    elif op == OP["CALL"]:
                        n = (code[ip] << 8) | code[ip + 1]
                        ip += 2
                        args = [stack.pop() for _ in range(n)][::-1]
                        callee = stack.pop()
                        if isinstance(callee, ObjClosure):
                            self._check_arity(callee, n,
                                              lines[ip - 1] if ip else 0)
                            if len(frames) >= MAX_FRAMES:
                                self.rt_here(
                                    "kedalaman panggilan maksimum ({0}) "
                                    "tercapai".format(MAX_FRAMES), frame, ip)
                            nf = Frame(callee)
                            for a in args:
                                nf.slots.append([a])
                            frame.ip = ip
                            frames.append(nf)
                            break  # muat ulang frame baru
                        elif isinstance(callee, ObjNative):
                            self._check_native(callee, n,
                                               lines[ip - 1] if ip else 0)
                            try:
                                stack.append(callee.fn(self, *args))
                            except CrescentRuntimeError as e:
                                if not e.traceback:
                                    self.rt_here(e.msg, frame, ip)
                                raise
                        else:
                            self.rt_here(
                                "nilai tidak dapat dipanggil: {0}".format(
                                    type_name(callee)), frame, ip)
                    elif op == OP["CLOSURE"]:
                        cidx = (code[ip] << 8) | code[ip + 1]
                        nup = (code[ip + 2] << 8) | code[ip + 3]
                        ip += 4
                        cells = []
                        for _ in range(nup):
                            is_local = (code[ip] << 8) | code[ip + 1]
                            idx = (code[ip + 2] << 8) | code[ip + 3]
                            ip += 4
                            if is_local:
                                cells.append(frame.slots[idx])
                            else:
                                cells.append(frame.closure.cells[idx])
                        stack.append(ObjClosure(consts[cidx], cells))
                    elif op == OP["RETURN"]:
                        rv = stack.pop()
                        frames.pop()
                        if len(frames) < base:
                            return rv
                        stack.append(rv)
                        break  # muat ulang frame pemanggil
                    else:
                        self.rt_here("opcode tidak dikenal: {0}".format(op),
                                     frame, ip)
            finally:
                frame.ip = ip
        return self.stack.pop() if self.stack else None

    # -------------------------------------------------------- indeks

    def _index_get(self, obj, idx, frame, ip):
        t = type(obj)
        if t is list:
            if type(idx) is not int:
                self.rt_here("indeks array harus number, didapat {0}"
                             .format(type_name(idx)), frame, ip)
            if not 0 <= idx < len(obj):
                self.rt_here("indeks array di luar batas: {0} (panjang {1})"
                             .format(idx, len(obj)), frame, ip)
            return obj[idx]
        if t is dict:
            try:
                if idx in obj:
                    return obj[idx]
            except TypeError:
                pass
            return None
        if t is str:
            if type(idx) is not int:
                self.rt_here("indeks string harus number, didapat {0}"
                             .format(type_name(idx)), frame, ip)
            if not 0 <= idx < len(obj):
                self.rt_here("indeks string di luar batas: {0} (panjang {1})"
                             .format(idx, len(obj)), frame, ip)
            return obj[idx]
        self.rt_here("tidak dapat mengindeks nilai bertipe {0}"
                     .format(type_name(obj)), frame, ip)

    def _index_set(self, obj, idx, value, frame, ip):
        t = type(obj)
        if t is list:
            if type(idx) is not int:
                self.rt_here("indeks array harus number, didapat {0}"
                             .format(type_name(idx)), frame, ip)
            if not 0 <= idx < len(obj):
                self.rt_here("indeks array di luar batas: {0} (panjang {1}) "
                             "— gunakan push() untuk menambah"
                             .format(idx, len(obj)), frame, ip)
            obj[idx] = value
            return
        if t is dict:
            try:
                obj[idx] = value
            except TypeError:
                self.rt_here("kunci map harus hashable, didapat {0}"
                             .format(type_name(idx)), frame, ip)
            return
        if t is str:
            self.rt_here("string bersifat immutable — tidak dapat diindeks "
                         "untuk diisi", frame, ip)
        self.rt_here("tidak dapat mengindeks nilai bertipe {0}"
                     .format(type_name(obj)), frame, ip)
