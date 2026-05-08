from model.order import Order
from repository.base_repository import JsonRepository


class OrderRepository(JsonRepository):
    """Order 엔티티의 JSON CRU(Create/Read/Update)를 담당한다.

    PRD에 주문 삭제 기능이 없으므로 delete()는 NotImplementedError를 발생시킨다.
    """

    def create(self, order: Order) -> None:
        """Order를 저장소에 추가한다.

        Args:
            order: 추가할 Order 객체

        Raises:
            ValueError: 동일 order_id가 이미 존재하는 경우
        """
        data = self._load()
        if order.order_id in data:
            raise ValueError(f"Order with order_id '{order.order_id}' already exists.")
        data[order.order_id] = order.to_dict()
        self._save(data)

    def read(self, order_id: str) -> Order | None:
        """order_id에 해당하는 Order를 반환한다.

        Args:
            order_id: 조회할 주문 ID

        Returns:
            Order 객체 또는 None (존재하지 않는 경우)
        """
        data = self._load()
        record = data.get(order_id)
        if record is None:
            return None
        return Order.from_dict(record)

    def update(self, order: Order) -> None:
        """동일 order_id의 Order 데이터를 갱신한다.

        Args:
            order: 갱신할 Order 객체

        Raises:
            KeyError: 해당 order_id가 존재하지 않는 경우
        """
        data = self._load()
        if order.order_id not in data:
            raise KeyError(f"Order with order_id '{order.order_id}' not found.")
        data[order.order_id] = order.to_dict()
        self._save(data)

    def delete(self, order_id: str) -> None:
        """PRD에 주문 삭제 기능이 없으므로 NotImplementedError를 발생시킨다.

        Raises:
            NotImplementedError: 항상 발생
        """
        raise NotImplementedError("Order deletion is not supported per PRD.")

    def list_all(self) -> list[Order]:
        """저장된 전체 Order 목록을 등록 순서대로 반환한다.

        Returns:
            Order 객체 리스트 (Python 3.7+ dict 삽입 순서 보장, FIFO)
        """
        data = self._load()
        return [Order.from_dict(record) for record in data.values()]

    def list_by_status(self, status: str) -> list[Order]:
        """특정 status를 가진 Order 목록을 등록 순서대로 반환한다.

        Args:
            status: 조회할 주문 상태 (예: RESERVED, CONFIRMED 등)

        Returns:
            해당 상태의 Order 객체 리스트 (FIFO 순서)
        """
        data = self._load()
        return [
            Order.from_dict(record)
            for record in data.values()
            if record["status"] == status
        ]
