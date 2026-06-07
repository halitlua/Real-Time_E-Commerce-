import flet as ft
import uuid
import threading
import time

import database

database.init_db()

# ==========================================
# COLORS
# ==========================================

PRIMARY = "#111827"

BACKGROUND = "#F8FAFC"

SUCCESS = "#10B981"

WARNING = "#F59E0B"

INFO = "#3B82F6"

GRAY = "#6B7280"


# ==========================================
# STATUS COLORS
# ==========================================

def get_status_color(status):

    if "Completed" in status:
        return SUCCESS

    if "Shipment" in status:
        return INFO

    if "Queue" in status:
        return WARNING

    if "Payment" in status:
        return "#8B5CF6"

    if "Inventory" in status:
        return "#6366F1"

    if "Packaging" in status:
        return "#EC4899"

    return GRAY



PRODUCTS = [

    "Gaming Mouse",

    "Mechanical Keyboard",

    "Monitor",

    "Headset",

    "Webcam",

    "Microphone",

    "SSD Drive"
]
# ==========================================
# MAIN
# ==========================================

def main(page: ft.Page):

    page.title = "LogisticsPro Customer Portal"

    page.theme_mode = ft.ThemeMode.LIGHT

    page.bgcolor = BACKGROUND

    page.scroll = ft.ScrollMode.AUTO

    page.window_width = 1500

    page.window_height = 900

    selected_customer = {
        "name": ""
    }

    customer_name = ft.TextField(
        label="Customer Name"
    )

    product_name = ft.Dropdown(

    label="Select Product",

    width=300,

    options=[

        ft.dropdown.Option(p)

        for p in PRODUCTS
    ]
)

    quantity = ft.Dropdown(

    label="Quantity",

    value="1",

    width=150,

    options=[

        ft.dropdown.Option("1"),
        ft.dropdown.Option("2"),
        ft.dropdown.Option("3"),
        ft.dropdown.Option("4"),
        ft.dropdown.Option("5")

    ]
)

    orders_column = ft.Column()

    timeline_column = ft.Column()

    # ======================================
    # MESSAGE
    # ======================================

    def show_message(message):

        page.snack_bar = ft.SnackBar(
            ft.Text(message)
        )

        page.snack_bar.open = True

        page.update()


    # ======================================
    # TIMELINE VIEWER
    # ======================================

    def show_timeline(order_id):

        timeline_column.controls.clear()

        timeline_column.controls.append(

            ft.Text(
                f"Order Timeline",
                size=22,
                weight=ft.FontWeight.BOLD
            )
        )

        timeline_column.controls.append(

            ft.Text(
                f"Order: {order_id}",
                color=GRAY
            )
        )

        timeline = database.get_timeline(
            order_id
        )

        for event in timeline:

            timeline_column.controls.append(

                ft.ListTile(

                    leading=ft.Icon(
                        ft.Icons.CHECK_CIRCLE
                    ),

                    title=ft.Text(
                        event["stage"]
                    ),

                    subtitle=ft.Text(
                        event["timestamp"]
                    )
                )
            )

        page.update()

    # ======================================
    # PLACE ORDER
    # ======================================
    # ======================================
    # PLACE ORDER
    # ======================================

    def place_order(e):

        if not customer_name.value:

            show_message(
                "Please enter customer name."
            )

            return

        if not product_name.value:

            show_message(
                "Please select a product."
            )

            return

        qty = int(quantity.value)

        order_id = (

            "LP-"

            +

            str(
                uuid.uuid4()
            )[:8]
        )

        database.add_order(

            order_id,

            customer_name.value,

            product_name.value,

            qty
        )

        selected_customer["name"] = (
            customer_name.value
        )

        load_orders()

        show_message(
            f"Order {order_id} created."
        )

    # ======================================
    # LOAD ORDERS
    # ======================================

    def load_orders():

        customer = (
            customer_name.value
        )

        if not customer:
            return

        selected_customer["name"] = (
            customer
        )

        orders = (

            database.get_customer_orders(
                customer
            )

        )

        rows = []

        for order in orders:

            status_color = (

                get_status_color(
                    order["status"]
                )
            )

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

                            ft.Container(

                                bgcolor=
                                status_color,

                                border_radius=20,

                                padding=8,

                                content=ft.Text(

                                    order["status"],

                                    color="white",

                                    size=12
                                )
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
                        ),

                        ft.DataCell(

                            ft.TextButton(

                                "Timeline",

                                on_click=lambda e,
                                oid=order["id"]:

                                show_timeline(
                                    oid
                                )
                            )
                        )

                    ]
                )
            )

        orders_column.controls = [

            ft.DataTable(

                columns=[

                    ft.DataColumn(
                        ft.Text(
                            "Order ID"
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
                    ),

                    ft.DataColumn(
                        ft.Text(
                            "Timeline"
                        )
                    )

                ],

                rows=rows

            )
        ]

        page.update()

    # ======================================
    # AUTO REFRESH
    # ======================================

    def refresh_loop():

        while True:

            try:

                if selected_customer["name"]:

                    load_orders()

            except Exception as ex:

                print(
                    "Refresh Error:",
                    ex
                )

            time.sleep(2)

    # ======================================
    # NAVBAR
    # ======================================

    navbar = ft.Container(

        bgcolor="white",

        padding=20,

        content=ft.Row(

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

            controls=[

                ft.Row([

                    ft.Text(
                        "🚚 LogisticsPro",
                        size=26,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(width=30),

                    ft.Text(
                        "Portal",
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text("Dashboard"),

                    ft.Text("Analytics")

                ]),

                ft.Row([

                    ft.TextField(
                        hint_text="Track shipment...",
                        width=220,
                        height=45
                    ),

                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS
                    ),

                    ft.CircleAvatar(
                        content=ft.Text("U")
                    )

                ])

            ]
        )
    )

    # ======================================
    # HERO
    # ======================================

    hero = ft.Container(

        padding=30,

        content=ft.Column([

            ft.Text(
                "Order Portal",
                size=36,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Manage your hardware requests and track real-time fulfillment status."
            )

        ])
    )

    # ======================================
    # ORDER FORM CARD
    # ======================================

    order_form_card = ft.Card(

        content=ft.Container(

            padding=20,

            content=ft.Column([

                ft.Text(
                    "Place Your Order",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),

                customer_name,

                product_name,

                quantity,

                ft.Container(height=10),

                ft.ElevatedButton(
                    "Submit Order",
                    on_click=place_order
                ),

                ft.Container(height=20),

                ft.Container(

                    bgcolor="#F3F4F6",

                    border_radius=10,

                    padding=15,

                    content=ft.Row([

                        ft.Icon(
                            ft.Icons.INFO
                        ),

                        ft.Text(
                            "Standard processing is handled automatically by the worker pool."
                        )

                    ])
                )

            ])
        )
    )

    # ======================================
    # ORDER HISTORY CARD
    # ======================================

    history_card = ft.Card(

        content=ft.Container(

            padding=20,

            content=ft.Column([

                ft.Row(

                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    controls=[

                        ft.Text(
                            "Your Order History",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.TextButton(
                            "Refresh",
                            on_click=lambda e:
                            load_orders()
                        )

                    ]
                ),

                orders_column

            ])
        )
    )

    # ======================================
    # TIMELINE CARD
    # ======================================

    timeline_card = ft.Card(

        content=ft.Container(

            padding=20,

            content=timeline_column
        )
    )

    # ======================================
    # FOOTER
    # ======================================

    footer = ft.Container(

        padding=20,

        content=ft.Row(

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

            controls=[

                ft.Text(
                    "© 2026 LogisticsPro Systems"
                ),

                ft.Row([

                    ft.Text(
                        "Terms"
                    ),

                    ft.Text(
                        "Privacy"
                    ),

                    ft.Text(
                        "Support"
                    )

                ])

            ]
        )
    )

    # ======================================
    # PAGE LAYOUT
    # ======================================

    page.add(

        navbar,

        hero,

        ft.Container(

            padding=20,

            content=ft.Row([

                ft.Container(
                    content=order_form_card,
                    expand=1
                ),

                ft.Container(
                    content=history_card,
                    expand=2
                )

            ])
        ),

        ft.Container(

            padding=20,

            content=timeline_card
        ),

        footer

    )

    # ======================================
    # START REFRESH THREAD
    # ======================================

    threading.Thread(
        target=refresh_loop,
        daemon=True
    ).start()


ft.app(
    target=main,
    port=8551,
    view=ft.AppView.WEB_BROWSER
)