from model.sample import Sample
from repository.base_repository import JsonRepository


class SampleRepository(JsonRepository):
    """Sample 엔티티의 JSON CRUD를 담당한다."""

    def create(self, sample: Sample) -> None:
        """Sample을 저장소에 추가한다.

        Args:
            sample: 추가할 Sample 객체

        Raises:
            ValueError: 동일 id가 이미 존재하는 경우
        """
        data = self._load()
        if sample.id in data:
            raise ValueError(f"Sample with id '{sample.id}' already exists.")
        data[sample.id] = sample.to_dict()
        self._save(data)

    def read(self, id: str) -> Sample | None:
        """id에 해당하는 Sample을 반환한다.

        Args:
            id: 조회할 시료 ID

        Returns:
            Sample 객체 또는 None (존재하지 않는 경우)
        """
        data = self._load()
        record = data.get(id)
        if record is None:
            return None
        return Sample.from_dict(record)

    def update(self, sample: Sample) -> None:
        """동일 id의 Sample 데이터를 갱신한다.

        Args:
            sample: 갱신할 Sample 객체

        Raises:
            KeyError: 해당 id가 존재하지 않는 경우
        """
        data = self._load()
        if sample.id not in data:
            raise KeyError(f"Sample with id '{sample.id}' not found.")
        data[sample.id] = sample.to_dict()
        self._save(data)

    def delete(self, id: str) -> None:
        """id에 해당하는 Sample을 삭제한다.

        Args:
            id: 삭제할 시료 ID

        Raises:
            KeyError: 해당 id가 존재하지 않는 경우
        """
        data = self._load()
        if id not in data:
            raise KeyError(f"Sample with id '{id}' not found.")
        del data[id]
        self._save(data)

    def list_all(self) -> list[Sample]:
        """저장된 전체 Sample 목록을 등록 순서대로 반환한다.

        Returns:
            Sample 객체 리스트 (Python 3.7+ dict 삽입 순서 보장)
        """
        data = self._load()
        return [Sample.from_dict(record) for record in data.values()]
