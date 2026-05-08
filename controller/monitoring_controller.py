from model.order import Order
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class MonitoringController:
    """모니터링 및 출고 처리 비즈니스 로직을 담당한다.

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
            sample_repo: SampleRepository 인스턴스 (재고 조회용)
        """
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def get_order_status_summary(self) -> dict[str, int]:
        """REJECTED를 제외한 4종 상태별 주문 수를 집계하여 반환한다.

        PRD §5.4.1 기준.

        Returns:
            {"RESERVED": n, "PRODUCING": n, "CONFIRMED": n, "RELEASE": n}
        """
        summary = {
            "RESERVED": 0,
            "PRODUCING": 0,
            "CONFIRMED": 0,
            "RELEASE": 0,
        }
        for order in self._order_repo.list_all():
            if order.status in summary:
                summary[order.status] += 1
        return summary

    def get_stock_summary(self) -> list[dict]:
        """시료별 재고 상태를 집계하여 반환한다.

        PRD §5.4.2 기준.

        재고 상태 판단 기준:
            - "고갈": stock == 0
            - "부족": 0 < stock < 해당 시료의 RESERVED 주문 quantity 합계
            - "여유": stock >= 해당 시료의 RESERVED 주문 quantity 합계

        RESERVED 합계가 0인 경우:
            - stock > 0 → "여유"
            - stock == 0 → "고갈"

        Returns:
            [{"sample": Sample, "stock_status": str, "reserved_qty": int}, ...]
        """
        samples = self._sample_repo.list_all()
        reserved_orders = self._order_repo.list_by_status("RESERVED")

        # 시료 ID별 RESERVED 수량 합계를 미리 집계
        reserved_qty_map: dict[str, int] = {}
        for order in reserved_orders:
            reserved_qty_map[order.sample_id] = (
                reserved_qty_map.get(order.sample_id, 0) + order.quantity
            )

        result = []
        for sample in samples:
            reserved_qty = reserved_qty_map.get(sample.id, 0)

            if sample.stock == 0:
                stock_status = "고갈"
            elif reserved_qty == 0:
                # RESERVED 주문이 없고 재고 > 0
                stock_status = "여유"
            elif sample.stock >= reserved_qty:
                stock_status = "여유"
            else:
                # 0 < stock < reserved_qty
                stock_status = "부족"

            result.append(
                {
                    "sample": sample,
                    "stock_status": stock_status,
                    "reserved_qty": reserved_qty,
                }
            )
        return result

    def get_confirmed_orders(self) -> list[Order]:
        """출고 대상(CONFIRMED) 주문 목록을 반환한다.

        PRD §5.6 기준.

        Returns:
            CONFIRMED 상태의 Order 객체 리스트 (등록 순서)
        """
        return self._order_repo.list_by_status("CONFIRMED")

    def release_order(self, order_id: str) -> Order:
        """CONFIRMED 상태의 주문을 RELEASE로 전환한다.

        PRD §5.6 기준.

        Args:
            order_id: 출고 처리할 주문 ID

        Returns:
            상태가 RELEASE로 변경된 Order 객체

        Raises:
            ValueError: order_id가 존재하지 않거나 CONFIRMED 상태가 아닌 경우
        """
        order = self._order_repo.read(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")
        if order.status != "CONFIRMED":
            raise ValueError(
                f"CONFIRMED 상태의 주문만 출고 처리할 수 있습니다. (현재 상태: {order.status})"
            )

        order.status = "RELEASE"
        self._order_repo.update(order)
        return order
