"""Lexer Crescent — mengubah sumber menjadi deretan token.

Aturan:
- Baris baru MENGAKHIRI pernyataan (newline-aware), tetapi diabaikan saat
  berada di dalam ``(...)`` / ``[...]`` sehingga argumen dan elemen array
  boleh dilipat lintas baris. Kurung kurawal TIDAK menekan newline karena
  berperan ganda (blok vs literal map) — parser map melompatinya sendiri.
- Komentar satu baris: ``//`` sampai akhir baris.
- String: ``"..."`` atau ``'...'`` dengan escape ``\\n \\t \\r \\\\ \\" \\' \\0``.
- Angka: integer atau float (``1.5``); tidak ada oktal/heksadesimal.
"""
from .errors import CrescentSyntaxError

KEYWORDS = {
    "let", "fn", "if", "else", "while", "for", "in", "return",
    "break", "continue", "true", "false", "nil", "print",
    "and", "or", "not",
}

TWO_CHAR = {"==", "!=", "<=", ">="}

SINGLE = set("+-*/%<>=(){}[],;:.")

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"',
           "'": "'", "0": "\0"}


class Token:
    __slots__ = ("type", "value", "line", "col")

    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return "Token({0}, {1!r}, {2}:{3})".format(
            self.type, self.value, self.line, self.col)


def tokenize(src):
    """Kembalikan daftar token diakhiri token EOF.

    Baris baru selalu menjadi token NEWLINE — tanpa pengecualian. Parser
    yang tahu kapan newline boleh dilompati (titik kontinuasi ekspresi).
    """
    tokens = []
    i = 0
    line = 1
    col = 1
    n = len(src)

    def error(msg, l=None, c=None):
        raise CrescentSyntaxError(msg, l or line, c or col)

    while i < n:
        ch = src[i]

        # spasi putih horizontal
        if ch in " \t\r":
            i += 1
            col += 1
            continue

        # baris baru — SELALU jadi token
        if ch == "\n":
            tokens.append(Token("NEWLINE", "\n", line, col))
            i += 1
            line += 1
            col = 1
            continue

        # komentar //
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
                col += 1
            continue

        # angka
        if ch.isdigit():
            start = i
            start_col = col
            while i < n and src[i].isdigit():
                i += 1
                col += 1
            is_float = False
            if i + 1 < n and src[i] == "." and src[i + 1].isdigit():
                is_float = True
                i += 2
                col += 2
                while i < n and src[i].isdigit():
                    i += 1
                    col += 1
            text = src[start:i]
            value = float(text) if is_float else int(text)
            tokens.append(Token("NUMBER", value, line, start_col))
            continue

        # string
        if ch in ('"', "'"):
            quote = ch
            start_col = col
            i += 1
            col += 1
            buf = []
            while True:
                if i >= n:
                    error("string tidak ditutup", line, start_col)
                c = src[i]
                if c == quote:
                    i += 1
                    col += 1
                    break
                if c == "\n":
                    error("string tidak ditutup sebelum baris baru",
                          line, start_col)
                if c == "\\":
                    if i + 1 >= n:
                        error("escape tidak lengkap")
                    e = src[i + 1]
                    if e not in ESCAPES:
                        error("escape tidak dikenal: \\{0}".format(e))
                    buf.append(ESCAPES[e])
                    i += 2
                    col += 2
                    continue
                buf.append(c)
                i += 1
                col += 1
            tokens.append(Token("STRING", "".join(buf), line, start_col))
            continue

        # identifier / keyword
        if ch.isalpha() or ch == "_":
            start = i
            start_col = col
            while i < n and (src[i].isalnum() or src[i] == "_"):
                i += 1
                col += 1
            word = src[start:i]
            if word in KEYWORDS:
                tokens.append(Token(word, word, line, start_col))
            else:
                tokens.append(Token("IDENT", word, line, start_col))
            continue

        # operator dua karakter
        pair = src[i:i + 2]
        if pair in TWO_CHAR:
            tokens.append(Token(pair, pair, line, col))
            i += 2
            col += 2
            continue

        # operator/karakter tunggal
        if ch in SINGLE:
            tokens.append(Token(ch, ch, line, col))
            i += 1
            col += 1
            continue

        error("karakter tidak dikenal: {0!r}".format(ch))

    tokens.append(Token("EOF", None, line, col))
    return tokens
