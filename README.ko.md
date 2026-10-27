# Crescent

![crescent](https://raw.githubusercontent.com/lunarjjo/crescent/main/gallery-badge/lunar__crescent__v0.1.0.svg)
[![CI](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml/badge.svg)](https://github.com/lunarjjo/crescent/actions/workflows/ci.yml)

<div align="center">

<sub>🌐 <a href="README.md">English</a> · <a href="README.id.md">Bahasa Indonesia</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.pt.md">Português</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh-CN.md">简体中文</a> · **한국어** · <a href="README.hi.md">हिन्दी</a></sub>

</div>

> 작은 동적 언어 — **렉서 → 파서 → 바이트코드 컴파일러 → 가상 머신**. 처음부터 직접 구축, 100% Python 표준 라이브러리, 의존성 0.

Crescent은 프로그래밍 언어가 어떻게 동작하는지 읽기 쉽게 보여주는 연구입니다. 모든 단계 — 토큰, AST, 16비트 바이트코드, 셀 기반 프레임, 클로저 — 전부 손으로 작성되었습니다. 언어 자체도 쾌적합니다: 진짜 클로저, 리터럴 데이터 구조, 함수형 표준 라이브러리(map/filter/reduce/sort), 대화형 REPL, 위치가 있는 오류 메시지.

## 특징

- **완전한 파이프라인** — 렉서, 파서, 바이트코드 컴파일러, VM (38 옵코드)
- **진짜 클로저** — 셀 기반 캡처, 반복마다 독립적인 루프 변수
- **함수형 표준 라이브러리** — 비교자를 받는 map / filter / reduce / sort (32 내장)
- **REPL + 디스어셈블러** — --tokens / --ast / --bytecode 플래그
- **140개 테스트 통과** — 렉서, 파서, VM, REPL, CLI + 결정적 예제
- **의존성 0** — 100% Python 표준 라이브러리(3.8+), 폴더 복사만 하면 됨

## 빠른 시작

```bash
python3 -m crescent                         # interactive REPL
python3 -m crescent examples/fibonacci.cres # run a file
pip install git+https://github.com/lunarjjo/crescent.git
```

## 라이선스

MIT — see [LICENSE](LICENSE).

---

*이 번역은 핵심만 담고 있습니다. 전체 문서는 [영어 README](README.md)를 참고하세요.*
