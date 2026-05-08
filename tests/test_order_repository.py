import pytest
from model.order import Order
from repository.order_repository import OrderRepository


def _make_order(
    order_id="ORD-20260508-0001",
    sample_id="S-001",
    customer_name="삼성전자",
    quantity=100,
    status="RESERVED",
):
    """테스트용 Order 객체 생성 헬퍼."""
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status=status,
    )


def test_create_and_read(tmp_path):
    """create() 후 read()로 동일 객체를 반환하는지 확인."""
    repo = OrderRepository(str(tmp_path / "orders.json"))
    order = _make_order()
    repo.create(order)

    result = repo.read("ORD-20260508-0001")
    assert result is not None
    assert result.order_id == "ORD-20260508-0001"
    assert result.sample_id == "S-001"
    assert result.customer_name == "삼성전자"
    assert result.quantity == 100
    assert result.status == "RESERVED"


def test_update_status(tmp_path):
    """update()로 주문 상태를 변경한 후 변경 값이 반영되는지 확인."""
    repo = OrderRepository(str(tmp_path / "orders.json"))
    order = _make_order(status="RESERVED")
    repo.create(order)

    # 상태를 CONFIRMED로 변경
    updated_order = _make_order(status="CONFIRMED")
    repo.update(updated_order)

    result = repo.read("ORD-20260508-0001")
    assert result.status == "CONFIRMED"


def test_delete_raises_not_implemented(tmp_path):
    """delete() 호출 시 NotImplementedError 발생 확인 (PRD에 주문 삭제 없음)."""
    repo = OrderRepository(str(tmp_path / "orders.json"))
    with pytest.raises(NotImplementedError):
        repo.delete("ORD-20260508-0001")


def test_list_by_status(tmp_path):
    """list_by_status()가 특정 상태의 주문만 필터링하여 반환하는지 확인."""
    repo = OrderRepository(str(tmp_path / "orders.json"))
    o1 = _make_order(order_id="ORD-20260508-0001", status="RESERVED")
    o2 = _make_order(order_id="ORD-20260508-0002", status="CONFIRMED")
    o3 = _make_order(order_id="ORD-20260508-0003", status="RESERVED")
    repo.create(o1)
    repo.create(o2)
    repo.create(o3)

    reserved = repo.list_by_status("RESERVED")
    assert len(reserved) == 2
    assert all(o.status == "RESERVED" for o in reserved)
    assert reserved[0].order_id == "ORD-20260508-0001"
    assert reserved[1].order_id == "ORD-20260508-0003"

    confirmed = repo.list_by_status("CONFIRMED")
    assert len(confirmed) == 1
    assert confirmed[0].order_id == "ORD-20260508-0002"


def test_persistence(tmp_path):
    """재인스턴스 후에도 JSON 파일을 통해 데이터가 유지되는지 확인."""
    json_path = str(tmp_path / "orders.json")

    # 첫 번째 인스턴스에서 데이터 저장
    repo1 = OrderRepository(json_path)
    order = _make_order(status="PRODUCING")
    repo1.create(order)

    # 두 번째 인스턴스에서 데이터 조회
    repo2 = OrderRepository(json_path)
    result = repo2.read("ORD-20260508-0001")
    assert result is not None
    assert result.order_id == "ORD-20260508-0001"
    assert result.status == "PRODUCING"
