import math

import pytest

from model.sample import Sample
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.production_controller import ProductionController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repos(tmp_path):
    """테스트용 Repository 쌍 생성 헬퍼."""
    sample_repo = SampleRepository(str(tmp_path / "samples.json"))
    order_repo = OrderRepository(str(tmp_path / "orders.json"))
    return sample_repo, order_repo


def _make_ctrl(tmp_path):
    """테스트용 ProductionController 생성 헬퍼."""
    sample_repo, order_repo = _make_repos(tmp_path)
    return ProductionController(order_repo=order_repo, sample_repo=sample_repo)


def _add_sample(sample_repo: SampleRepository, id_: str = "S-001", stock: int = 30,
                yield_rate: float = 0.9, avg_production_time: float = 2.0) -> Sample:
    """테스트용 Sample 등록 헬퍼."""
    sample = Sample(
        id=id_,
        name="테스트 시료",
        avg_production_time=avg_production_time,
        yield_rate=yield_rate,
        stock=stock,
    )
    sample_repo.create(sample)
    return sample


def _add_producing_order(order_repo: OrderRepository, order_id: str,
                          sample_id: str = "S-001", quantity: int = 100,
                          customer_name: str = "홍길동") -> Order:
    """PRODUCING 상태의 주문을 직접 등록하는 헬퍼."""
    order = Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status="PRODUCING",
    )
    order_repo.create(order)
    return order


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_production_queue_fifo(tmp_path):
    """PRODUCING 주문이 order_id 오름차순(FIFO)으로 반환되는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    # 시퀀스 역순으로 삽입
    _add_producing_order(order_repo, "ORD-20260508-0003")
    _add_producing_order(order_repo, "ORD-20260508-0001")
    _add_producing_order(order_repo, "ORD-20260508-0002")

    queue = ctrl.get_production_queue()

    assert len(queue) == 3
    assert queue[0].order_id == "ORD-20260508-0001"
    assert queue[1].order_id == "ORD-20260508-0002"
    assert queue[2].order_id == "ORD-20260508-0003"


def test_get_production_info_calculation(tmp_path):
    """quantity=100, stock=30, yield_rate=0.9 → shortage=70, actual_production=87인지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, stock=30, yield_rate=0.9, avg_production_time=2.0)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    _add_producing_order(order_repo, "ORD-20260508-0001", quantity=100)

    info = ctrl.get_production_info("ORD-20260508-0001")

    assert info["shortage"] == 70            # 100 - 30
    assert info["actual_production"] == 87   # ceil(70 / (0.9 * 0.9)) = ceil(86.42) = 87
    expected_total_time = 2.0 * 87
    assert info["total_time"] == pytest.approx(expected_total_time)


def test_get_production_info_zero_stock(tmp_path):
    """stock=0인 경우 shortage가 quantity와 같은지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, stock=0, yield_rate=0.9, avg_production_time=1.0)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    _add_producing_order(order_repo, "ORD-20260508-0001", quantity=50)

    info = ctrl.get_production_info("ORD-20260508-0001")

    # stock=0이면 부족분 = quantity (특수 처리 없이 공식이 자동 성립)
    assert info["shortage"] == 50   # 50 - 0 = 50
    expected_actual = math.ceil(50 / (0.9 * 0.9))
    assert info["actual_production"] == expected_actual


def test_get_production_info_not_found(tmp_path):
    """존재하지 않는 order_id 입력 시 ValueError가 발생하는지 확인."""
    ctrl = _make_ctrl(tmp_path)

    with pytest.raises(ValueError, match="주문을 찾을 수 없습니다"):
        ctrl.get_production_info("ORD-99999999-9999")


def test_complete_production_status_change(tmp_path):
    """complete_production() 후 주문 상태가 PRODUCING → CONFIRMED로 전환되는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, stock=30, yield_rate=0.9, avg_production_time=1.0)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    _add_producing_order(order_repo, "ORD-20260508-0001", quantity=100)

    returned_order = ctrl.complete_production("ORD-20260508-0001")

    assert returned_order.status == "CONFIRMED"

    # 저장소에서 다시 읽어서도 CONFIRMED인지 확인
    stored_order = order_repo.read("ORD-20260508-0001")
    assert stored_order.status == "CONFIRMED"


def test_complete_production_stock_update(tmp_path):
    """complete_production() 후 재고가 new_stock = stock + actual_production - quantity 공식으로 반영되는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=30, yield_rate=0.9, avg_production_time=1.0)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    _add_producing_order(order_repo, "ORD-20260508-0001", quantity=100)

    # 사전 계산: shortage=70, actual_production=ceil(70/(0.9*0.9))=87
    # new_stock = 30 + 87 - 100 = 17
    ctrl.complete_production("ORD-20260508-0001")

    updated_sample = sample_repo.read("S-001")
    assert updated_sample.stock == 17  # 30 + 87 - 100 = 17


def test_complete_production_wrong_status_raises(tmp_path):
    """PRODUCING 상태가 아닌 주문에 complete_production() 시 ValueError가 발생하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo)
    ctrl = ProductionController(order_repo=order_repo, sample_repo=sample_repo)

    # CONFIRMED 상태의 주문 직접 등록
    confirmed_order = Order(
        order_id="ORD-20260508-0001",
        sample_id="S-001",
        customer_name="홍길동",
        quantity=10,
        status="CONFIRMED",
    )
    order_repo.create(confirmed_order)

    with pytest.raises(ValueError):
        ctrl.complete_production("ORD-20260508-0001")
