from model.order import Order


class ProductionView:
    """생산라인 관련 콘솔 입출력 전담 클래스.

    비즈니스 로직을 포함하지 않으며, Controller·Repository를 import하지 않는다.
    Model 타입(Order) 참조는 허용된다.
    """

    def show_production_menu(self) -> None:
        """생산라인 서브루프용 메뉴를 출력한다."""
        print("=" * 40)
        print("   생산라인")
        print("=" * 40)
        print("[1] 생산 현황 조회")
        print("[2] 대기 주문 목록 (생산 큐)")
        print("[3] 생산 완료 처리")
        print("[0] 메인 메뉴로 돌아가기")
        print("-" * 40)

    def show_production_queue(self, orders: list[Order]) -> None:
        """PRODUCING 상태의 대기 주문 목록 테이블을 출력한다.

        Args:
            orders: Order 객체의 리스트.
                    비어있으면 "생산 대기 중인 주문이 없습니다."를 출력한다.
        """
        if not orders:
            print("생산 대기 중인 주문이 없습니다.")
            return

        header = f"{'순번':>4} {'주문번호':<24} {'시료ID':<12} {'고객명':<16} {'수량':>6}"
        print(header)
        print("-" * len(header))
        for idx, order in enumerate(orders, start=1):
            print(
                f"{idx:>4} {order.order_id:<24} {order.sample_id:<12} "
                f"{order.customer_name:<16} {order.quantity:>6}"
            )

    def show_production_info(self, info: dict) -> None:
        """생산 현황 정보를 출력한다.

        Args:
            info: {
                "order": Order,
                "sample": Sample,
                "shortage": int,
                "actual_production": int,
                "total_time": float,
            }
        """
        order = info["order"]
        sample = info["sample"]
        shortage = info["shortage"]
        actual_production = info["actual_production"]
        total_time = info["total_time"]

        print("=" * 40)
        print("   생산 현황")
        print("=" * 40)
        print(f"주문번호     : {order.order_id}")
        print(f"고객명       : {order.customer_name}")
        print(f"시료 ID      : {sample.id}")
        print(f"시료명       : {sample.name}")
        print(f"주문 수량    : {order.quantity}")
        print(f"현재 재고    : {sample.stock}")
        print(f"부족분       : {shortage}")
        print(f"실 생산량    : {actual_production}")
        print(f"총 생산 시간 : {total_time:.2f} 분")
        print("-" * 40)

    def show_message(self, msg: str) -> None:
        """단순 메시지를 1줄 출력한다.

        Args:
            msg: 출력할 메시지 문자열
        """
        print(msg)

    def input_order_id(self, prompt: str) -> str:
        """주문번호를 입력받아 반환한다.

        Args:
            prompt: 입력 안내 문자열

        Returns:
            사용자가 입력한 주문번호 문자열
        """
        return input(prompt)

    def get_user_choice(self) -> str:
        """"선택 > " 프롬프트를 출력하고 사용자 입력을 반환한다."""
        return input("선택 > ")
