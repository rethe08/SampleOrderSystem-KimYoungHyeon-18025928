# phase-5-6-monitoring-release.md - 모니터링 및 출고 처리 기능

## 목표
PRD §5.4(모니터링)와 §5.6(출고 처리)을 구현한다.

---

## 구현 항목

### `controller/monitoring_controller.py` — `MonitoringController`

```python
# 의존: OrderRepository, SampleRepository
#
# __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository)
#
# get_order_status_summary() -> dict[str, int]
#   - PRD §5.4.1: 상태별 주문 수 집계 (REJECTED 제외)
#   - 반환: {"RESERVED": n, "PRODUCING": n, "CONFIRMED": n, "RELEASE": n}
#
# get_stock_summary() -> list[dict]
#   - PRD §5.4.2: 시료별 재고 상태 집계
#   - 반환: [{"sample": Sample, "stock_status": str, "reserved_qty": int}, ...]
#   - stock_status 판단 기준 (PRD §5.4.2 및 phase-3 기준 통일):
#     - "고갈": stock == 0
#     - "부족": 0 < stock < 해당 시료의 RESERVED 주문 quantity 합계
#     - "여유": stock >= 해당 시료의 RESERVED 주문 quantity 합계
#
# get_confirmed_orders() -> list[Order]
#   - PRD §5.6: 출고 대상 주문 목록
#   - order_repo.list_by_status("CONFIRMED") 반환
#
# release_order(order_id: str) -> Order
#   - PRD §5.6: CONFIRMED → RELEASE 전환
#   - 대상 주문이 CONFIRMED 아니면 ValueError
#   - order_repo.update() 후 Order 반환
```

### `view/monitoring_view.py` — `MonitoringView`

> **메뉴 분리 방침**: main.py의 [4] 모니터링과 [6] 출고 처리는 별개 진입점이다.
> - [4] 진입 시: show_monitoring_menu() 서브루프 → [1] 주문량, [2] 재고량만 처리
> - [6] 진입 시: 서브루프 없이 show_confirmed_orders() → input_order_id() → release 직접 실행
> show_monitoring_menu()는 [1],[2],[0]만 포함하고, 출고 처리는 별도 메서드로 분리한다.

```python
# show_monitoring_menu() -> None
#   [1] 주문량 확인 (상태별 주문 수)
#   [2] 재고량 확인 (시료별 재고 상태)
#   [0] 메인 메뉴로 돌아가기
#
# show_release_menu() -> None   ← [6] 출고 처리 전용 진입 메서드
#   CONFIRMED 주문 목록 표시 후 출고 대상 주문번호 입력 받아 처리
#   (main.py에서 직접 호출, 서브루프 아님)
#
# show_order_status_summary(summary: dict[str, int]) -> None
#   - 상태 4종(RESERVED / PRODUCING / CONFIRMED / RELEASE)과 건수 출력
#
# show_stock_summary(stock_list: list[dict]) -> None
#   - 컬럼: 시료ID | 이름 | 재고 | RESERVED 합계 | 상태(여유/부족/고갈)
#   - 빈 목록: "등록된 시료가 없습니다." 출력
#
# show_confirmed_orders(orders: list[Order]) -> None
#   - 컬럼: 주문번호 | 시료ID | 고객명 | 수량
#   - 빈 목록: "출고 대기 중인 주문이 없습니다." 출력
#
# show_message(msg: str) -> None
#
# input_order_id(prompt: str) -> str
#
# get_user_choice() -> str
```

---

## 재고 상태 판단 기준 (PRD §5.4.2)

| 상태 | 조건 |
|------|------|
| 고갈 | `stock == 0` |
| 부족 | `0 < stock < RESERVED 주문 quantity 합계` |
| 여유 | `stock >= RESERVED 주문 quantity 합계` |

> RESERVED 주문 quantity 합계가 0인 경우(주문 없음): stock > 0 이면 "여유", stock == 0 이면 "고갈"

---

## 단위 테스트 (`tests/test_monitoring_controller.py`) (7개, `tmp_path` fixture 사용)

- `test_order_status_summary_excludes_rejected` — REJECTED 제외 확인
- `test_order_status_summary_counts` — 각 상태별 정확한 카운트
- `test_stock_summary_excess` — 재고 충분 → "여유"
- `test_stock_summary_shortage` — 재고 부족 → "부족"
- `test_stock_summary_depleted` — stock=0 → "고갈"
- `test_release_order_success` — CONFIRMED → RELEASE 전환
- `test_release_order_wrong_status_raises` — CONFIRMED 아닌 주문 출고 → ValueError
  (get_confirmed_orders()는 test_release_order_success에서 간접 커버됨 — 별도 테스트 불필요)

---

## 체크리스트

- [x] `controller/monitoring_controller.py` 구현 (4개 메서드)
- [x] `view/monitoring_view.py` 구현 (show_monitoring_menu / show_release_menu 등 8개 메서드)
- [x] 재고 상태 판단 기준 3종(여유/부족/고갈) 정확히 구현
- [x] REJECTED 주문이 주문량 집계에서 제외됨을 확인
- [x] 출고 처리 시 CONFIRMED → RELEASE 전환 확인
- [x] [4] 모니터링과 [6] 출고 처리 진입점 분리 확인 (show_monitoring_menu vs show_release_menu)
- [x] 단위 테스트 7개 작성 및 전체 PASS
- [x] Controller 내 View import 없음 확인
