# phase-5-3-sample-management.md - 시료 관리 기능

## 목표
PRD §5.1의 시료 관리 3기능(등록 / 목록 조회 / 이름 검색)을 JSON 영속성과 함께 구현한다.
Phase 1의 인메모리 SampleController를 Repository 기반으로 교체한다.

---

## 구현 항목

### `controller/sample_controller.py` — `SampleController`

```python
# 의존: SampleRepository
#
# __init__(self, repo: SampleRepository)
#
# add_sample(id, name, avg_production_time, yield_rate, stock) -> Sample
#   - 중복 ID 시 ValueError (Repository에서 전파)
#   - Sample 생성 후 repo.create() 호출
#   - 추가된 Sample 반환
#
# get_all_samples() -> list[Sample]
#   - repo.list_all() 반환
#
# search_sample_by_name(keyword: str) -> list[Sample]
#   - 대소문자 무시, name에 keyword 포함 시 반환
#   - 결과 없으면 빈 리스트
#   - PRD §5.1.3 "이름 등 속성" 중 이름(name) 검색만 구현 (ID·수율 등 타 속성 검색 제외)
#
# get_sample(id: str) -> Sample | None
#   - repo.read(id) 반환 (다른 Controller에서 재고 확인 시 사용)
#
# update_stock(id: str, new_stock: int)
#   - repo.read() → stock 변경 → repo.update()
#   - 시료 미존재 시 KeyError
#   - new_stock < 0 시 ValueError
```

### `view/sample_view.py` — `SampleView`

```python
# show_sample_menu() -> None
#   [1] 시료 등록
#   [2] 시료 목록 조회
#   [3] 시료 검색
#   [0] 메인 메뉴로 돌아가기
#
# show_sample_list(samples: list[Sample]) -> None
#   - 컬럼: ID | 이름 | 평균생산시간(min/ea) | 수율 | 재고
#   - 빈 목록: "등록된 시료가 없습니다." 출력
#
# show_message(msg: str) -> None
#
# input_sample_data() -> dict
#   - 반환: {"id", "name", "avg_production_time", "yield_rate", "stock"}
#
# get_user_choice() -> str
#   - "선택 > " 프롬프트
#
# input_search_keyword() -> str
```

---

## 단위 테스트

**`tests/test_sample_controller.py`** (8개, `tmp_path` fixture 사용)
- `test_add_sample_success`
- `test_add_sample_duplicate_raises`
- `test_get_all_samples_empty`
- `test_get_all_samples_multiple`
- `test_search_by_name_found`
- `test_search_by_name_not_found`
- `test_search_case_insensitive`
- `test_update_stock`
  (get_sample()은 test_approve_order 계열 테스트에서 간접 커버됨 — 별도 테스트 불필요)

---

## 체크리스트

- [x] `controller/sample_controller.py` 구현 (Repository 기반, 5개 메서드)
- [x] `view/sample_view.py` 구현 (6개 메서드)
- [x] 단위 테스트 8개 작성 및 전체 PASS
- [x] Controller 내 View import 없음 확인
- [x] View 내 Controller import 없음 확인
