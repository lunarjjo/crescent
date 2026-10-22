"""Parser Crescent — recursive descent + precedence climbing.

Pernyataan diakhiri baris baru ATAU ``;`` (keduanya opsional sebelum ``}``
dan EOF). Baris baru di dalam kurung diabaikan lexer sehingga ekspresi
panjang boleh dilipat.

Grammar inti::

    program  := stmt* EOF
    stmt     := let | fnDecl | if | while | for | return | break
                | continue | print | block | exprStmt
    exprStmt := expr ('=' expr)?          -- assignment sebagai pernyataan
    expr     := unary (binop expr)*       -- precedence climbing
    primary  := NUMBER | STRING | IDENT | true | false | nil
                | '(' expr ')' | '[' ... ']' | '{' ... '}' | fnExpr
"""
from . import nodes as N
from .errors import CrescentSyntaxError
from .lexer import tokenize

# precedence — makin besar makin rapat
PREC = {
    "or": 1, "and": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6,
}

TYPE_TEST = {"nil", "bool", "number", "string", "array", "map", "function"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------------------------------------------------------------- util

    def peek(self, k=0):
        idx = self.pos + k
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def check(self, ttype):
        return self.peek().type == ttype

    def match(self, ttype):
        if self.check(ttype):
            return self.advance()
        return None

    def expect(self, ttype, what=None):
        if self.check(ttype):
            return self.advance()
        tok = self.peek()
        what = what or "'{0}'".format(ttype)
        raise CrescentSyntaxError(
            "mengharapkan {0}, didapat {1}".format(
                what, self._describe(tok)), tok.line, tok.col)

    @staticmethod
    def _describe(tok):
        if tok.type == "EOF":
            return "akhir file"
        if tok.type == "NEWLINE":
            return "akhir baris"
        return "'{0}'".format(tok.value)

    def error_here(self, msg):
        tok = self.peek()
        raise CrescentSyntaxError(msg, tok.line, tok.col)

    def skip_newlines(self):
        while self.check("NEWLINE"):
            self.advance()

    def peek_past_newlines(self):
        idx = self.pos
        while self.tokens[idx].type == "NEWLINE":
            idx += 1
        return self.tokens[idx].type

    def end_statement(self):
        """Konsumsi akhir pernyataan: NEWLINE+ / ';' / tak perlu sebelum '}' EOF."""
        if self.check("}") or self.check("EOF"):
            return
        if self.match(";") or self.match("NEWLINE"):
            self.skip_newlines()
            return
        self.error_here(
            "akhir pernyataan tidak valid — harap baris baru atau ';'")

    # ------------------------------------------------------------ program

    def parse(self):
        stmts = []
        self.skip_newlines()
        while not self.check("EOF"):
            if self.match(";"):
                self.skip_newlines()
                continue
            stmts.append(self.statement())
            self.end_statement()
            self.skip_newlines()
        return N.Program(1, stmts)

    # ---------------------------------------------------------- statement

    def statement(self):
        t = self.peek().type

        if t == "let":
            return self.let_statement()
        if t == "fn" and self.peek(1).type == "IDENT":
            return self.fn_decl()
        if t == "if":
            return self.if_statement()
        if t == "while":
            return self.while_statement()
        if t == "for":
            return self.for_statement()
        if t == "return":
            return self.return_statement()
        if t == "break":
            tok = self.advance()
            return N.BreakStmt(tok.line)
        if t == "continue":
            tok = self.advance()
            return N.ContinueStmt(tok.line)
        if t == "print":
            return self.print_statement()
        if t == "{":
            return self.block()

        return self.expr_statement()

    def let_statement(self):
        tok = self.advance()  # let
        name = self.expect("IDENT", "nama variabel")
        expr = None
        if self.match("="):
            self.skip_newlines()
            expr = self.expression()
        return N.LetStmt(tok.line, name.value, expr)

    def fn_decl(self):
        tok = self.advance()  # fn
        name = self.expect("IDENT", "nama fungsi")
        params, body = self.fn_rest()
        return N.FnDecl(tok.line, name.value, params, body)

    def fn_rest(self):
        self.expect("(", "'(' setelah nama fungsi")
        self.skip_newlines()
        params = []
        seen = set()
        if not self.check(")"):
            while True:
                p = self.expect("IDENT", "nama parameter")
                if p.value in seen:
                    raise CrescentSyntaxError(
                        "parameter '{0}' ganda".format(p.value),
                        p.line, p.col)
                seen.add(p.value)
                params.append(p.value)
                if not self.match(","):
                    break
                self.skip_newlines()
        self.skip_newlines()
        self.expect(")", "')' penutup parameter")
        body = self.block()
        return params, body

    def if_statement(self):
        tok = self.advance()  # if
        cond = self.expression()
        then = self.block()
        orelse = None
        if self.peek_past_newlines() == "else":
            self.skip_newlines()
            self.advance()  # else
            self.skip_newlines()
            if self.check("if"):
                orelse = self.if_statement()
            else:
                orelse = self.block()
        return N.IfStmt(tok.line, cond, then, orelse)

    def while_statement(self):
        tok = self.advance()  # while
        cond = self.expression()
        body = self.block()
        return N.WhileStmt(tok.line, cond, body)

    def for_statement(self):
        tok = self.advance()  # for
        var = self.expect("IDENT", "nama variabel loop")
        self.expect("in", "'in' setelah variabel loop")
        iterable = self.expression()
        body = self.block()
        return N.ForStmt(tok.line, var.value, iterable, body)

    def return_statement(self):
        tok = self.advance()  # return
        expr = None
        if not (self.check("NEWLINE") or self.check(";")
                or self.check("}") or self.check("EOF")):
            expr = self.expression()
        return N.ReturnStmt(tok.line, expr)

    def print_statement(self):
        tok = self.advance()  # print
        exprs = [self.expression()]
        while self.match(","):
            self.skip_newlines()
            exprs.append(self.expression())
        return N.PrintStmt(tok.line, exprs)

    def expr_statement(self):
        expr = self.expression()
        if self.check("="):
            eq = self.advance()
            if not isinstance(expr, (N.Ident, N.Index)):
                raise CrescentSyntaxError(
                    "sisi kiri assignment tidak valid", eq.line, eq.col)
            self.skip_newlines()
            value = self.expression()
            return N.ExprStmt(eq.line, N.Assign(eq.line, expr, value))
        return N.ExprStmt(expr.line, expr)

    def block(self):
        self.expect("{", "'{' pembuka blok")
        stmts = []
        self.skip_newlines()
        while not self.check("}"):
            if self.check("EOF"):
                self.error_here("'}' penutup blok hilang")
            stmts.append(self.statement())
            self.end_statement()
            self.skip_newlines()
        self.advance()  # '}'
        return N.Block(1, stmts)

    # --------------------------------------------------------- expression

    def expression(self, min_prec=0):
        left = self.unary()
        while True:
            t = self.peek().type
            if t in ("and", "or"):
                prec = PREC[t]
                maker = N.Logical
            elif t in PREC:
                prec = PREC[t]
                maker = N.Binary
            else:
                break
            if prec < min_prec:
                break
            op = self.advance()
            self.skip_newlines()  # operator menggantung: lanjut baris bawah
            right = self.expression(prec + 1)
            left = maker(op.line, op.type, left, right)
        return left

    def unary(self):
        if self.check("-") or self.check("not"):
            op = self.advance()
            operand = self.unary()
            return N.Unary(op.line, op.type, operand)
        return self.postfix()

    def postfix(self):
        expr = self.primary()
        while True:
            if self.check("("):
                op = self.advance()
                args = []
                self.skip_newlines()
                if not self.check(")"):
                    args.append(self.expression())
                    while self.match(","):
                        self.skip_newlines()
                        if self.check(")"):
                            break  # trailing comma
                        args.append(self.expression())
                self.skip_newlines()
                self.expect(")", "')' penutup argumen")
                expr = N.Call(op.line, expr, args)
            elif self.check("["):
                op = self.advance()
                self.skip_newlines()
                idx = self.expression()
                self.skip_newlines()
                self.expect("]", "']' penutup indeks")
                expr = N.Index(op.line, expr, idx)
            elif self.check("."):
                # gula sintaks: obj.key  ==  obj["key"]
                op = self.advance()
                name = self.expect("IDENT", "nama properti setelah '.'")
                expr = N.Index(op.line, expr, N.Literal(op.line, name.value))
            else:
                break
        return expr

    def primary(self):
        tok = self.peek()
        t = tok.type

        if t == "NUMBER" or t == "STRING":
            self.advance()
            return N.Literal(tok.line, tok.value)
        if t == "true":
            self.advance()
            return N.Literal(tok.line, True)
        if t == "false":
            self.advance()
            return N.Literal(tok.line, False)
        if t == "nil":
            self.advance()
            return N.Literal(tok.line, None)
        if t == "IDENT":
            self.advance()
            return N.Ident(tok.line, tok.value)
        if t == "(":
            self.advance()
            self.skip_newlines()
            expr = self.expression()
            self.skip_newlines()
            self.expect(")", "')' penutup grup")
            return expr
        if t == "[":
            return self.array_literal()
        if t == "{":
            return self.map_literal()
        if t == "fn":
            self.advance()
            if self.check("IDENT"):
                self.error_here(
                    "fungsi bernama hanya sebagai pernyataan; "
                    "di ekspresi gunakan fn(params) { ... }")
            params, body = self.fn_rest()
            return N.FnExpr(tok.line, params, body, "<anon>")

        self.error_here(
            "ekspresi tidak valid, didapat {0}".format(self._describe(tok)))

    def array_literal(self):
        tok = self.advance()  # '['
        items = []
        self.skip_newlines()
        if not self.check("]"):
            items.append(self.expression())
            while self.match(","):
                self.skip_newlines()
                if self.check("]"):
                    break  # trailing comma diperbolehkan
                items.append(self.expression())
        self.skip_newlines()
        self.expect("]", "']' penutup array")
        return N.ArrayLit(tok.line, items)

    def map_literal(self):
        tok = self.advance()  # '{'
        pairs = []
        self.skip_newlines()
        if not self.check("}"):
            while True:
                key = self.map_key()
                self.expect(":", "':' pemisah kunci-nilai")
                value = self.expression()
                pairs.append((key, value))
                if not self.match(","):
                    break
                self.skip_newlines()
                if self.check("}"):
                    break  # trailing comma diperbolehkan
        self.skip_newlines()
        self.expect("}", "'}' penutup map")
        return N.MapLit(tok.line, pairs)

    def map_key(self):
        tok = self.peek()
        if tok.type == "STRING" or tok.type == "NUMBER":
            self.advance()
            return N.Literal(tok.line, tok.value)
        if tok.type == "IDENT":
            self.advance()
            return N.Literal(tok.line, tok.value)
        if tok.type == "[":
            self.advance()
            expr = self.expression()
            self.expect("]", "']' penutup kunci")
            return expr
        self.error_here("kunci map harus string, angka, atau [ekspresi]")


def parse(source):
    """Pintasan: tokenisasi lalu parse menjadi Program."""
    return Parser(tokenize(source)).parse()
