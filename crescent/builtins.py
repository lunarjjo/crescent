"""Stdlib Crescent — fungsi bawaan (native).

Semua native menerima ``vm`` sebagai argumen pertama agar sort/map/filter/
reduce dapat memanggil balik closure Crescent lewat ``vm.call_callable``.
"""
import math
import random as _random_module
import time as _time

from .errors import CrescentRuntimeError
from .values import (ObjNative, assert_array, assert_map, assert_number,
                     assert_string, fmt, truthy, type_name)


def _err(msg):
    raise CrescentRuntimeError(msg, 0)


def _call(vm, f, args):
    return vm.call_callable(f, args)


def _callable(v, ctx):
    from .values import ObjClosure, ObjNative
    if not isinstance(v, (ObjClosure, ObjNative)):
        _err("{0} mengharapkan function, didapat {1}".format(ctx, type_name(v)))
    return v


# ------------------------------------------------------------ dasar

def _len(vm, x):
    t = type(x)
    if t is list or t is dict or t is str:
        return len(x)
    _err("len() mengharapkan array, map, atau string, didapat {0}"
         .format(type_name(x)))


def _push(vm, arr, v):
    assert_array(arr, "push()")
    arr.append(v)
    return arr


def _pop(vm, arr):
    assert_array(arr, "pop()")
    if not arr:
        _err("pop() pada array kosong")
    return arr.pop()


def _keys(vm, m):
    assert_map(m, "keys()")
    return list(m.keys())


def _values(vm, m):
    assert_map(m, "values()")
    return list(m.values())


def _has(vm, coll, key):
    t = type(coll)
    if t is dict:
        try:
            return key in coll
        except TypeError:
            return False
    if t is list:
        if type(key) is not int:
            _err("has() pada array mengharapkan indeks number")
        return 0 <= key < len(coll)
    if t is str:
        return assert_string(key, "has() pada string") in coll
    _err("has() mengharapkan map, array, atau string")


def _del(vm, coll, key):
    t = type(coll)
    if t is dict:
        try:
            if key in coll:
                del coll[key]
                return None
        except TypeError:
            pass
        _err("kunci map tidak ditemukan: {0}".format(fmt(key, True)))
    if t is list:
        if type(key) is not int or not 0 <= key < len(coll):
            _err("indeks array di luar batas: {0}".format(key))
        del coll[key]
        return None
    _err("del() mengharapkan map atau array")


def _str(vm, x):
    return fmt(x)


def _num(vm, x):
    t = type(x)
    if t is int or t is float:
        return x
    if t is str:
        s = x.strip()
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                _err("num() tidak dapat membaca angka dari: {0}"
                     .format(fmt(x, True)))
    _err("num() mengharapkan string atau number, didapat {0}".format(
        type_name(x)))


def _type(vm, x):
    return type_name(x)


# ------------------------------------------------------------- angka

def _abs(vm, x):
    return abs(assert_number(x, "abs()"))


def _floor(vm, x):
    return math.floor(assert_number(x, "floor()"))


def _ceil(vm, x):
    return math.ceil(assert_number(x, "ceil()"))


def _sqrt(vm, x):
    v = assert_number(x, "sqrt()")
    if v < 0:
        _err("sqrt() pada bilangan negatif")
    return math.sqrt(v)


def _min(vm, *args):
    if not args:
        _err("min() butuh minimal satu argumen")
    for a in args:
        assert_number(a, "min()")
    return min(args)


def _max(vm, *args):
    if not args:
        _err("max() butuh minimal satu argumen")
    for a in args:
        assert_number(a, "max()")
    return max(args)


def _range(vm, *args):
    for a in args:
        if type(a) is not int:
            _err("range() mengharapkan number bulat")
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    else:
        start, stop, step = args
    if step == 0:
        _err("range(): langkah tidak boleh nol")
    return list(range(start, stop, step))


def _clock(vm):
    return _time.time()


def _random(vm, *args):
    if not args:
        return _random_module.random()
    if len(args) == 1 and type(args[0]) is int:
        return _random_module.randrange(args[0])
    _err("random() tanpa argumen atau random(n)")


# ----------------------------------------------------------- string

def _join(vm, arr, sep):
    assert_array(arr, "join()")
    assert_string(sep, "join()")
    for x in arr:
        if type(x) is not str:
            _err("join() mengharapkan array of string, didapat {0}"
                 .format(type_name(x)))
    return sep.join(arr)


def _split(vm, s, sep):
    assert_string(s, "split()")
    assert_string(sep, "split()")
    return s.split(sep)


def _upper(vm, s):
    return assert_string(s, "upper()").upper()


def _lower(vm, s):
    return assert_string(s, "lower()").lower()


def _replace(vm, s, old, new):
    assert_string(s, "replace()")
    assert_string(old, "replace()")
    assert_string(new, "replace()")
    return s.replace(old, new)


def _trim(vm, s):
    return assert_string(s, "trim()").strip()


def _ord(vm, c):
    s = assert_string(c, "ord()")
    if len(s) != 1:
        _err("ord() mengharapkan satu karakter")
    return ord(s)


def _chr(vm, n):
    if type(n) is not int:
        _err("chr() mengharapkan number bulat")
    try:
        return chr(n)
    except (ValueError, OverflowError):
        _err("chr() di luar rentang unicode")


# ----------------------------------------------- fungsional & iterasi

def _map_fn(vm, arr, f):
    assert_array(arr, "map()")
    _callable(f, "map()")
    return [_call(vm, f, [x]) for x in arr]


def _filter(vm, arr, f):
    assert_array(arr, "filter()")
    _callable(f, "filter()")
    return [x for x in arr if truthy(_call(vm, f, [x]))]


def _reduce(vm, arr, f, init):
    assert_array(arr, "reduce()")
    _callable(f, "reduce()")
    acc = init
    for x in arr:
        acc = _call(vm, f, [acc, x])
    return acc


def _default_cmp(a, b):
    an = type(a) is int or type(a) is float
    bn = type(b) is int or type(b) is float
    if an and bn:
        return (a > b) - (a < b)
    if type(a) is str and type(b) is str:
        return (a > b) - (a < b)
    _err("sort() default mengharapkan number atau string sejenis, "
         "didapat {0} dan {1}".format(type_name(a), type_name(b)))


def _sort(vm, arr, *f):
    assert_array(arr, "sort()")
    import functools
    result = list(arr)
    if f:
        cmp = _callable(f[0], "sort()")
        key = functools.cmp_to_key(
            lambda a, b: _call(vm, cmp, [a, b]))
    else:
        key = functools.cmp_to_key(_default_cmp)
    try:
        result.sort(key=key)
    except CrescentRuntimeError:
        raise
    except TypeError:
        _err("sort(): elemen tidak dapat dibandingkan")
    return result


def _iter_internal(vm, obj, i):
    """Dipakai compiler untuk for-in: [indeks_berikut, nilai] atau nil."""
    if type(i) is not int or i < 0:
        _err("kesalahan internal __iter: indeks tidak valid")
    t = type(obj)
    if t is list:
        if i >= len(obj):
            return None
        return [i + 1, obj[i]]
    if t is str:
        if i >= len(obj):
            return None
        return [i + 1, obj[i]]
    if t is dict:
        ks = list(obj.keys())
        if i >= len(ks):
            return None
        return [i + 1, ks[i]]
    _err("for-in mengharapkan array, string, atau map, didapat {0}"
         .format(type_name(obj)))


# ----------------------------------------------------------- instalasi

def install_builtins(vm):
    """Daftarkan semua builtin ke globals VM."""
    natives = [
        ObjNative("len", 1, _len),
        ObjNative("push", 2, _push),
        ObjNative("pop", 1, _pop),
        ObjNative("keys", 1, _keys),
        ObjNative("values", 1, _values),
        ObjNative("has", 2, _has),
        ObjNative("del", 2, _del),
        ObjNative("str", 1, _str),
        ObjNative("num", 1, _num),
        ObjNative("type", 1, _type),
        ObjNative("abs", 1, _abs),
        ObjNative("floor", 1, _floor),
        ObjNative("ceil", 1, _ceil),
        ObjNative("sqrt", 1, _sqrt),
        ObjNative("min", -1, _min, min_arity=1),
        ObjNative("max", -1, _max, min_arity=1),
        ObjNative("range", -1, _range, min_arity=1),
        ObjNative("clock", 0, _clock),
        ObjNative("random", -1, _random, min_arity=0),
        ObjNative("join", 2, _join),
        ObjNative("split", 2, _split),
        ObjNative("upper", 1, _upper),
        ObjNative("lower", 1, _lower),
        ObjNative("replace", 3, _replace),
        ObjNative("trim", 1, _trim),
        ObjNative("ord", 1, _ord),
        ObjNative("chr", 1, _chr),
        ObjNative("map", 2, _map_fn),
        ObjNative("filter", 2, _filter),
        ObjNative("reduce", 3, _reduce),
        ObjNative("sort", -1, _sort, min_arity=1),
        ObjNative("__iter", 2, _iter_internal),
    ]
    for n in natives:
        vm.globals[n.name] = n
