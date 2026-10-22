"""Objek runtime Crescent — fungsi, closure, native; format & perbandingan nilai.

Representasi nilai runtime memanfaatkan tipe Python:
- nil  → None
- bool → bool
- number → int / float
- string → str
- array → list
- map → dict
- fungsi → ObjFunction / ObjClosure / ObjNative
"""
from .errors import CrescentRuntimeError


class ObjFunction:
    __slots__ = ("name", "arity", "chunk")

    def __init__(self, name, arity, chunk):
        self.name = name
        self.arity = arity
        self.chunk = chunk

    def __repr__(self):
        return "<fn {0}/{1}>".format(self.name or "<script>", self.arity)


class ObjClosure:
    __slots__ = ("fn", "cells")

    def __init__(self, fn, cells=None):
        self.fn = fn
        self.cells = cells if cells is not None else []

    def __repr__(self):
        return "<fn {0}/{1}>".format(self.fn.name, self.fn.arity)


class ObjNative:
    __slots__ = ("name", "arity", "min_arity", "fn")

    def __init__(self, name, arity, fn, min_arity=None):
        self.name = name
        self.arity = arity          # -1 = variadik (cek min_arity)
        self.min_arity = min_arity if min_arity is not None else arity
        self.fn = fn

    def __repr__(self):
        return "<native {0}>".format(self.name)


def type_name(v):
    if v is None:
        return "nil"
    if v is True or v is False:
        return "bool"
    t = type(v)
    if t is int or t is float:
        return "number"
    if t is str:
        return "string"
    if t is list:
        return "array"
    if t is dict:
        return "map"
    if isinstance(v, (ObjFunction, ObjClosure, ObjNative)):
        return "function"
    return "obyek-python"  # seharusnya tak terjadi


def truthy(v):
    """Hanya nil dan false yang falsy — 0 dan \"\" tetap truthy."""
    return v is not None and v is not False


def crescent_eq(a, b):
    """Perbandingan kesetaraan nilai; bool tidak sama dengan number."""
    a_bool = a is True or a is False
    b_bool = b is True or b is False
    if a_bool or b_bool:
        return a is b
    ta, tb = type(a), type(b)
    if (ta is int or ta is float) and (tb is int or tb is float):
        return a == b
    if ta is str and tb is str:
        return a == b
    if ta is list and tb is list:
        if len(a) != len(b):
            return False
        return all(crescent_eq(x, y) for x, y in zip(a, b))
    if ta is dict and tb is dict:
        if len(a) != len(b):
            return False
        for k, v in a.items():
            if k not in b or not crescent_eq(v, b[k]):
                return False
        return True
    if a is None and b is None:
        return True
    return a is b


def _quote(s):
    out = s.replace("\\", "\\\\").replace('"', '\\"')
    out = out.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
    return '"' + out + '"'


def fmt(v, quote=False):
    """Format nilai untuk print; koleksi mengutip elemen stringnya."""
    if v is None:
        return "nil"
    if v is True:
        return "true"
    if v is False:
        return "false"
    t = type(v)
    if t is int:
        return str(v)
    if t is float:
        if v != v:  # NaN
            return "nan"
        if v in (float("inf"), float("-inf")):
            return "inf" if v > 0 else "-inf"
        if v == int(v) and abs(v) < 1e16:
            return "{0:.1f}".format(v)
        return repr(v)
    if t is str:
        return _quote(v) if quote else v
    if t is list:
        return "[" + ", ".join(fmt(x, True) for x in v) + "]"
    if t is dict:
        inner = ", ".join("{0}: {1}".format(fmt(k, True), fmt(x, True))
                          for k, x in v.items())
        return "{" + inner + "}"
    if isinstance(v, (ObjFunction, ObjClosure)):
        return "<fn {0}/{1}>".format(v.fn.name if isinstance(v, ObjClosure)
                                     else v.name,
                                     (v.fn.arity if isinstance(v, ObjClosure)
                                      else v.arity))
    if isinstance(v, ObjNative):
        return "<native {0}>".format(v.name)
    return str(v)


def assert_number(v, ctx):
    if type(v) is not int and type(v) is not float:
        raise CrescentRuntimeError(
            "{0} mengharapkan number, didapat {1}".format(
                ctx, type_name(v)), 0)
    return v


def assert_string(v, ctx):
    if type(v) is not str:
        raise CrescentRuntimeError(
            "{0} mengharapkan string, didapat {1}".format(
                ctx, type_name(v)), 0)
    return v


def assert_array(v, ctx):
    if type(v) is not list:
        raise CrescentRuntimeError(
            "{0} mengharapkan array, didapat {1}".format(
                ctx, type_name(v)), 0)
    return v


def assert_map(v, ctx):
    if type(v) is not dict:
        raise CrescentRuntimeError(
            "{0} mengharapkan map, didapat {1}".format(
                ctx, type_name(v)), 0)
    return v
