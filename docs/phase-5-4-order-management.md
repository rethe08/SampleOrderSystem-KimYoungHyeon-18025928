# phase-5-4-order-management.md - 시료 주문 및 승인·거절 기능

## 목표
PRD §5.2(시료 주문)와 §5.3(주문 승인/거절)을 구현한다.
승인 시 재고 상황에 따라 CONFIRMED 또는 PRODUCING으로 자동 분기한다.

---

## 구현 항목

### `controller/order_controller.py` — `OrderController`

```python
# 의존: OrderRepository, SampleRepository(재고 확인·차감용)
#
# __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository)
#
# create_order(sample_id: str, customer_name: str, quantity: int) -> Order
#   - sample_id 미등록 시 ValueError ("등록되지 않은 시료입니다.")
#   - quantity <= 0 시 ValueError
#   - order_id 자동 생성: ORD-YYYYMMDD-XXXX
#     - 오늘 날짜 기준 orders.json 내 최대 시퀀스 + 1
#   - status = RESERVED 로 생성
#   - order_repo.create() 후 Order 반환
#
# get_reserved_orders() -> list[Order]
#   - order_repo.list_by_status("RESERVED") 반환
#
# approve_order(order_id: str) -> str
#   - 대상 주문: RESERVED 상태여야 함, 아니면 ValueError
#   - 재고 확인: sample.stock >= order.quantity
#     - 재고 충분: stock 차감 → sample_repo.update() → order.status = CONFIRMED
#     - 재고 부족: order.status = PRODUCING
#       (별도 enqueue 호출 없음 — PRODUCING 상태 주문이 곧 생산 큐 항목임.
#        ProductionController.get_production_queue()가 list_by_status("PRODUCING")으로 조회)
#   - order_repo.update() 후 최종 status 반환 ("CONFIRMED" 또는 "PRODUCING")
#
# reject_order(order_id: str)
#   - 대상 주문: RESERVED 상태여야 함, 아니면 ValueError
#   - order.status = REJECTED → order_repo.update()
```

### `view/order_view.py` — `OrderView`

> **메뉴 분리 방침**: main.py의 [2] 시료 주문과 [3] 주문 승인/거절은 별개 진입점이다.
> - [2] 진입 시: input_order_data() 직접 호출 (서브루프 없이 주문 접수 단일 동작)
> - [3] 진입 시: show_order_menu() 서브루프 ([1] 목록, [2] 승인, [3] 거절, [0] 돌아가기)

```python
# show_order_menu() -> None   ← [3] 주문 승인/거절 진입 시 서브루프용
#   [1] 접수된 주문 목록 조회 (RESERVED)
#   [2] 주문 승인
#   [3] 주문 거절
#   [0] 메인 메뉴로 돌아가기
#
# show_order_list(orders: list[Order]) -> None
#   - 컬럼: 주문번호 | 시료ID | 고객명 | 수량 | 상태
#   - 빈 목록: "접수된 주문이 없습니다." 출력
#
# show_message(msg: str) -> None
#
# input_order_data() -> dict
#   - 반환: {"sample_id": str, "customer_name": str, "quantity": int}
#
# input_order_id(prompt: str) -> str
#   - 승인/거절 대상 주문번호 입력
#
# get_user_choice() -> str
```

---

## 주문 ID 자동 생성 규칙

```
형식: ORD-{YYYYMMDD}-{XXXX}
예:   ORD-20260508-0001

시퀀스 결정:
  1. order_repo.list_all()에서 오늘 날짜(YYYYMMDD) 기준 order_id 필터
  2. 해당 날짜의 최대 시퀀스 번호 추출
  3. 최대 + 1 (없으면 1)
  4. 4자리 zero-padding
```

---

## 승인 분기 로직 (PRD §5.3.2)

```
approve_order(order_id):
  order = order_repo.read(order_id)
  sample = sample_repo.read(order.sample_id)

  if sample.stock >= order.quantity:
      sample.stock -= order.quantity
      sample_repo.update(sample)
      order.status = "CONFIRMED"
  else:
      order.status = "PRODUCING"   # PRODUCING 상태 = 큐 항목. 별도 enqueue 불필요

  order_repo.update(order)
  return order.status
```

---

## 단위 테스트

**`tests/test_order_controller.py`** (8개, `tmp_path` fixture 사용)
- `test_create_order_success`
- `test_create_order_invalid_sample_raises`
- `test_create_order_id_format` — `ORD-YYYYMMDD-XXXX` 형식 확인
- `test_approve_order_sufficient_stock` — 재고 충분 → CONFIRMED, 재고 차감 확인
- `test_approve_order_insufficient_stock` — 재고 부족 → PRODUCING
- `test_approve_order_wrong_status_raises` — RESERVED 아닌 주문 승인 → ValueError
- `test_reject_order_success` — RESERVED → REJECTED
- `test_reject_order_wrong_status_raises` — RESERVED 아닌 주문 거절 → ValueError

---

## 체크리스트

- [x] `controller/order_controller.py` 구현 (4개 메서드 + order_id 생성 로직)
- [x] `view/order_view.py` 구현 (6개 메서드)
- [x] 단위 테스트 8개 작성 및 전체 PASS
- [x] 승인 시 재고 차감 동작 확인 (CONFIRMED 경로)
- [x] 승인 시 PRODUCING 전환 동작 확인 (재고 부족 경로)
- [x] Controller 내 View import 없음 확인
- [x] View 내 Controller/Repository import 없음 확인
