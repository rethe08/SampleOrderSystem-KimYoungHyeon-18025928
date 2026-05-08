"""진입점 및 메인 메뉴 루프.

초기화:
    - SampleRepository("data/samples.json"), OrderRepository("data/orders.json") 생성
    - SampleController, OrderController, ProductionController, MonitoringController 생성
    - SampleView, OrderView, ProductionView, MonitoringView 생성
    (config.py 불필요 — 경로 직접 주입)
"""

import os
import sys

# 패키지 루트를 sys.path에 추가하여 절대 import가 동작하도록 보장
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller.monitoring_controller import MonitoringController
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from view.monitoring_view import MonitoringView
from view.order_view import OrderView
from view.production_view import ProductionView
from view.sample_view import SampleView


def _run_sample_menu(
    sample_ctrl: SampleController,
    sample_view: SampleView,
) -> None:
    """[1] 시료 관리 서브루프."""
    while True:
        sample_view.show_sample_menu()
        choice = sample_view.get_user_choice()

        if choice == "1":
            try:
                data = sample_view.input_sample_data()
                sample = sample_ctrl.add_sample(
                    id=data["id"],
                    name=data["name"],
                    avg_production_time=data["avg_production_time"],
                    yield_rate=data["yield_rate"],
                    stock=data["stock"],
                )
                sample_view.show_message(f"시료 '{sample.id}'가 등록되었습니다.")
            except ValueError as e:
                sample_view.show_message(f"오류: {e}")

        elif choice == "2":
            samples = sample_ctrl.get_all_samples()
            sample_view.show_sample_list(samples)

        elif choice == "3":
            keyword = sample_view.input_search_keyword()
            results = sample_ctrl.search_sample_by_name(keyword)
            sample_view.show_sample_list(results)

        elif choice == "0":
            break

        else:
            sample_view.show_message("잘못된 선택입니다.")


def _run_order_menu(
    order_ctrl: OrderController,
    order_view: OrderView,
) -> None:
    """[3] 주문 승인/거절 서브루프."""
    while True:
        order_view.show_order_menu()
        choice = order_view.get_user_choice()

        if choice == "1":
            orders = order_ctrl.get_reserved_orders()
            order_view.show_order_list(orders)

        elif choice == "2":
            orders = order_ctrl.get_reserved_orders()
            order_view.show_order_list(orders)
            order_id = order_view.input_order_id("승인할 주문번호 > ")
            try:
                new_status = order_ctrl.approve_order(order_id)
                order_view.show_message(f"주문 '{order_id}' 승인 완료. 상태: {new_status}")
            except ValueError as e:
                order_view.show_message(f"오류: {e}")

        elif choice == "3":
            orders = order_ctrl.get_reserved_orders()
            order_view.show_order_list(orders)
            order_id = order_view.input_order_id("거절할 주문번호 > ")
            try:
                order_ctrl.reject_order(order_id)
                order_view.show_message(f"주문 '{order_id}' 거절 완료.")
            except ValueError as e:
                order_view.show_message(f"오류: {e}")

        elif choice == "0":
            break

        else:
            order_view.show_message("잘못된 선택입니다.")


def _run_monitoring_menu(
    monitoring_ctrl: MonitoringController,
    monitoring_view: MonitoringView,
) -> None:
    """[4] 모니터링 서브루프 (주문량/재고량 확인만. 출고 처리 없음)."""
    while True:
        monitoring_view.show_monitoring_menu()
        choice = monitoring_view.get_user_choice()

        if choice == "1":
            summary = monitoring_ctrl.get_order_status_summary()
            monitoring_view.show_order_status_summary(summary)

        elif choice == "2":
            stock_list = monitoring_ctrl.get_stock_summary()
            monitoring_view.show_stock_summary(stock_list)

        elif choice == "0":
            break

        else:
            monitoring_view.show_message("잘못된 선택입니다.")


def _run_production_menu(
    production_ctrl: ProductionController,
    production_view: ProductionView,
) -> None:
    """[5] 생산라인 서브루프."""
    while True:
        production_view.show_production_menu()
        choice = production_view.get_user_choice()

        if choice == "1":
            queue = production_ctrl.get_production_queue()
            if not queue:
                production_view.show_message("생산 대기 중인 주문이 없습니다.")
            else:
                order_id = production_view.input_order_id("조회할 주문번호 > ")
                try:
                    info = production_ctrl.get_production_info(order_id)
                    production_view.show_production_info(info)
                except ValueError as e:
                    production_view.show_message(f"오류: {e}")

        elif choice == "2":
            queue = production_ctrl.get_production_queue()
            production_view.show_production_queue(queue)

        elif choice == "3":
            queue = production_ctrl.get_production_queue()
            production_view.show_production_queue(queue)
            order_id = production_view.input_order_id("생산 완료 처리할 주문번호 > ")
            try:
                order = production_ctrl.complete_production(order_id)
                production_view.show_message(
                    f"주문 '{order.order_id}' 생산 완료. 상태: {order.status}"
                )
            except ValueError as e:
                production_view.show_message(f"오류: {e}")

        elif choice == "0":
            break

        else:
            production_view.show_message("잘못된 선택입니다.")


def _show_main_menu(
    sample_ctrl: SampleController,
    monitoring_ctrl: MonitoringController,
) -> None:
    """메인 메뉴 화면을 출력한다.

    요약 정보:
        - 등록 시료 수: SampleController.get_all_samples() → len()
        - RESERVED 주문 수: MonitoringController.get_order_status_summary()["RESERVED"]
    Controller 경유 방식 사용 — Repository 직접 접근 금지.
    """
    sample_count = len(sample_ctrl.get_all_samples())
    reserved_count = monitoring_ctrl.get_order_status_summary()["RESERVED"]

    print("=" * 60)
    print("  S-Semi 반도체 시료 생산주문관리 시스템")
    print("=" * 60)
    print(f"  [시료 현황] 등록 시료: {sample_count}종 | 접수 대기: {reserved_count}건")
    print("-" * 60)
    print("[1] 시료 관리")
    print("[2] 시료 주문")
    print("[3] 주문 승인/거절")
    print("[4] 모니터링")
    print("[5] 생산라인")
    print("[6] 출고 처리")
    print("[0] 종료")
    print("=" * 60)


def main() -> None:
    """애플리케이션 진입점."""
    # 데이터 디렉터리 경로 (main.py 위치 기준)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    samples_path = os.path.join(base_dir, "data", "samples.json")
    orders_path = os.path.join(base_dir, "data", "orders.json")

    # Repository 초기화 (경로 직접 주입)
    sample_repo = SampleRepository(samples_path)
    order_repo = OrderRepository(orders_path)

    # Controller 초기화
    sample_ctrl = SampleController(sample_repo)
    order_ctrl = OrderController(order_repo, sample_repo)
    production_ctrl = ProductionController(order_repo, sample_repo)
    monitoring_ctrl = MonitoringController(order_repo, sample_repo)

    # View 초기화
    sample_view = SampleView()
    order_view = OrderView()
    production_view = ProductionView()
    monitoring_view = MonitoringView()

    # 메인 메뉴 루프
    while True:
        _show_main_menu(sample_ctrl, monitoring_ctrl)
        choice = input("선택 > ").strip()

        if choice == "1":
            # [1] 시료 관리 서브루프
            _run_sample_menu(sample_ctrl, sample_view)

        elif choice == "2":
            # [2] 시료 주문 — 단일 동작 (서브루프 없음)
            try:
                data = order_view.input_order_data()
                order = order_ctrl.create_order(
                    sample_id=data["sample_id"],
                    customer_name=data["customer_name"],
                    quantity=data["quantity"],
                )
                order_view.show_message(
                    f"주문 접수 완료. 주문번호: {order.order_id} / 상태: {order.status}"
                )
            except (ValueError, TypeError) as e:
                order_view.show_message(f"오류: {e}")

        elif choice == "3":
            # [3] 주문 승인/거절 서브루프
            _run_order_menu(order_ctrl, order_view)

        elif choice == "4":
            # [4] 모니터링 서브루프 (주문량/재고량 확인만)
            _run_monitoring_menu(monitoring_ctrl, monitoring_view)

        elif choice == "5":
            # [5] 생산라인 서브루프
            _run_production_menu(production_ctrl, production_view)

        elif choice == "6":
            # [6] 출고 처리 — 단일 동작 (서브루프 없음)
            monitoring_view.show_release_menu()
            confirmed_orders = monitoring_ctrl.get_confirmed_orders()
            monitoring_view.show_confirmed_orders(confirmed_orders)
            order_id = monitoring_view.input_order_id("출고 처리할 주문번호 > ")
            try:
                released = monitoring_ctrl.release_order(order_id)
                monitoring_view.show_message(
                    f"주문 '{released.order_id}' 출고 처리 완료. 상태: {released.status}"
                )
            except ValueError as e:
                monitoring_view.show_message(f"오류: {e}")

        elif choice == "0":
            print("시스템을 종료합니다.")
            break

        else:
            print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
