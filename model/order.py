VALID_STATUSES = {"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"}


class Order:
    """주문 도메인 모델.

    속성:
        order_id (str): 주문 고유 번호 (예: ORD-20260508-0001)
                        생성 책임은 OrderController에 있음.
                        Model은 전달받은 값을 저장·검증만 한다.
        sample_id (str): 주문 대상 시료 ID
        customer_name (str): 고객명
        quantity (int): 주문 수량 (quantity > 0)
        status (str): 주문 상태 (RESERVED / REJECTED / PRODUCING / CONFIRMED / RELEASE)
    """

    def __init__(
        self,
        order_id: str,
        sample_id: str,
        customer_name: str,
        quantity: int,
        status: str,
    ) -> None:
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        if status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(VALID_STATUSES)}, got '{status}'"
            )

        self.order_id = order_id
        self.sample_id = sample_id
        self.customer_name = customer_name
        self.quantity = quantity
        self.status = status

    def to_dict(self) -> dict:
        """Order 객체를 JSON 직렬화 가능한 dict로 변환."""
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "customer_name": self.customer_name,
            "quantity": self.quantity,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Order":
        """dict에서 Order 객체를 생성 (JSON 역직렬화)."""
        return cls(
            order_id=d["order_id"],
            sample_id=d["sample_id"],
            customer_name=d["customer_name"],
            quantity=d["quantity"],
            status=d["status"],
        )
