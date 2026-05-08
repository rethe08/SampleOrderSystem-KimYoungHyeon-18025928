# phase-5-2-model-repository.md - 도메인 모델 및 영속성 계층

## 목표
Sample·Order 도메인 모델과 JSON 파일 기반 Repository 계층을 구현한다.
Phase 2(DataPersistence)의 설계를 그대로 계승한다.

---

## 구현 항목

### Model

**`model/sample.py`** — `Sample` 클래스
- 속성: `id: str`, `name: str`, `avg_production_time: float`, `yield_rate: float`, `stock: int`
- 유효성 검증 (생성자):
  - `yield_rate`: 0.0 이상 1.0 이하, 위반 시 `ValueError`
  - `avg_production_time`: 0 초과, 위반 시 `ValueError`
  - `stock`: 0 이상, 위반 시 `ValueError`
- `to_dict() -> dict` — JSON 직렬화
- `from_dict(d: dict) -> Sample` — JSON 역직렬화 (classmethod)

**`model/order.py`** — `Order` 클래스
- 속성:
  - `order_id: str` — 형식: `ORD-YYYYMMDD-XXXX`
  - `sample_id: str`
  - `customer_name: str`
  - `quantity: int` — 0 초과, 위반 시 `ValueError`
  - `status: str` — `RESERVED / REJECTED / PRODUCING / CONFIRMED / RELEASE` 중 하나
- `to_dict() -> dict`
- `from_dict(d: dict) -> Order` (classmethod)

---

### Repository

**`repository/base_repository.py`** — `JsonRepository` 추상 클래스
- `__init__(self, file_path: str)` — JSON 파일 경로 주입
- `_load() -> dict[str, dict]` — JSON 파일 읽기 (파일 없으면 빈 dict 반환)
- `_save(data: dict[str, dict])` — JSON 파일 쓰기
- 추상 메서드: `create`, `read`, `update`, `delete`, `list_all`

**`repository/sample_repository.py`** — `SampleRepository(JsonRepository)`
- `create(sample: Sample)` — 추가; 중복 ID 시 `ValueError`
- `read(id: str) -> Sample | None` — 없으면 `None`
- `update(sample: Sample)` — 덮어쓰기; 미존재 시 `KeyError`
- `delete(id: str)` — 삭제; 미존재 시 `KeyError`
- `list_all() -> list[Sample]` — 등록 순서대로 반환 (Python 3.7+ dict 삽입 순서에 의존)

**`repository/order_repository.py`** — `OrderRepository(JsonRepository)`
- PRD에 주문 삭제 기능 없으므로 `delete`는 구현하지 않음 (`raise NotImplementedError` 처리)
- 그 외 `create`, `read`, `update`, `list_all`은 `SampleRepository`와 동일 패턴
- `list_by_status(status: str) -> list[Order]` — 특정 상태의 주문 목록 반환
- `order_id` 생성은 호출자(controller)가 담당; Repository는 생성하지 않음
  - 형식: `ORD-{날짜 8자리}-{4자리 시퀀스}` (예: `ORD-20260508-0001`)
  - 시퀀스: `list_all()`에서 당일 최대 시퀀스 + 1 (controller에서 계산)

---

## JSON 파일 형식

**`data/samples.json`**
```json
{
  "S-001": {
    "id": "S-001",
    "name": "실리콘 웨이퍼-8인치",
    "avg_production_time": 0.5,
    "yield_rate": 0.92,
    "stock": 100
  }
}
```

**`data/orders.json`**
```json
{
  "ORD-20260508-0001": {
    "order_id": "ORD-20260508-0001",
    "sample_id": "S-001",
    "customer_name": "삼성전자",
    "quantity": 100,
    "status": "RESERVED"
  }
}
```

---

## 단위 테스트

**`tests/test_sample_model.py`** (5개)
- `test_create_success` — 정상 생성
- `test_yield_rate_boundary` — 0.0, 1.0 허용 / 1.1, -0.1 ValueError
- `test_avg_time_zero_raises` — avg_production_time=0 → ValueError
- `test_stock_negative_raises` — stock=-1 → ValueError
- `test_to_dict_from_dict_roundtrip` — 직렬화 후 역직렬화 동등성 확인

**`tests/test_order_model.py`** (3개)
- `test_create_success` — 정상 생성
- `test_quantity_zero_raises` — quantity=0 → ValueError
- `test_to_dict_from_dict_roundtrip` — 직렬화 후 역직렬화 동등성 확인

**`tests/test_sample_repository.py`** (6개, `tmp_path` fixture 사용)
- `test_create_and_read`
- `test_read_not_found`
- `test_update`
- `test_update_not_found_raises`
- `test_delete`
- `test_list_all`

**`tests/test_order_repository.py`** (5개, `tmp_path` fixture 사용)
- `test_create_and_read`
- `test_update_status`
- `test_delete_raises_not_implemented` — delete() 호출 시 NotImplementedError 발생 확인
- `test_list_by_status`
- `test_persistence` — 재인스턴스 후 데이터 유지 확인

---

## 체크리스트

- [x] `model/sample.py` 구현 (유효성 검증 + to_dict/from_dict)
- [x] `model/order.py` 구현 (유효성 검증 + to_dict/from_dict)
- [x] `repository/base_repository.py` 추상 클래스 구현
- [x] `repository/sample_repository.py` CRUD 구현
- [x] `repository/order_repository.py` CRUD + `list_by_status()` 구현
- [x] `data/` 초기 빈 JSON 파일 확인
- [x] 단위 테스트 19개 작성 및 전체 PASS (tmp_path 사용)
