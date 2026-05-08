# phase-5-1-project-setup.md - 프로젝트 구조 설정

## 목표
Phase 5 최종 프로그램의 패키지 폴더 구조와 기반 파일을 생성한다.
코드 구현은 하지 않으며, 구조와 설정 파일만 완성한다.

---

## 생성할 파일 및 폴더

```
5_SampleOrderSystem-yhyeon08.kim-18025928/
├── model/
│   └── __init__.py          # 빈 파일
├── repository/
│   └── __init__.py          # 빈 파일
├── controller/
│   └── __init__.py          # 빈 파일
├── view/
│   └── __init__.py          # 빈 파일
├── tests/
│   └── __init__.py          # 빈 파일
├── data/
│   ├── samples.json         # 초기 빈 JSON: {}
│   └── orders.json          # 초기 빈 JSON: {}
├── requirements.txt
└── .gitignore
```

---

## `requirements.txt`

```
pytest==8.3.5
```

## `.gitignore`

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/
.venv/
venv/
data/
```

> `data/` 는 런타임 생성 파일이므로 git 추적 제외한다.

---

## 체크리스트

- [x] model/ 폴더 및 `__init__.py` 생성
- [x] repository/ 폴더 및 `__init__.py` 생성
- [x] controller/ 폴더 및 `__init__.py` 생성
- [x] view/ 폴더 및 `__init__.py` 생성
- [x] tests/ 폴더 및 `__init__.py` 생성
- [x] data/ 폴더 및 초기 빈 JSON 파일 2개 생성
- [x] `requirements.txt` 작성
- [x] `.gitignore` 작성
- [x] `pytest` 설치 및 실행 확인 (테스트 없음 상태에서 오류 없이 종료)
