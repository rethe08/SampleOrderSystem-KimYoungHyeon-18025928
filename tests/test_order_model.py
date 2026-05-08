import pytest
from model.order import Order


def test_create_success():
    """정상적인 속성값으로 Order 객체 생성 확인."""
    order = Order(
        order_id="ORD-20260508-0001",
        sample_id="S-001",
        customer_name="삼성전자",
        quantity=100,
        status="RESERVED",
    )
    assert order.order_id == "ORD-20260508-0001"
    assert order.sample_id == "S-001"
    assert order.customer_name == "삼성전자"
    assert order.quantity == 100
    assert order.status == "RESERVED"


def test_quantity_zero_raises():
    """quantity=0 → ValueError 발생 확인."""
    with pytest.raises(ValueError):
        Order(
            order_id="ORD-20260508-0001",
            sample_id="S-001",
            customer_name="삼성전자",
            quantity=0,
            status="RESERVED",
        )


def test_to_dict_from_dict_roundtrip():
    """to_dict() 후 from_dict()로 복원한 객체가 원본과 동등한지 확인."""
    original = Order(
        order_id="ORD-20260508-0002",
        sample_id="S-002",
        customer_name="SK하이닉스",
        quantity=200,
        status="CONFIRMED",
    )
    d = original.to_dict()
    restored = Order.from_dict(d)

    assert restored.order_id == original.order_id
    assert restored.sample_id == original.sample_id
    assert restored.customer_name == original.customer_name
    assert restored.quantity == original.quantity
    assert restored.status == original.status
