import flet as ft
import sqlite3
import threading
import time
import random
import uuid

import database
import engine

database.init_db()
engine.start_engine()


# ==========================================
# COLORS
# ==========================================

PRIMARY = "#111827"
BACKGROUND = "#F8FAFC"

SUCCESS = "#10B981"
WARNING = "#F59E0B"
INFO = "#3B82F6"
GRAY = "#6B7280"

CARD_BG = "#FFFFFF"


# ==========================================
# METRIC CARD
# ==========================================

def metric_card(
    title,
    value,
    color
):

    return ft.Container(

        width=220,
        height=110,

        bgcolor=color,

        border_radius=15,

        padding=20,

        content=ft.Column([

            ft.Text(
                title,
                color="white",
                size=14
            ),

            ft.Text(
                str(value),
                color="white",
                size=30,
                weight=ft.FontWeight.BOLD
            )

        ])
    )


# ==========================================
# MAIN
# ==========================================

def main(page: ft.Page):

    page.title = (
        "LogisticsPro Fulfillment Center"
    )

    page.theme_mode = (
        ft.ThemeMode.LIGHT
    )

    page.bgcolor = BACKGROUND

    page.padding = 0

    page.scroll = (
        ft.ScrollMode.AUTO
    )

    page.window_width = 1600
    page.window_height = 900

    # ======================================
    # CONTAINERS
    # ======================================

    metric_row = ft.Row()

    tracking_board = ft.Column()

    worker_panel = ft.Column()

    timeline_panel = ft.Column()

    # ======================================
    # TEST DATA
    # ======================================

    RANDOM_CUSTOMERS = [

        "John Doe",
        "Jane Smith",
        "Bob Johnson",
        "Alice Brown",

        "Michael Garcia",
        "Sarah Wilson",

        "David Lee",
        "Emma Davis"
    ]

    RANDOM_PRODUCTS = [

        "Gaming Mouse",

        "Mechanical Keyboard",

        "Monitor",

        "Headset",

        "Webcam",

        "Microphone",

        "SSD Drive"
    ]

    # ======================================
    # GENERATE ORDERS
    # ======================================

    def generate_orders(count):

        for _ in range(count):

            database.add_order(

                f"LP-{str(uuid.uuid4())[:8]}",

                random.choice(
                    RANDOM_CUSTOMERS
                ),

                random.choice(
                    RANDOM_PRODUCTS
                ),

                random.randint(1, 5)
            )

    # ======================================
    # CLEAR DATABASE
    # ======================================

    def clear_database(e):

        with sqlite3.connect(
            database.DB_FILE
        ) as conn:

            c = conn.cursor()

            c.execute(
                "DELETE FROM timeline"
            )

            c.execute(
                "DELETE FROM orders"
            )

            conn.commit()

    # ======================================
    # STRESS TEST PANEL
    # ======================================

    stress_panel = ft.Card(

        content=ft.Container(

            padding=15,

            content=ft.Column([

                ft.Text(
                    "System Simulation",
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),

                ft.ElevatedButton(
                    "Generate 10 Orders",
                    on_click=lambda e:
                    generate_orders(10)
                ),

                ft.ElevatedButton(
                    "Generate 50 Orders",
                    on_click=lambda e:
                    generate_orders(50)
                ),

                ft.ElevatedButton(
                    "Generate 100 Orders",
                    on_click=lambda e:
                    generate_orders(100)
                ),

                ft.ElevatedButton(
                    "Clear Database",
                    on_click=clear_database
                )

            ])
        )
    )

    # ======================================
    # SIDEBAR
    # ======================================

    sidebar = ft.Container(

        width=240,

        bgcolor="#FFFFFF",

        padding=20,

        content=ft.Column([

            ft.Text(
                "🚚 LogisticsPro",
                size=28,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Distributed Fulfillment"
            ),

            ft.Divider(),

            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.DASHBOARD
                ),
                title=ft.Text(
                    "Dashboard"
                )
            ),

            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.INVENTORY
                ),
                title=ft.Text(
                    "Orders"
                )
            ),

            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.GROUP
                ),
                title=ft.Text(
                    "Workers"
                )
            ),

            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.HISTORY
                ),
                title=ft.Text(
                    "History"
                )
            )

        ])
    )

    # ======================================
    # TIMELINE VIEWER
    # ======================================

    def show_timeline(order_id):

        timeline_panel.controls.clear()

        timeline_panel.controls.append(

            ft.Text(
                f"Fulfillment Deep Dive",
                size=22,
                weight=ft.FontWeight.BOLD
            )
        )

        timeline_panel.controls.append(
            ft.Text(
                f"Order: {order_id}",
                color=GRAY
            )
        )

        try:

            timeline = (
                database.get_timeline(
                    order_id
                )
            )

            for event in timeline:

                timeline_panel.controls.append(

                    ft.ListTile(

                        leading=ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE
                        ),

                        title=ft.Text(
                            event["stage"]
                        ),

                        subtitle=ft.Text(
                            event["timestamp"]
                        )
                    )
                )

        except Exception as ex:

            timeline_panel.controls.append(
                ft.Text(str(ex))
            )

    # ======================================
    # WORKER STATUS PANEL
    # ======================================

    def build_worker_cards():

        worker_panel.controls.clear()

        worker_panel.controls.append(

            ft.Text(
                "Worker Status",
                size=22,
                weight=ft.FontWeight.BOLD
            )
        )

        for worker, status in (
            engine.WORKER_STATUS.items()
        ):

            active = (
                status != "Idle"
            )

            worker_panel.controls.append(

                ft.Card(

                    content=ft.Container(

                        padding=15,

                        content=ft.Column([

                            ft.Text(
                                worker,
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                status,
                                color=
                                SUCCESS
                                if active
                                else GRAY
                            )

                        ])
                    )
                )
            )

    # ======================================
    # REFRESH DASHBOARD
    # ======================================

    def refresh_dashboard():

        orders = (
            database.get_all_orders()
        )

        total = len(orders)

        completed = len([

            o for o in orders

            if o["status"]
            ==
            "✅ Completed"

        ])

        processing = len([

            o for o in orders

            if o["status"]

            not in (

                "⏳ Pending in Queue",

                "🔄 Queueing...",

                "✅ Completed"
            )
        ])

        queue_size = (
            engine.order_queue.qsize()
        )

        # ==================================
        # METRICS
        # ==================================

        metric_row.controls = [

            metric_card(
                "Waiting in Line",
                queue_size,
                WARNING
            ),

            metric_card(
                "Handling Now",
                processing,
                INFO
            ),

            metric_card(
                "Completed",
                completed,
                SUCCESS
            ),

            metric_card(
                "Total Orders",
                total,
                GRAY
            )
        ]

        # ==================================
        # WORKERS
        # ==================================

        build_worker_cards()

        # ==================================
        # TRACKING TABLE
        # ==================================

        rows = []

        for order in orders:

            rows.append(

                ft.DataRow(

                    cells=[

                        ft.DataCell(

                            ft.Text(
                                order["id"]
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                order["customer"]
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                order["product"]
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                str(
                                    order["qty"]
                                )
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                order["status"]
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                order["worker"]
                            )
                        ),

                        ft.DataCell(

                            ft.Text(
                                order[
                                    "tracking_number"
                                ]
                            )
                        )
                    ]
                )
            )

        tracking_board.controls = [

            ft.Text(
                "Global Tracking Board",
                size=24,
                weight=ft.FontWeight.BOLD
            ),

            ft.Card(

                content=ft.Container(

                    padding=10,

                    content=ft.DataTable(

                        columns=[

                            ft.DataColumn(
                                ft.Text(
                                    "Order ID"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Customer"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Product"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Qty"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Status"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Worker"
                                )
                            ),

                            ft.DataColumn(
                                ft.Text(
                                    "Tracking"
                                )
                            )
                        ],

                        rows=rows
                    )
                )
            )
        ]

    # ======================================
    # SEARCH BAR
    # ======================================

    order_search = ft.TextField(
        label="Search Order Timeline",
        width=300
    )

    search_button = ft.ElevatedButton(
        "View Timeline",
        icon=ft.Icons.SEARCH,
        on_click=lambda e:
        show_timeline(
            order_search.value
        )
    )

    # ======================================
    # HEADER
    # ======================================

    header = ft.Container(

        padding=20,

        content=ft.Column([

            ft.Text(
                "🚚 LogisticsPro Fulfillment Center",
                size=32,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Distributed Real-Time E-Commerce Order Fulfillment System",
                color=GRAY
            )
        ])
    )

    # ======================================
    # RIGHT PANEL
    # ======================================

    right_panel = ft.Column([

        worker_panel,

        ft.Divider(),

        stress_panel,

        ft.Divider(),

        timeline_panel

    ])

    # ======================================
    # MAIN CONTENT
    # ======================================

    main_content = ft.Container(

        expand=True,

        padding=20,

        content=ft.Column([

            header,

            metric_row,

            ft.Divider(),

            ft.Row([

                order_search,

                search_button

            ]),

            ft.Divider(),

            ft.Row([

                ft.Container(
                    content=tracking_board,
                    expand=2
                ),

                ft.Container(
                    content=right_panel,
                    expand=1
                )

            ],
            expand=True)

        ])
    )

    # ======================================
    # PAGE LAYOUT
    # ======================================

    page.add(

        ft.Row([

            sidebar,

            main_content

        ],
        expand=True)
    )

    # ======================================
    # AUTO REFRESH
    # ======================================

    def refresh_loop():

        while True:

            try:

                refresh_dashboard()

                page.update()

            except Exception as ex:

                print(
                    "Dashboard Error:",
                    ex
                )

            time.sleep(2)

    # ======================================
    # INITIAL LOAD
    # ======================================

    refresh_dashboard()

    threading.Thread(
        target=refresh_loop,
        daemon=True
    ).start()

ft.app(
    target=main,
    port=8550,
    view=ft.AppView.WEB_BROWSER
)