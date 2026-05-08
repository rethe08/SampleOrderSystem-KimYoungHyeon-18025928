import pytest
from model.sample import Sample


def test_create_success():
    """정상적인 속성값으로 Sample 객체 생성 확인."""
    sample = Sample(
        id="S-001",
        name="실리콘 웨이퍼-8인치",
        avg_production_time=0.5,
        yield_rate=0.92,
        stock=100,
    )
    assert sample.id == "S-001"
    assert sample.name == "실리콘 웨이퍼-8인치"
    assert sample.avg_production_time == 0.5
    assert sample.yield_rate == 0.92
    assert sample.stock == 100


def test_yield_rate_boundary():
    """yield_rate 경계값 검증: 0.0, 1.0은 허용 / 1.1, -0.1은 ValueError."""
    # 허용 경계값
    s_zero = Sample("S-A", "테스트A", 1.0, 0.0, 0)
    assert s_zero.yield_rate == 0.0

    s_one = Sample("S-B", "테스트B", 1.0, 1.0, 0)
    assert s_one.yield_rate == 1.0

    # 상한 초과 → ValueError
    with pytest.raises(ValueError):
        Sample("S-C", "테스트C", 1.0, 1.1, 0)

    # 하한 미만 → ValueError
    with pytest.raises(ValueError):
        Sample("S-D", "테스트D", 1.0, -0.1, 0)


def test_avg_time_zero_raises():
    """avg_production_time=0 → ValueError 발생 확인."""
    with pytest.raises(ValueError):
        Sample("S-001", "테스트", 0, 0.5, 0)


def test_stock_negative_raises():
    """stock=-1 → ValueError 발생 확인."""
    with pytest.raises(ValueError):
        Sample("S-001", "테스트", 1.0, 0.5, -1)


def test_to_dict_from_dict_roundtrip():
    """to_dict() 후 from_dict()로 복원한 객체가 원본과 동등한지 확인."""
    original = Sample(
        id="S-002",
        name="GaAs 웨이퍼",
        avg_production_time=1.5,
        yield_rate=0.85,
        stock=50,
    )
    d = original.to_dict()
    restored = Sample.from_dict(d)

    assert restored.id == original.id
    assert restored.name == original.name
    assert restored.avg_production_time == original.avg_production_time
    assert restored.yield_rate == original.yield_rate
    assert restored.stock == original.stock
