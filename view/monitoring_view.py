from model.order import Order


class MonitoringView:
    """모니터링 및 출고 처리 관련 콘솔 입출력 전담 클래스.

    비즈니스 로직을 포함하지 않으며, Controller·Repository를 import하지 않는다.
    Model 타입(Order) 참조는 허용된다.
    """

    def show_monitoring_menu(self) -> None:
        """[4] 모니터링 서브루프용 메뉴를 출력한다."""
        print("=" * 40)
        print("   모니터링")
        print("=" * 40)
        print("[1] 주문량 확인 (상태별 주문 수)")
        print("[2] 재고량 확인 (시료별 재고 상태)")
        print("[0] 메인 메뉴로 돌아가기")
        print("-" * 40)

    def show_release_menu(self) -> None:
        """[6] 출고 처리 전용 진입 헤더를 출력한다.

        main.py에서 직접 호출되며, 서브루프가 아니다.
        CONFIRMED 주문 목록을 표시한 후 출고 대상 주문번호 입력을 안내하는 UI 헤더 역할이다.
        """
        print("=" * 40)
        print("   출고 처리")
        print("=" * 40)

    def show_order_status_summary(self, summary: dict[str, int]) -> None:
        """상태별 주문 수를 출력한다.

        Args:
            summary: {"RESERVED": n, "PRODUCING": n, "CONFIRMED": n, "RELEASE": n}
        """
        print("=" * 40)
        print("   주문 현황 (상태별 주문 수)")
        print("=" * 40)
        print(f"{'RESERVED':<12}: {summary.get('RESERVED', 0):>4} 건")
        print(f"{'PRODUCING':<12}: {summary.get('PRODUCING', 0):>4} 건")
        print(f"{'CONFIRMED':<12}: {summary.get('CONFIRMED', 0):>4} 건")
        print(f"{'RELEASE':<12}: {summary.get('RELEASE', 0):>4} 건")
        print("-" * 40)

    def show_stock_summary(self, stock_list: list[dict]) -> None:
        """시료별 재고 상태 테이블을 출력한다.

        Args:
            stock_list: [{"sample": Sample, "stock_status": str, "reserved_qty": int}, ...]
                        비어있으면 "등록된 시료가 없습니다."를 출력한다.
        """
        if not stock_list:
            print("등록된 시료가 없습니다.")
            return

        header = f"{'시료ID':<10} {'이름':<16} {'재고':>6} {'RESERVED합계':>12} {'상태':<6}"
        print(header)
        print("-" * len(header))
        for item in stock_list:
            sample = item["sample"]
            print(
                f"{sample.id:<10} {sample.name:<16} {sample.stock:>6} "
                f"{item['reserved_qty']:>12} {item['stock_status']:<6}"
            )

    def show_confirmed_orders(self, orders: list[Order]) -> None:
        """CONFIRMED 상태의 출고 대기 주문 목록 테이블을 출력한다.

        Args:
            orders: Order 객체의 리스트.
                    비어있으면 "출고 대기 중인 주문이 없습니다."를 출력한다.
        """
        if not orders:
            print("출고 대기 중인 주문이 없습니다.")
            return

        header = f"{'주문번호':<24} {'시료ID':<12} {'고객명':<16} {'수량':>6}"
        print(header)
        print("-" * len(header))
        for order in orders:
            print(
                f"{order.order_id:<24} {order.sample_id:<12} "
                f"{order.customer_name:<16} {order.quantity:>6}"
            )

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
