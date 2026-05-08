import datetime
import re

import pytest

from model.sample import Sample
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.order_controller import OrderController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repos(tmp_path):
    """테스트용 Repository 쌍 생성 헬퍼."""
    sample_repo = SampleRepository(str(tmp_path / "samples.json"))
    order_repo = OrderRepository(str(tmp_path / "orders.json"))
    return sample_repo, order_repo


def _make_ctrl(tmp_path):
    """테스트용 OrderController 생성 헬퍼."""
    sample_repo, order_repo = _make_repos(tmp_path)
    return OrderController(order_repo=order_repo, sample_repo=sample_repo)


def _add_sample(sample_repo: SampleRepository, id_: str = "S-001", stock: int = 100):
    """테스트용 Sample 등록 헬퍼."""
    sample = Sample(
        id=id_,
        name="테스트 시료",
        avg_production_time=1.0,
        yield_rate=0.9,
        stock=stock,
    )
    sample_repo.create(sample)
    return sample


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_order_success(tmp_path):
    """create_order()가 올바른 속성을 가진 RESERVED 상태 Order를 반환하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=50)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(
        sample_id="S-001",
        customer_name="홍길동",
        quantity=10,
    )

    assert order.sample_id == "S-001"
    assert order.customer_name == "홍길동"
    assert order.quantity == 10
    assert order.status == "RESERVED"
    # order_repo에 실제 저장됐는지 확인
    stored = order_repo.read(order.order_id)
    assert stored is not None
    assert stored.status == "RESERVED"


def test_create_order_invalid_sample_raises(tmp_path):
    """등록되지 않은 sample_id로 create_order() 시 ValueError가 발생하는지 확인."""
    ctrl = _make_ctrl(tmp_path)

    with pytest.raises(ValueError, match="등록되지 않은 시료입니다."):
        ctrl.create_order(
            sample_id="NOT-EXIST",
            customer_name="홍길동",
            quantity=5,
        )


def test_create_order_id_format(tmp_path):
    """create_order()가 생성하는 order_id가 ORD-YYYYMMDD-XXXX 형식이며 오늘 날짜를 포함하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=100)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="테스트", quantity=1)

    today_str = datetime.date.today().strftime("%Y%m%d")
    pattern = re.compile(r"^ORD-\d{8}-\d{4}$")
    assert pattern.match(order.order_id), f"order_id 형식 불일치: {order.order_id}"
    assert today_str in order.order_id, f"오늘 날짜({today_str})가 order_id에 없음: {order.order_id}"

    # 두 번째 주문 생성 시 시퀀스가 +1 증가하는지 확인
    order2 = ctrl.create_order(sample_id="S-001", customer_name="테스트2", quantity=2)
    seq1 = int(order.order_id.split("-")[-1])
    seq2 = int(order2.order_id.split("-")[-1])
    assert seq2 == seq1 + 1


def test_approve_order_sufficient_stock(tmp_path):
    """재고 충분 시 approve_order()가 CONFIRMED를 반환하고 재고를 차감하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=50)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="홍길동", quantity=10)
    result_status = ctrl.approve_order(order.order_id)

    assert result_status == "CONFIRMED"

    # 주문 상태 확인
    updated_order = order_repo.read(order.order_id)
    assert updated_order.status == "CONFIRMED"

    # 재고 차감 확인 (50 - 10 = 40)
    updated_sample = sample_repo.read("S-001")
    assert updated_sample.stock == 40


def test_approve_order_insufficient_stock(tmp_path):
    """재고 부족 시 approve_order()가 PRODUCING을 반환하고 재고를 차감하지 않는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=5)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="홍길동", quantity=10)
    result_status = ctrl.approve_order(order.order_id)

    assert result_status == "PRODUCING"

    # 주문 상태 확인
    updated_order = order_repo.read(order.order_id)
    assert updated_order.status == "PRODUCING"

    # 재고 차감 없음 확인 (여전히 5)
    updated_sample = sample_repo.read("S-001")
    assert updated_sample.stock == 5


def test_approve_order_wrong_status_raises(tmp_path):
    """RESERVED 상태가 아닌 주문에 approve_order() 시 ValueError가 발생하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=100)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="홍길동", quantity=10)
    # CONFIRMED로 전환
    ctrl.approve_order(order.order_id)
    # 이미 CONFIRMED인 주문에 다시 승인 시도
    with pytest.raises(ValueError):
        ctrl.approve_order(order.order_id)


def test_reject_order_success(tmp_path):
    """reject_order()가 RESERVED → REJECTED로 올바르게 전환하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=100)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="홍길동", quantity=10)
    ctrl.reject_order(order.order_id)

    updated_order = order_repo.read(order.order_id)
    assert updated_order.status == "REJECTED"


def test_reject_order_wrong_status_raises(tmp_path):
    """RESERVED 상태가 아닌 주문에 reject_order() 시 ValueError가 발생하는지 확인."""
    sample_repo, order_repo = _make_repos(tmp_path)
    _add_sample(sample_repo, id_="S-001", stock=100)
    ctrl = OrderController(order_repo=order_repo, sample_repo=sample_repo)

    order = ctrl.create_order(sample_id="S-001", customer_name="홍길동", quantity=10)
    # 먼저 승인해서 CONFIRMED 상태로 변경
    ctrl.approve_order(order.order_id)
    # CONFIRMED 상태에서 거절 시도
    with pytest.raises(ValueError):
        ctrl.reject_order(order.order_id)
