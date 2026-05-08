from model.sample import Sample


class SampleView:
    """시료 관련 콘솔 입출력 전담 클래스.

    비즈니스 로직을 포함하지 않으며, Controller·Repository를 import하지 않는다.
    Model 타입(Sample) 참조는 허용된다.
    """

    def show_sample_menu(self) -> None:
        """시료 관리 서브메뉴를 출력한다."""
        print("=" * 40)
        print("   시료 관리")
        print("=" * 40)
        print("[1] 시료 등록")
        print("[2] 시료 목록 조회")
        print("[3] 시료 검색")
        print("[0] 메인 메뉴로 돌아가기")
        print("-" * 40)

    def show_sample_list(self, samples: list[Sample]) -> None:
        """시료 목록 테이블을 출력한다.

        Args:
            samples: Sample 객체의 리스트.
                     비어있으면 "등록된 시료가 없습니다."를 출력한다.
        """
        if not samples:
            print("등록된 시료가 없습니다.")
            return

        header = (
            f"{'ID':<12} {'이름':<20} {'평균생산시간(min/ea)':>20} {'수율':>6} {'재고':>6}"
        )
        print(header)
        print("-" * len(header))
        for sample in samples:
            print(
                f"{sample.id:<12} {sample.name:<20} "
                f"{sample.avg_production_time:>20.2f} "
                f"{sample.yield_rate:>6.2f} "
                f"{sample.stock:>6}"
            )

    def show_message(self, msg: str) -> None:
        """단순 메시지를 1줄 출력한다.

        Args:
            msg: 출력할 메시지 문자열
        """
        print(msg)

    def input_sample_data(self) -> dict:
        """시료 등록에 필요한 입력값을 수집하여 반환한다.

        Returns:
            {
                "id": str,
                "name": str,
                "avg_production_time": float,
                "yield_rate": float,
                "stock": int,
            }
        """
        print("=== 시료 등록 ===")
        id_ = input("시료 ID > ")
        name = input("시료 이름 > ")
        avg_production_time = float(input("평균 생산시간 (min/ea) > "))
        yield_rate = float(input("수율 (0.0 ~ 1.0) > "))
        stock = int(input("초기 재고 수량 > "))
        return {
            "id": id_,
            "name": name,
            "avg_production_time": avg_production_time,
            "yield_rate": yield_rate,
            "stock": stock,
        }

    def get_user_choice(self) -> str:
        """"선택 > " 프롬프트를 출력하고 사용자 입력을 반환한다."""
        return input("선택 > ")

    def input_search_keyword(self) -> str:
        """검색 키워드를 입력받아 반환한다."""
        return input("검색 키워드 > ")
