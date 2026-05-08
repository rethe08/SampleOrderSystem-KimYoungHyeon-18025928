from model.order import Order


class OrderView:
    """주문 관련 콘솔 입출력 전담 클래스.

    비즈니스 로직을 포함하지 않으며, Controller·Repository를 import하지 않는다.
    Model 타입(Order) 참조는 허용된다.
    """

    def show_order_menu(self) -> None:
        """[3] 주문 승인/거절 진입 시 서브루프용 메뉴를 출력한다."""
        print("=" * 40)
        print("   주문 승인/거절")
        print("=" * 40)
        print("[1] 접수된 주문 목록 조회 (RESERVED)")
        print("[2] 주문 승인")
        print("[3] 주문 거절")
        print("[0] 메인 메뉴로 돌아가기")
        print("-" * 40)

    def show_order_list(self, orders: list[Order]) -> None:
        """주문 목록 테이블을 출력한다.

        Args:
            orders: Order 객체의 리스트.
                    비어있으면 "접수된 주문이 없습니다."를 출력한다.
        """
        if not orders:
            print("접수된 주문이 없습니다.")
            return

        header = (
            f"{'주문번호':<24} {'시료ID':<12} {'고객명':<16} {'수량':>6} {'상태':<12}"
        )
        print(header)
        print("-" * len(header))
        for order in orders:
            print(
                f"{order.order_id:<24} {order.sample_id:<12} "
                f"{order.customer_name:<16} {order.quantity:>6} "
                f"{order.status:<12}"
            )

    def show_message(self, msg: str) -> None:
        """단순 메시지를 1줄 출력한다.

        Args:
            msg: 출력할 메시지 문자열
        """
        print(msg)

    def input_order_data(self) -> dict:
        """주문 접수에 필요한 입력값을 수집하여 반환한다.

        [2] 시료 주문 진입 시 직접 호출용. 서브루프 없이 주문 접수 단일 동작.

        Returns:
            {
                "sample_id": str,
                "customer_name": str,
                "quantity": int,
            }
        """
        print("=== 시료 주문 ===")
        sample_id = input("시료 ID > ")
        customer_name = input("고객명 > ")
        quantity = int(input("주문 수량 > "))
        return {
            "sample_id": sample_id,
            "customer_name": customer_name,
            "quantity": quantity,
        }

    def input_order_id(self, prompt: str) -> str:
        """승인/거절 대상 주문번호를 입력받아 반환한다.

        Args:
            prompt: 입력 안내 문자열

        Returns:
            사용자가 입력한 주문번호 문자열
        """
        return input(prompt)

    def get_user_choice(self) -> str:
        """"선택 > " 프롬프트를 출력하고 사용자 입력을 반환한다."""
        return input("선택 > ")
