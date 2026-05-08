import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository


def _make_sample(id="S-001", name="실리콘 웨이퍼", apt=0.5, yr=0.9, stock=100):
    """테스트용 Sample 객체 생성 헬퍼."""
    return Sample(id=id, name=name, avg_production_time=apt, yield_rate=yr, stock=stock)


def test_create_and_read(tmp_path):
    """create() 후 read()로 동일 객체를 반환하는지 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    sample = _make_sample()
    repo.create(sample)

    result = repo.read("S-001")
    assert result is not None
    assert result.id == "S-001"
    assert result.name == "실리콘 웨이퍼"
    assert result.stock == 100


def test_read_not_found(tmp_path):
    """존재하지 않는 id로 read() 시 None 반환 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    result = repo.read("NOT-EXIST")
    assert result is None


def test_update(tmp_path):
    """update() 후 변경된 값이 반영되는지 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    sample = _make_sample(stock=100)
    repo.create(sample)

    updated = _make_sample(stock=200)
    repo.update(updated)

    result = repo.read("S-001")
    assert result.stock == 200


def test_update_not_found_raises(tmp_path):
    """존재하지 않는 Sample을 update() 시 KeyError 발생 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    sample = _make_sample(id="NOT-EXIST")
    with pytest.raises(KeyError):
        repo.update(sample)


def test_delete(tmp_path):
    """delete() 후 read()로 None을 반환하는지 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    sample = _make_sample()
    repo.create(sample)

    repo.delete("S-001")
    result = repo.read("S-001")
    assert result is None


def test_list_all(tmp_path):
    """list_all()이 등록 순서대로 전체 Sample 목록을 반환하는지 확인."""
    repo = SampleRepository(str(tmp_path / "samples.json"))
    s1 = _make_sample(id="S-001", name="웨이퍼1")
    s2 = _make_sample(id="S-002", name="웨이퍼2")
    s3 = _make_sample(id="S-003", name="웨이퍼3")
    repo.create(s1)
    repo.create(s2)
    repo.create(s3)

    result = repo.list_all()
    assert len(result) == 3
    assert result[0].id == "S-001"
    assert result[1].id == "S-002"
    assert result[2].id == "S-003"
