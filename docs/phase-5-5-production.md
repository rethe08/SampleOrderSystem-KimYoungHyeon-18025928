# phase-5-5-production.md - 생산라인 기능

## 목표
PRD §5.5와 §6의 생산라인 기능을 구현한다.
PRODUCING 상태 주문을 FIFO 큐로 관리하고, 생산 완료 시 CONFIRMED으로 전환한다.

---

## 생산량 계산 공식 (PRD §5.5.1)

```
실 생산량 = ceil(부족분 / (수율 × 0.9))
총 생산 시간 = 평균 생산시간 × 실 생산량

부족분 = order.quantity - sample.stock
  (stock=0이면 부족분=quantity가 자동 성립 — 특수 처리 불필요)
```

## 생산 현황 표기 (PRD §5.5.3)

이 시스템은 실시간 생산 진행을 추적하지 않는 상태 기반(state-based) 시스템이다.
PRD §5.5.3의 "현재까지의 생산량"은 `get_production_info()`의 `actual_production`
(계획 실 생산량)으로 대체하여 표시한다. 부분 생산량 추적은 구현하지 않는다.
> **설계 결정 승인 (plan.md §PRD 불일치 사항 참조):** PoC 범위에서 실시간 진행량
> 추적은 불필요하다고 판단. actual_production(계획값) 표시로 대체함이 승인됨.

---

## 구현 항목

### `controller/production_controller.py` — `ProductionController`

```python
# 의존: OrderRepository, SampleRepository
#
# __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository)
#
# get_production_queue() -> list[Order]
#   - order_repo.list_by_status("PRODUCING") 반환 (FIFO: 주문 접수 순서)
#   - 정렬 기준: order_id 오름차순 (ORD-날짜-시퀀스 형식이므로 문자열 정렬로 FIFO 보장)
#
# get_production_info(order_id: str) -> dict
#   - PRODUCING 상태 주문의 생산 정보 계산 및 반환
#   - 반환:
#     {
#       "order": Order,
#       "sample": Sample,
#       "shortage": int,          # 부족분 = quantity - stock (stock이 0이면 quantity)
#       "actual_production": int, # ceil(부족분 / (수율 × 0.9))
#       "total_time": float,      # 평균생산시간 × 실 생산량
#     }
#   - 미존재 order_id 시 ValueError
#   - PRODUCING 상태가 아닌 주문 시 ValueError
#
# complete_production(order_id: str) -> Order
#   - PRODUCING 상태 주문을 CONFIRMED으로 전환
#   - 생산된 시료를 재고에 반영:
#       new_stock = sample.stock + actual_production - order.quantity
#       (실 생산량에서 주문 수량을 충당하고 남은 수량을 재고로 추가)
#   - sample_repo.update(sample) + order_repo.update(order) 후 Order 반환
#   - PRODUCING 상태가 아닌 주문 시 ValueError
#   재고 반영 공식: PRD §5.5.2 "생산 완료 시 CONFIRMED 전환"에서 파생된 설계 결정.
#   PRD에 공식 명시 없으나, 생산분에서 주문분을 충당하고 잔량을 재고에 추가하는
#   방식(new_stock = stock + actual_production - quantity)이 유일한 합리적 해석임.
```

### `view/production_view.py` — `ProductionView`

```python
# show_production_menu() -> None
#   [1] 생산 현황 조회 (PRODUCING 상태 주문 정보)
#   [2] 대기 주문 목록 (생산 큐)
#   [3] 생산 완료 처리
#   [0] 메인 메뉴로 돌아가기
#
# show_production_queue(orders: list[Order]) -> None
#   - 컬럼: 순번 | 주문번호 | 시료ID | 고객명 | 수량
#   - 빈 큐: "생산 대기 중인 주문이 없습니다." 출력
#
# show_production_info(info: dict) -> None
#   - 주문 정보, 부족분, 실 생산량, 총 생산 시간 출력
#
# show_message(msg: str) -> None
#
# input_order_id(prompt: str) -> str
#
# get_user_choice() -> str
```

---

## 단위 테스트

**`tests/test_production_controller.py`** (7개, `tmp_path` fixture 사용)
- `test_get_production_queue_fifo` — PRODUCING 주문이 order_id 오름차순으로 반환
- `test_get_production_info_calculation` — 실 생산량·총 시간 계산 정확성 확인
  - 예: quantity=100, stock=30, yield_rate=0.9 → 부족분=70, 실생산량=ceil(70/(0.9×0.9))=87
- `test_get_production_info_zero_stock` — stock=0인 경우 부족분=quantity
- `test_get_production_info_not_found` — 미존재 order_id 입력 시 ValueError
- `test_complete_production_status_change` — PRODUCING → CONFIRMED 전환 확인
- `test_complete_production_stock_update` — 생산 후 재고 반영 확인
- `test_complete_production_wrong_status_raises` — PRODUCING 아닌 주문 완료 → ValueError

---

## 체크리스트

- [x] `controller/production_controller.py` 구현 (3개 메서드)
- [x] `view/production_view.py` 구현 (6개 메서드)
- [x] 생산량 계산 공식(`ceil(부족분 / (수율 × 0.9))`) 정확히 구현
- [x] FIFO 정렬 구현 (order_id 오름차순)
- [x] 생산 완료 시 재고 반영 구현
- [x] 단위 테스트 7개 작성 및 전체 PASS
- [x] Controller 내 View import 없음 확인
