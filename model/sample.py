class Sample:
    """시료 도메인 모델.

    속성:
        id (str): 시료 고유 ID (예: S-001)
        name (str): 시료 이름
        avg_production_time (float): 평균 생산시간 (min/ea), 양수여야 함 (> 0)
        yield_rate (float): 수율 (0.0 이상 ~ 1.0 이하)
        stock (int): 현재 재고 수량 (0 이상)
    """

    def __init__(
        self,
        id: str,
        name: str,
        avg_production_time: float,
        yield_rate: float,
        stock: int,
    ) -> None:
        if not (0.0 <= yield_rate <= 1.0):
            raise ValueError(
                f"yield_rate must be between 0.0 and 1.0, got {yield_rate}"
            )
        if avg_production_time <= 0:
            raise ValueError(
                f"avg_production_time must be positive, got {avg_production_time}"
            )
        if stock < 0:
            raise ValueError(f"stock must be non-negative, got {stock}")

        self.id = id
        self.name = name
        self.avg_production_time = avg_production_time
        self.yield_rate = yield_rate
        self.stock = stock

    def to_dict(self) -> dict:
        """Sample 객체를 JSON 직렬화 가능한 dict로 변환."""
        return {
            "id": self.id,
            "name": self.name,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Sample":
        """dict에서 Sample 객체를 생성 (JSON 역직렬화)."""
        return cls(
            id=d["id"],
            name=d["name"],
            avg_production_time=d["avg_production_time"],
            yield_rate=d["yield_rate"],
            stock=d["stock"],
        )
