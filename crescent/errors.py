"""Jenis kesalahan Crescent — semua membawa info posisi sumber."""


class CrescentError(Exception):
    """Dasar semua kesalahan Crescent."""

    def __init__(self, msg, line, col=0):
        super().__init__(msg)
        self.msg = msg
        self.line = line
        self.col = col

    def format(self):
        pos = "baris {0}".format(self.line)
        if self.col:
            pos += ":{0}".format(self.col)
        return "{0}: {1}".format(pos, self.msg)


class CrescentSyntaxError(CrescentError):
    """Kesalahan leksikal / parsing."""

    def __str__(self):
        return "SyntaxError: " + self.format()


class CrescentCompileError(CrescentError):
    """Kesalahan kompilasi (resolusi nama, return di luar fn, dll)."""

    def __init__(self, msg, line):
        super().__init__(msg, line)

    def __str__(self):
        return "CompileError: " + self.format()


class CrescentRuntimeError(CrescentError):
    """Kesalahan saat eksekusi bytecode di VM.

    traceback: daftar (nama_fungsi, baris) dari frame terdalam ke terluar.
    """

    def __init__(self, msg, line, traceback=None):
        super().__init__(msg, line)
        self.traceback = traceback or []

    def __str__(self):
        out = ["RuntimeError: baris {0}: {1}".format(self.line, self.msg)]
        for name, line in self.traceback:
            label = "<script>" if not name else "fn {0}".format(name)
            out.append("  pada {0} (baris {1})".format(label, line))
        return "\n".join(out)
