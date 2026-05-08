import json
from abc import ABC, abstractmethod
from pathlib import Path


class JsonRepository(ABC):
    """JSON 파일 기반 CRUD 추상 클래스.

    서브클래스는 create, read, update, delete, list_all 메서드를 구현해야 한다.
    _load()와 _save()는 공통 JSON I/O 로직을 제공한다.
    """

    def __init__(self, file_path: str) -> None:
        """
        Args:
            file_path: JSON 파일 경로 (없으면 _save 시 자동 생성)
        """
        self._file_path = file_path

    def _load(self) -> dict:
        """JSON 파일을 읽어 dict로 반환. 파일이 없으면 빈 dict 반환."""
        path = Path(self._file_path)
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        """data를 JSON 파일로 저장 (덮어쓰기). 부모 디렉토리가 없으면 자동 생성."""
        path = Path(self._file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @abstractmethod
    def create(self, entity) -> None:
        """엔티티를 저장소에 추가한다."""

    @abstractmethod
    def read(self, key: str):
        """key에 해당하는 엔티티를 반환한다. 없으면 None."""

    @abstractmethod
    def update(self, entity) -> None:
        """key에 해당하는 엔티티를 덮어쓴다."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """key에 해당하는 엔티티를 삭제한다."""

    @abstractmethod
    def list_all(self) -> list:
        """저장된 전체 엔티티 목록을 등록 순서대로 반환한다."""
