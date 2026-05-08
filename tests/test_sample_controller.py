import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository
from controller.sample_controller import SampleController


def _make_repo(tmp_path):
    """테스트용 SampleRepository 생성 헬퍼 (tmp_path 기반 임시 파일 사용)."""
    return SampleRepository(str(tmp_path / "samples.json"))


def _make_ctrl(tmp_path):
    """테스트용 SampleController 생성 헬퍼."""
    return SampleController(_make_repo(tmp_path))


def test_add_sample_success(tmp_path):
    """add_sample()이 올바른 속성을 가진 Sample 객체를 반환하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    sample = ctrl.add_sample(
        id="S-001",
        name="실리콘 웨이퍼",
        avg_production_time=0.5,
        yield_rate=0.9,
        stock=100,
    )

    assert sample.id == "S-001"
    assert sample.name == "실리콘 웨이퍼"
    assert sample.avg_production_time == 0.5
    assert sample.yield_rate == 0.9
    assert sample.stock == 100


def test_add_sample_duplicate_raises(tmp_path):
    """중복 ID로 add_sample() 시 ValueError가 발생하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample(
        id="S-001",
        name="실리콘 웨이퍼",
        avg_production_time=0.5,
        yield_rate=0.9,
        stock=100,
    )

    with pytest.raises(ValueError):
        ctrl.add_sample(
            id="S-001",
            name="다른 이름",
            avg_production_time=1.0,
            yield_rate=0.8,
            stock=50,
        )


def test_get_all_samples_empty(tmp_path):
    """등록된 시료가 없을 때 get_all_samples()가 빈 리스트를 반환하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    result = ctrl.get_all_samples()
    assert result == []


def test_get_all_samples_multiple(tmp_path):
    """여러 시료 등록 후 get_all_samples()가 등록 순서대로 반환하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample("S-001", "웨이퍼A", 0.5, 0.9, 100)
    ctrl.add_sample("S-002", "웨이퍼B", 1.0, 0.85, 50)
    ctrl.add_sample("S-003", "웨이퍼C", 2.0, 0.75, 30)

    result = ctrl.get_all_samples()
    assert len(result) == 3
    assert result[0].id == "S-001"
    assert result[1].id == "S-002"
    assert result[2].id == "S-003"


def test_search_by_name_found(tmp_path):
    """search_sample_by_name()이 keyword를 포함하는 name의 시료를 반환하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample("S-001", "실리콘 웨이퍼", 0.5, 0.9, 100)
    ctrl.add_sample("S-002", "갈륨 비소", 1.0, 0.85, 50)
    ctrl.add_sample("S-003", "실리콘 카바이드", 2.0, 0.75, 30)

    result = ctrl.search_sample_by_name("실리콘")
    assert len(result) == 2
    ids = [s.id for s in result]
    assert "S-001" in ids
    assert "S-003" in ids


def test_search_by_name_not_found(tmp_path):
    """keyword와 일치하는 name이 없을 때 빈 리스트를 반환하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample("S-001", "실리콘 웨이퍼", 0.5, 0.9, 100)
    ctrl.add_sample("S-002", "갈륨 비소", 1.0, 0.85, 50)

    result = ctrl.search_sample_by_name("게르마늄")
    assert result == []


def test_search_case_insensitive(tmp_path):
    """search_sample_by_name()이 대소문자를 무시하고 검색하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample("S-001", "GaN Wafer", 0.5, 0.9, 100)
    ctrl.add_sample("S-002", "SiC Substrate", 1.0, 0.85, 50)

    result_upper = ctrl.search_sample_by_name("GAN")
    result_lower = ctrl.search_sample_by_name("gan")
    result_mixed = ctrl.search_sample_by_name("Gan")

    assert len(result_upper) == 1
    assert result_upper[0].id == "S-001"
    assert len(result_lower) == 1
    assert result_lower[0].id == "S-001"
    assert len(result_mixed) == 1
    assert result_mixed[0].id == "S-001"


def test_update_stock(tmp_path):
    """update_stock()이 재고를 new_stock 값으로 올바르게 갱신하는지 확인."""
    ctrl = _make_ctrl(tmp_path)
    ctrl.add_sample("S-001", "실리콘 웨이퍼", 0.5, 0.9, 100)

    ctrl.update_stock("S-001", 200)
    sample = ctrl.get_sample("S-001")
    assert sample.stock == 200

    # 0으로 설정도 허용
    ctrl.update_stock("S-001", 0)
    sample = ctrl.get_sample("S-001")
    assert sample.stock == 0

    # 음수 시 ValueError
    with pytest.raises(ValueError):
        ctrl.update_stock("S-001", -1)

    # 존재하지 않는 시료 시 KeyError
    with pytest.raises(KeyError):
        ctrl.update_stock("NOT-EXIST", 100)
