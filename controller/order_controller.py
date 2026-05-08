import datetime

from model.order import Order
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class OrderController:
    """주문 접수·승인·거절 비즈니스 로직을 담당한다.

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
            sample_repo: SampleRepository 인스턴스 (재고 확인·차감용)
        """
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def create_order(
        self,
        sample_id: str,
        customer_name: str,
        quantity: int,
    ) -> Order:
        """주문을 접수(RESERVED)한다.

        Args:
            sample_id: 주문 대상 시료 ID
            customer_name: 고객명
            quantity: 주문 수량 (양수여야 함)

        Returns:
            생성된 Order 객체 (status=RESERVED)

        Raises:
            ValueError: sample_id가 등록되지 않은 경우 "등록되지 않은 시료입니다."
            ValueError: quantity <= 0 인 경우 (Order 생성자가 처리)
        """
        if self._sample_repo.read(sample_id) is None:
            raise ValueError("등록되지 않은 시료입니다.")

        order_id = self._generate_order_id()
        order = Order(
            order_id=order_id,
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status="RESERVED",
        )
        self._order_repo.create(order)
        return order

    def get_reserved_orders(self) -> list[Order]:
        """RESERVED 상태의 주문 목록을 반환한다.

        Returns:
            RESERVED 상태의 Order 객체 리스트 (FIFO 순서)
        """
        return self._order_repo.list_by_status("RESERVED")

    def approve_order(self, order_id: str) -> str:
        """주문을 승인한다. 재고 상황에 따라 CONFIRMED 또는 PRODUCING으로 전환한다.

        재고 충분: stock 차감 → sample_repo.update() → order.status = CONFIRMED
        재고 부족: order.status = PRODUCING (stock 차감 없음)

        Args:
            order_id: 승인할 주문 ID

        Returns:
            최종 주문 상태 문자열 ("CONFIRMED" 또는 "PRODUCING")

        Raises:
            ValueError: order_id가 존재하지 않거나 RESERVED 상태가 아닌 경우
        """
        order = self._order_repo.read(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")
        if order.status != "RESERVED":
            raise ValueError(
                f"RESERVED 상태의 주문만 승인할 수 있습니다. (현재 상태: {order.status})"
            )

        sample = self._sample_repo.read(order.sample_id)
        if sample.stock >= order.quantity:
            sample.stock -= order.quantity
            self._sample_repo.update(sample)
            order.status = "CONFIRMED"
        else:
            order.status = "PRODUCING"

        self._order_repo.update(order)
        return order.status

    def reject_order(self, order_id: str) -> None:
        """주문을 거절한다 (RESERVED → REJECTED).

        Args:
            order_id: 거절할 주문 ID

        Raises:
            ValueError: order_id가 존재하지 않거나 RESERVED 상태가 아닌 경우
        """
        order = self._order_repo.read(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")
        if order.status != "RESERVED":
            raise ValueError(
                f"RESERVED 상태의 주문만 거절할 수 있습니다. (현재 상태: {order.status})"
            )

        order.status = "REJECTED"
        self._order_repo.update(order)

    def _generate_order_id(self) -> str:
        """오늘 날짜 기준 order_id를 자동 생성한다.

        형식: ORD-{YYYYMMDD}-{XXXX}
        당일 orders에서 최대 시퀀스를 추출한 후 +1. 없으면 0001.

        Returns:
            생성된 order_id 문자열 (예: ORD-20260508-0001)
        """
        today = datetime.date.today().strftime("%Y%m%d")
        prefix = f"ORD-{today}-"

        max_seq = 0
        for order in self._order_repo.list_all():
            if order.order_id.startswith(prefix):
                try:
                    seq = int(order.order_id[len(prefix):])
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    pass

        next_seq = max_seq + 1
        return f"{prefix}{next_seq:04d}"
