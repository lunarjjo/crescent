# Contoh Program Crescent

Setiap contoh di bawah ini **dijalankan sungguhan** oleh interpreter
saat dokumen ini diregenerasi — output yang tampil adalah output
asli VM, bukan ditulis tangan.

---

## FizzBuzz — kontrol alir klasik

```crescent
// fizzbuzz.cres — klasik yang wajib ada
for i in range(1, 21) {
  if i % 15 == 0 {
    print "FizzBuzz"
  } else if i % 3 == 0 {
    print "Fizz"
  } else if i % 5 == 0 {
    print "Buzz"
  } else {
    print i
  }
}
```

Output:

```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
16
17
Fizz
19
Buzz
```

---

## Fibonacci — rekursi + memoization via closure

```crescent
// fibonacci.cres — rekursi + memoization dengan closure
fn buatFib() {
  let memo = {}

  fn fib(n) {
    if n < 2 { return n }
    if has(memo, n) { return memo[n] }
    let hasil = fib(n - 1) + fib(n - 2)
    memo[n] = hasil
    return hasil
  }

  return fib
}

let fib = buatFib()

// tanpa memo ini akan ~1 juta panggilan
for n in [10, 20, 30, 40, 50] {
  print "fib(" + str(n) + ") = " + str(fib(n))
}
```

Output:

```
fib(10) = 55
fib(20) = 6765
fib(30) = 832040
fib(40) = 102334155
fib(50) = 12586269025
```

---

## Closures — counter berbagi vs per instansi

```crescent
// closures.cres — dunia closure: counter berbagi vs per instansi
fn buatCounter(nama) {
  let n = 0

  return fn() {
    n = n + 1
    return nama + " ke-" + str(n)
  }
}

let a = buatCounter("alpha")
let b = buatCounter("beta")

print a()   // alpha ke-1
print a()   // alpha ke-2 — sel milik alpha sendiri
print b()   // beta ke-1  — sel beta terpisah

// adder: closure menangkap parameter (tetap hidup setelah frame selesai)
fn buatAdder(x) {
  return fn(y) { return x + y }
}
let tambah10 = buatAdder(10)
let tambahPesan = buatAdder(1)

print tambah10(5), tambahPesan(5)

// closure per iterasi — seperti JS `let`
let fns = []
for i in [1, 2, 3] {
  push(fns, fn() { return i * 100 })
}
print fns[0](), fns[1](), fns[2]()
```

Output:

```
alpha ke-1
alpha ke-2
beta ke-1
15 6
100 200 300
```

---

## Fungsi orde tinggi — map/filter/reduce/sort

```crescent
// higher_order.cres — map, filter, reduce, sort dengan closure
let angka = [5, 3, 8, 1, 9, 2, 7]

let kuadrat = map(angka, fn(x) { return x * x })
print "kuadrat      :", kuadrat

let genap = filter(angka, fn(x) { return x % 2 == 0 })
print "genap        :", genap

let total = reduce(angka, fn(a, x) { return a + x }, 0)
print "total        :", total

let terurut = sort(angka)
print "terurut naik :", terurut

// komparator kustom: menurun
let menurun = sort(angka, fn(a, b) { return b - a })
print "terurut turun:", menurun

// komparator kustom: angka ganjil dulu, lalu menaik
let ganjilDulu = sort(angka, fn(a, b) {
  if a % 2 != b % 2 {
    if a % 2 == 1 { return -1 }
    return 1
  }
  return a - b
})
print "ganjil dulu :", ganjilDulu

// pipeline: filter -> map -> reduce dalam satu aliran
let hasil = reduce(
  map(filter(angka, fn(x) { return x > 3 }), fn(x) { return x * 10 }),
  fn(a, x) { return a + x },
  0
)
print "pipeline     :", hasil
```

Output:

```
kuadrat      : [25, 9, 64, 1, 81, 4, 49]
genap        : [8, 2]
total        : 35
terurut naik : [1, 2, 3, 5, 7, 8, 9]
terurut turun: [9, 8, 7, 5, 3, 2, 1]
ganjil dulu : [1, 3, 5, 7, 9, 2, 8]
pipeline     : 290
```

---

## Sieve of Eratosthenes — array & loop while

```crescent
// primes.cres — sieve of Eratosthenes dengan array
fn sieve(batas) {
  let penanda = []
  for _ in range(batas + 1) {
    push(penanda, true)
  }

  let hasil = []
  let i = 2
  while i <= batas {
    if penanda[i] {
      push(hasil, i)
      let j = i * i
      while j <= batas {
        penanda[j] = false
        j = j + i
      }
    }
    i = i + 1
  }
  return hasil
}

let prima = sieve(100)
print "ada " + str(len(prima)) + " bilangan prima <= 100:"
print prima

// jumlah dan rata-rata pakai reduce
let total = reduce(prima, fn(a, x) { return a + x }, 0)
print "jumlah = " + str(total) + ", rata-rata = " + str(total / len(prima))
```

Output:

```
ada 25 bilangan prima <= 100:
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
jumlah = 1060, rata-rata = 42.4
```

---

## Word count — map + string tools

```crescent
// wordcount.cres — hitung frekuensi kata: map + string tools
fn wordcount(teks) {
  let frek = {}
  for kata in split(lower(teks), " ") {
    let bersih = trim(kata)
    if len(bersih) == 0 { continue }
    if has(frek, bersih) {
      frek[bersih] = frek[bersih] + 1
    } else {
      frek[bersih] = 1
    }
  }
  return frek
}

let teks = "bulan bersinar di malam hari dan malam itu dingin " +
           "karena angin malam berembus perlahan"

let frek = wordcount(teks)
print "frekuensi kata:"
for k in frek {
  print "  " + k + " = " + str(frek[k])
}

// kata paling sering via reduce
let terbanyak = reduce(keys(frek), fn(best, k) {
  if frek[k] > frek[best] { return k }
  return best
}, keys(frek)[0])
print "kata terbanyak: " + terbanyak + " (" + str(frek[terbanyak]) + "x)"
```

Output:

```
frekuensi kata:
  bulan = 1
  bersinar = 1
  di = 1
  malam = 3
  hari = 1
  dan = 1
  itu = 1
  dingin = 1
  karena = 1
  angin = 1
  berembus = 1
  perlahan = 1
kata terbanyak: malam (3x)
```

---

## Matriks — array nested & indeks

```crescent
// matrix.cres — perkalian matriks dengan array nested
fn matriks(a, b) {
  let n = len(a)
  let m = len(b[0])
  let k = len(b)

  let c = []
  for i in range(n) {
    let baris = []
    for j in range(m) {
      push(baris, 0)
    }
    push(c, baris)
  }

  for i in range(n) {
    for j in range(m) {
      let s = 0
      for t in range(k) {
        s = s + a[i][t] * b[t][j]
      }
      c[i][j] = s
    }
  }
  return c
}

fn tampil(x) {
  for baris in x {
    print baris
  }
}

let A = [[1, 2], [3, 4]]
let B = [[5, 6], [7, 8]]

print "A x B ="
tampil(matriks(A, B))

let C = [[1, 2, 3], [4, 5, 6]]     // 2x3
let D = [[7, 8], [9, 10], [11, 12]] // 3x2

print "C x D ="
tampil(matriks(C, D))

// transpos: baris jadi kolom
fn transpos(x) {
  let hasil = []
  for j in range(len(x[0])) {
    let kolom = []
    for i in range(len(x)) {
      push(kolom, x[i][j])
    }
    push(hasil, kolom)
  }
  return hasil
}

print "transpos(B) ="
tampil(transpos(B))
```

Output:

```
A x B =
[19, 22]
[43, 50]
C x D =
[58, 64]
[139, 154]
transpos(B) =
[5, 7]
[6, 8]
```

---

## Mini memory bank — 'luna' dalam 50 baris Crescent

```crescent
// agent_memory.cres — "mini luna": bank memori sederhana ala agen
// dedikasi untuk kasyaira/luna — inspirasi arsitektur 5 bank memori

fn buatMemori() {
  let semantik = {}    // fakta jangka panjang
  let episodik = []    // kejadian berurutan

  return {
    ingat: fn(kunci, nilai) {
      semantik[kunci] = nilai
      push(episodik, "ingat: " + kunci)
      return nil
    },
    ambil: fn(kunci) {
      if has(semantik, kunci) { return semantik[kunci] }
      return "tidak ada: " + kunci
    },
    lupa: fn(kunci) {
      if has(semantik, kunci) {
        del(semantik, kunci)
        push(episodik, "lupa: " + kunci)
      }
      return nil
    },
    jejak: fn() {
      return episodik
    },
    ringkas: fn() {
      return str(len(semantik)) + " fakta, " + str(len(episodik)) + " kejadian"
    }
  }
}

let mem = buatMemori()

mem.ingat("pemilik", "kasyaira")
mem.ingat("misi", "bantu pemilik tanpa diminta")
mem.ingat("bahasa", "Crescent")

print mem.ringkas()
print "misi      -> " + mem.ambil("misi")
print "pemilik   -> " + mem.ambil("pemilik")
print "tidakada  -> " + mem.ambil("tidakada")

mem.lupa("bahasa")
print mem.ringkas()
print "jejak: " + join(mem.jejak(), ", ")
```

Output:

```
3 fakta, 3 kejadian
misi      -> bantu pemilik tanpa diminta
pemilik   -> kasyaira
tidakada  -> tidak ada: tidakada
2 fakta, 4 kejadian
jejak: ingat: pemilik, ingat: misi, ingat: bahasa, lupa: bahasa
```

