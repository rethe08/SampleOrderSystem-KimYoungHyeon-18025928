# phase-5-7-main.md - main.py 통합

## 목표
모든 Controller와 View를 연결하는 `main.py`를 구현하여
PRD.md 6개 메뉴가 동작하는 완성 콘솔 앱을 완성한다.

---

## 구현 항목

### `main.py`

```python
# 진입점 및 메인 메뉴 루프
#
# 초기화:
#   - SampleRepository, OrderRepository 인스턴스 생성 (data/ 경로 주입)
#   - SampleController, OrderController, ProductionController, MonitoringController 생성
#   - SampleView, OrderView, ProductionView, MonitoringView 생성
#
# 메인 메뉴 루프:
#   - 전체 시료 요약 정보 표시 (등록 시료 수 / RESERVED 주문 수)
#   - 메뉴 선택:
#     [1] 시료 관리   → SampleController + SampleView 서브루프
#     [2] 시료 주문   → OrderController + OrderView.input_order_data() 직접 호출 후 create_order()
#                       (서브루프 없음. 주문 접수 단일 동작)
#     [3] 주문 승인/거절 → OrderController + OrderView.show_order_menu() 서브루프
#                       ([1] RESERVED 목록 조회, [2] 주문 승인, [3] 주문 거절, [0] 돌아가기)
#     [4] 모니터링    → MonitoringController + MonitoringView.show_monitoring_menu() 서브루프
#                       (주문량/재고량 확인만. 출고 처리 없음)
#     [5] 생산라인    → ProductionController + ProductionView 서브루프
#     [6] 출고 처리   → MonitoringController + MonitoringView.show_release_menu() 직접 호출
#                       (서브루프 없음. CONFIRMED 목록 표시 → 주문번호 입력 → RELEASE 처리)
#     [0] 종료
#
# 메인 메뉴 요약 정보 (PRD §4):
#   - 등록된 시료 수: SampleController.get_all_samples() 결과의 len()
#   - RESERVED 상태 주문 수: MonitoringController.get_order_status_summary()["RESERVED"]
#   (Controller 경유 방식 사용 — Repository 직접 접근 금지)
```

### 메인 메뉴 화면 예시

```
============================================================
  S-Semi 반도체 시료 생산주문관리 시스템
============================================================
  [시료 현황] 등록 시료: 5종 | 접수 대기: 3건
------------------------------------------------------------
[1] 시료 관리
[2] 시료 주문
[3] 주문 승인/거절
[4] 모니터링
[5] 생산라인
[6] 출고 처리
[0] 종료
============================================================
선택 >
```

---

## MVC 역할 분리 최종 확인

| 레이어 | 허용 | 금지 |
|--------|------|------|
| Model | 데이터 구조, 유효성 검증, 직렬화 | Controller·View import |
| Repository | JSON CRUD | 비즈니스 로직 |
| Controller | 비즈니스 로직, Repository 사용 | View import |
| View | 입출력, Model 타입 참조 | Controller import, 비즈니스 로직 |
| main.py | Controller·View 연결, 서브루프 | 비즈니스 로직 직접 구현 |

---

## 통합 확인 시나리오 (수동 실행)

> main.py는 표준입력을 사용하므로 자동화 테스트 대상이 아님. 아래는 수동으로 확인한다.

1. 앱 실행 → 메인 메뉴 + 요약 정보 출력 확인
2. `[1]` 시료 관리 → 시료 등록 → 목록 조회 → 검색 → 메인 메뉴 복귀
3. `[2]` 시료 주문 → 주문 접수(RESERVED) 확인
4. `[3]` 주문 승인/거절 → RESERVED 목록 확인 → 승인(재고 충분 → CONFIRMED) 확인
5. `[3]` 주문 승인/거절 → 승인(재고 부족 → PRODUCING) 확인
6. `[5]` 생산라인 → 대기 큐 확인 → 생산 현황 → 생산 완료 처리(→ CONFIRMED)
7. `[6]` 출고 처리 → CONFIRMED 목록 확인 → 출고(→ RELEASE) 확인
8. `[4]` 모니터링 → 주문량 확인(REJECTED 제외) → 재고량 확인(여유/부족/고갈)
9. `[0]` 종료 확인
10. 재실행 후 데이터 유지(영속성) 확인

---

## 체크리스트

- [x] `main.py` 구현 (6개 메뉴 루프 + 각 서브루프 연결)
- [x] 메인 메뉴 요약 정보 표시 (등록 시료 수 / RESERVED 주문 수)
- [x] 메뉴 [1] 시료 관리 서브루프 동작 확인
- [x] 메뉴 [2] 시료 주문 (주문 접수) 동작 확인
- [x] 메뉴 [3] 주문 승인/거절 서브루프 동작 확인
- [x] 메뉴 [4] 모니터링 서브루프 동작 확인
- [x] 메뉴 [5] 생산라인 서브루프 동작 확인
- [x] 메뉴 [6] 출고 처리 동작 확인
- [x] 메뉴 [0] 종료 동작 확인
- [x] 잘못된 입력 처리 확인
- [x] 전체 단위 테스트 PASS 확인 (5-2~5-6 누적 테스트)
- [x] MVC 역할 분리 원칙 최종 확인
- [x] 앱 재실행 후 데이터 유지(영속성) 확인
