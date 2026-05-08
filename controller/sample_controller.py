from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    """시료 관리 비즈니스 로직을 담당한다. Repository를 통해 데이터를 영속화한다.

    View를 import하거나 의존하지 않는다.
    """

    def __init__(self, repo: SampleRepository) -> None:
        """
        Args:
            repo: SampleRepository 인스턴스
        """
        self._repo = repo

    def add_sample(
        self,
        id: str,
        name: str,
        avg_production_time: float,
        yield_rate: float,
        stock: int,
    ) -> Sample:
        """새로운 Sample을 등록한다.

        Args:
            id: 시료 고유 ID
            name: 시료 이름
            avg_production_time: 평균 생산시간 (min/ea), 양수여야 함
            yield_rate: 수율 (0.0 이상 ~ 1.0 이하)
            stock: 초기 재고 수량 (0 이상)

        Returns:
            생성된 Sample 객체

        Raises:
            ValueError: 중복 ID가 이미 존재하는 경우 또는 Repository에서 전파된 경우
        """
        if self._repo.read(id) is not None:
            raise ValueError(f"Sample with id '{id}' already exists.")
        sample = Sample(
            id=id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=stock,
        )
        self._repo.create(sample)
        return sample

    def get_all_samples(self) -> list[Sample]:
        """저장된 전체 Sample 목록을 반환한다 (등록 순서 유지).

        Returns:
            Sample 객체 리스트 (없으면 빈 리스트)
        """
        return self._repo.list_all()

    def search_sample_by_name(self, keyword: str) -> list[Sample]:
        """name에 keyword가 포함된 Sample 목록을 반환한다 (대소문자 무시).

        PRD §5.1.3: 이름(name) 검색만 구현 (ID·수율 등 타 속성 검색 제외)

        Args:
            keyword: 검색 키워드

        Returns:
            매칭된 Sample 목록. 없으면 빈 리스트.
        """
        keyword_lower = keyword.lower()
        return [
            sample
            for sample in self._repo.list_all()
            if keyword_lower in sample.name.lower()
        ]

    def get_sample(self, id: str) -> Sample | None:
        """id에 해당하는 Sample을 반환한다.

        다른 Controller에서 시료 존재 여부 및 재고 확인 시 사용된다.

        Args:
            id: 시료 고유 ID

        Returns:
            Sample 객체 또는 None (존재하지 않는 경우)
        """
        return self._repo.read(id)

    def update_stock(self, id: str, new_stock: int) -> None:
        """해당 Sample의 재고를 new_stock으로 직접 설정한다.

        Args:
            id: 시료 고유 ID
            new_stock: 새로운 재고 수량

        Raises:
            ValueError: new_stock이 음수인 경우
            KeyError: 해당 id의 Sample이 존재하지 않는 경우
        """
        if new_stock < 0:
            raise ValueError(
                f"new_stock must be non-negative, got {new_stock}"
            )
        sample = self._repo.read(id)
        if sample is None:
            raise KeyError(f"Sample with id '{id}' not found.")
        sample.stock = new_stock
        self._repo.update(sample)
