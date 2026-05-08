import pytest

from model.sample import Sample
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitoring_controller import MonitoringController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repos(tmp_path):
    """테스트용 Repository 쌍 생성 헬퍼."""
    sample_repo = SampleRepository(str(tmp_path / "samples.json"))
    order_repo = OrderRepository(str(tmp_path / "orders.json"))
    return sample_repo, order_repo


def _make_ctrl(tmp_path):
    """테스트용 MonitoringController 생성 헬퍼."""
    sample_repo, order_repo = _make_repos(tmp_path)
    return MonitoringController(order_repo=order_repo, sample_repo=sample_repo)


def _add_sample(sample_repo: SampleRepository, id_: str = "S-001",
                stock: int = 50, name: str = "테스트 시료") -> Sample:
    """테스트용 Sample 등록 헬퍼."""
    sample = Sample(
        id=id_,
        name=name,
        avg_production_time=1.0,
        yield_rate=0.9,
        stock=stock,
    )
    sample_repo.create(sample)
    return sample


def _add_order(order_repo: OrderRepository, order_id: str, sample_id: str,
               quantity: int, status: str, customer_name: str = "홍길동") -> Order:
    """지정 상태의 주문을 직접 등록하는 헬퍼."""
    order = Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status=status,
    )
    order_repo.create(order)
    return order


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_order_status_summary_excludes_rejected(tmp_path):
    """REJECTED 주문은 상태별 집계에 포함되지 않는다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    _add_order(order_repo, "ORD-20260508-0001", "S-001", 10, "RESERVED")
    _add_order(order_repo, "ORD-20260508-0002", "S-001", 10, "REJECTED")
    _add_order(order_repo, "ORD-20260508-0003", "S-001", 10, "CONFIRMED")

    summary = ctrl.get_order_status_summary()

    # REJECTED는 반환 dict에 존재하지 않거나 0이어야 한다
    assert "REJECTED" not in summary
    assert summary["RESERVED"] == 1
    assert summary["CONFIRMED"] == 1


def test_order_status_summary_counts(tmp_path):
    """각 상태별 정확한 카운트가 반환되는지 확인한다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    # RESERVED 2건
    _add_order(order_repo, "ORD-20260508-0001", "S-001", 10, "RESERVED")
    _add_order(order_repo, "ORD-20260508-0002", "S-001", 10, "RESERVED")
    # PRODUCING 1건
    _add_order(order_repo, "ORD-20260508-0003", "S-001", 10, "PRODUCING")
    # CONFIRMED 3건
    _add_order(order_repo, "ORD-20260508-0004", "S-001", 10, "CONFIRMED")
    _add_order(order_repo, "ORD-20260508-0005", "S-001", 10, "CONFIRMED")
    _add_order(order_repo, "ORD-20260508-0006", "S-001", 10, "CONFIRMED")
    # RELEASE 1건
    _add_order(order_repo, "ORD-20260508-0007", "S-001", 10, "RELEASE")
    # REJECTED 2건 (집계 제외)
    _add_order(order_repo, "ORD-20260508-0008", "S-001", 10, "REJECTED")
    _add_order(order_repo, "ORD-20260508-0009", "S-001", 10, "REJECTED")

    summary = ctrl.get_order_status_summary()

    assert summary["RESERVED"] == 2
    assert summary["PRODUCING"] == 1
    assert summary["CONFIRMED"] == 3
    assert summary["RELEASE"] == 1
    assert "REJECTED" not in summary


def test_stock_summary_excess(tmp_path):
    """재고가 RESERVED 주문 합계 이상이면 "여유"로 판단한다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    # stock=100, RESERVED 주문 합계=50 → 여유
    _add_sample(sample_repo, id_="S-001", stock=100)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    _add_order(order_repo, "ORD-20260508-0001", "S-001", 30, "RESERVED")
    _add_order(order_repo, "ORD-20260508-0002", "S-001", 20, "RESERVED")

    stock_list = ctrl.get_stock_summary()

    assert len(stock_list) == 1
    assert stock_list[0]["stock_status"] == "여유"
    assert stock_list[0]["reserved_qty"] == 50


def test_stock_summary_shortage(tmp_path):
    """재고가 0보다 크고 RESERVED 주문 합계 미만이면 "부족"으로 판단한다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    # stock=30, RESERVED 주문 합계=50 → 부족
    _add_sample(sample_repo, id_="S-001", stock=30)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    _add_order(order_repo, "ORD-20260508-0001", "S-001", 30, "RESERVED")
    _add_order(order_repo, "ORD-20260508-0002", "S-001", 20, "RESERVED")

    stock_list = ctrl.get_stock_summary()

    assert len(stock_list) == 1
    assert stock_list[0]["stock_status"] == "부족"
    assert stock_list[0]["reserved_qty"] == 50


def test_stock_summary_depleted(tmp_path):
    """재고가 0이면 RESERVED 주문 여부와 무관하게 "고갈"로 판단한다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    # stock=0 → 고갈
    _add_sample(sample_repo, id_="S-001", stock=0)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    # RESERVED 주문이 있어도 stock=0이면 고갈
    _add_order(order_repo, "ORD-20260508-0001", "S-001", 10, "RESERVED")

    stock_list = ctrl.get_stock_summary()

    assert len(stock_list) == 1
    assert stock_list[0]["stock_status"] == "고갈"


def test_release_order_success(tmp_path):
    """CONFIRMED 주문을 release_order() 하면 RELEASE로 전환된다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    _add_order(order_repo, "ORD-20260508-0001", "S-001", 10, "CONFIRMED")

    # get_confirmed_orders()도 간접 검증
    confirmed = ctrl.get_confirmed_orders()
    assert len(confirmed) == 1
    assert confirmed[0].order_id == "ORD-20260508-0001"

    returned_order = ctrl.release_order("ORD-20260508-0001")

    assert returned_order.status == "RELEASE"

    # 저장소에서 다시 읽어도 RELEASE인지 확인
    stored_order = order_repo.read("ORD-20260508-0001")
    assert stored_order.status == "RELEASE"


def test_release_order_wrong_status_raises(tmp_path):
    """CONFIRMED 상태가 아닌 주문에 release_order() 시 ValueError가 발생한다."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = MonitoringController(order_repo=order_repo, sample_repo=sample_repo)

    # RESERVED 상태의 주문에 출고 처리 시도
    _add_order(order_repo, "ORD-20260508-0001", "S-001", 10, "RESERVED")

    with pytest.raises(ValueError):
        ctrl.release_order("ORD-20260508-0001")
