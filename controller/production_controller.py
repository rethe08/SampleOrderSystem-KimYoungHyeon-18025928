import math

from model.order import Order
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class ProductionController:
    """생산라인 관리 비즈니스 로직을 담당한다.

    View를 import하거나 의존하지 않는다.
    Repository를 통해 데이터를 영속화한다.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
    ) -> None:
        """
        Args:
            order_repo: OrderRepository 인스턴스
            sample_repo: SampleRepository 인스턴스 (재고 반영용)
        """
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def get_production_queue(self) -> list[Order]:
        """PRODUCING 상태의 주문 목록을 FIFO 순서로 반환한다.

        order_id 오름차순 정렬(ORD-날짜-시퀀스 형식이므로 문자열 정렬로 FIFO 보장).

        Returns:
            PRODUCING 상태의 Order 객체 리스트 (order_id 오름차순)
        """
        orders = self._order_repo.list_by_status("PRODUCING")
        return sorted(orders, key=lambda o: o.order_id)

    def get_production_info(self, order_id: str) -> dict:
        """PRODUCING 상태 주문의 생산 정보를 계산하여 반환한다.

        Args:
            order_id: 조회할 주문 ID

        Returns:
            {
                "order": Order,
                "sample": Sample,
                "shortage": int,           # 부족분 = quantity - stock
                "actual_production": int,  # ceil(부족분 / (수율 × 0.9))
                "total_time": float,       # 평균생산시간 × 실 생산량
            }

        Raises:
            ValueError: order_id가 존재하지 않는 경우
            ValueError: PRODUCING 상태가 아닌 주문인 경우
        """
        order = self._order_repo.read(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")
        if order.status != "PRODUCING":
            raise ValueError(
                f"PRODUCING 상태의 주문만 조회할 수 있습니다. (현재 상태: {order.status})"
            )

        sample = self._sample_repo.read(order.sample_id)

        shortage = order.quantity - sample.stock
        actual_production = math.ceil(shortage / (sample.yield_rate * 0.9))
        total_time = sample.avg_production_time * actual_production

        return {
            "order": order,
            "sample": sample,
            "shortage": shortage,
            "actual_production": actual_production,
            "total_time": total_time,
        }

    def complete_production(self, order_id: str) -> Order:
        """생산을 완료하여 주문 상태를 PRODUCING → CONFIRMED로 전환한다.

        생산된 시료를 재고에 반영한다:
            new_stock = sample.stock + actual_production - order.quantity
        (실 생산량에서 주문 수량을 충당하고 남은 수량을 재고로 추가)

        Args:
            order_id: 완료 처리할 주문 ID

        Returns:
            상태가 CONFIRMED로 변경된 Order 객체

        Raises:
            ValueError: PRODUCING 상태가 아닌 주문인 경우
        """
        info = self.get_production_info(order_id)
        order: Order = info["order"]
        sample: Sample = info["sample"]
        actual_production: int = info["actual_production"]

        new_stock = sample.stock + actual_production - order.quantity
        sample.stock = new_stock
        self._sample_repo.update(sample)

        order.status = "CONFIRMED"
        self._order_repo.update(order)

        return order
