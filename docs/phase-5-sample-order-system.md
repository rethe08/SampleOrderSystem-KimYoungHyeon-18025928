# phase-5-sample-order-system.md - 최종 통합 프로그램 (개요)

## 개요
- 목적: Phase 1~4의 설계·구현을 통합하여 PRD.md 전체 기능을 갖춘 완성 프로그램 구현
- 폴더: `5_SampleOrderSystem-yhyeon08.kim-18025928/`
- 데이터: JSON 파일 영속성 (`data/samples.json`, `data/orders.json`)
- 아키텍처: MVC 패턴 + Repository 계층 + 생산 큐(FIFO)

---

## Sub-Phase 목록

| Sub-Phase | 이름 | 세부 문서 | 상태 |
|-----------|------|-----------|------|
| 5-1 | 프로젝트 구조 설정 | phase-5-1-project-setup.md | 완료 |
| 5-2 | 도메인 모델 및 영속성 계층 | phase-5-2-model-repository.md | 완료 |
| 5-3 | 시료 관리 기능 | phase-5-3-sample-management.md | 완료 |
| 5-4 | 시료 주문 및 승인·거절 기능 | phase-5-4-order-management.md | 완료 |
| 5-5 | 생산라인 기능 | phase-5-5-production.md | 미착수 |
| 5-6 | 모니터링 및 출고 처리 기능 | phase-5-6-monitoring-release.md | 미착수 |
| 5-7 | main.py 통합 | phase-5-7-main.md | 미착수 |

---

## 최종 디렉토리 구조

```
5_SampleOrderSystem-yhyeon08.kim-18025928/
├── model/
│   ├── __init__.py
│   ├── sample.py              # Sample 도메인 모델 (to_dict/from_dict 포함)
│   └── order.py               # Order 도메인 모델 (to_dict/from_dict 포함)
├── repository/
│   ├── __init__.py
│   ├── base_repository.py     # JSON CRUD 추상 클래스
│   ├── sample_repository.py   # Sample JSON CRUD
│   └── order_repository.py    # Order JSON CRUD
├── controller/
│   ├── __init__.py
│   ├── sample_controller.py   # 시료 관리 비즈니스 로직
│   ├── order_controller.py    # 주문 접수·승인·거절 비즈니스 로직
│   ├── production_controller.py # 생산라인 관리 비즈니스 로직
│   └── monitoring_controller.py # 모니터링·출고 비즈니스 로직
├── view/
│   ├── __init__.py
│   ├── sample_view.py         # 시료 관련 입출력
│   ├── order_view.py          # 주문 관련 입출력
│   ├── production_view.py     # 생산라인 관련 입출력
│   └── monitoring_view.py     # 모니터링·출고 관련 입출력
├── data/
│   ├── samples.json
│   └── orders.json
├── tests/
│   ├── __init__.py
│   ├── test_sample_model.py
│   ├── test_order_model.py
│   ├── test_sample_repository.py
│   ├── test_order_repository.py
│   ├── test_sample_controller.py
│   ├── test_order_controller.py
│   ├── test_production_controller.py
│   └── test_monitoring_controller.py
├── main.py
├── requirements.txt
└── .gitignore
```

---

## PRD.md → Phase 5 기능 매핑

| PRD 메뉴 | Sub-Phase | 구현 내용 |
|----------|-----------|-----------|
| 시료 관리 | 5-3 | 등록 / 목록 조회 / 이름 검색 |
| 시료 주문 | 5-4 | 주문 접수 (RESERVED) |
| 주문 승인/거절 | 5-4 | 승인(재고 확인→CONFIRMED/PRODUCING) / 거절(REJECTED) |
| 모니터링 | 5-6 | 상태별 주문 수 / 시료별 재고 상태 |
| 생산라인 | 5-5 | 생산 현황 / 대기 큐 / 생산 완료 처리 |
| 출고 처리 | 5-6 | CONFIRMED → RELEASE |

---

## 주문 상태 흐름 (PRD §3 기준)

```
RESERVED → (승인) → 재고 충분  → CONFIRMED → RELEASE
                 → 재고 부족  → PRODUCING → CONFIRMED → RELEASE
         → (거절) → REJECTED
```

## MVC 역할 분리 원칙

| 레이어 | 허용 | 금지 |
|--------|------|------|
| Model | 데이터 구조, 유효성 검증, 직렬화 | Controller·View import |
| Repository | JSON 파일 CRUD | 비즈니스 로직 |
| Controller | 비즈니스 로직, Repository 사용 | View import |
| View | 입출력, Model 타입 참조 | Controller import, 비즈니스 로직 |
| main.py | Controller·View 연결 | 비즈니스 로직 직접 구현 |
