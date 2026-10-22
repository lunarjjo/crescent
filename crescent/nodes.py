"""AST Crescent — node minimalis dengan pelacak baris sumber.

Setiap node menyimpan ``line`` agar compiler dapat melaporkan kesalahan
dengan posisi yang tepat.
"""


class Node:
    __slots__ = ("line",)

    def __init__(self, line):
        self.line = line

    def __repr__(self):
        fields = [s for s in self.__slots__ if s != "line"]
        inner = ", ".join("{0}={1!r}".format(f, getattr(self, f)) for f in fields)
        return "({0} {1})".format(type(self).__name__, inner)


def _node(name, *fields):
    slots = ("line",) + fields

    def __init__(self, line, *args):
        if len(args) != len(fields):
            raise TypeError("{0} butuh {1} argumen".format(name, len(fields)))
        self.line = line
        for f, v in zip(fields, args):
            setattr(self, f, v)

    return type(name, (Node,), {"__slots__": slots, "__init__": __init__})


Program = _node("Program", "stmts")
Block = _node("Block", "stmts")
LetStmt = _node("LetStmt", "name", "expr")
FnDecl = _node("FnDecl", "name", "params", "body")
IfStmt = _node("IfStmt", "cond", "then", "orelse")
WhileStmt = _node("WhileStmt", "cond", "body")
ForStmt = _node("ForStmt", "var", "iter", "body")
ReturnStmt = _node("ReturnStmt", "expr")
BreakStmt = _node("BreakStmt")
ContinueStmt = _node("ContinueStmt")
PrintStmt = _node("PrintStmt", "exprs")
ExprStmt = _node("ExprStmt", "expr")

Literal = _node("Literal", "value")
Ident = _node("Ident", "name")
Unary = _node("Unary", "op", "operand")
Binary = _node("Binary", "op", "left", "right")
Logical = _node("Logical", "op", "left", "right")
Assign = _node("Assign", "target", "value")
Call = _node("Call", "callee", "args")
Index = _node("Index", "obj", "index")
ArrayLit = _node("ArrayLit", "items")
MapLit = _node("MapLit", "pairs")
FnExpr = _node("FnExpr", "params", "body", "name")
