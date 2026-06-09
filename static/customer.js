// =====================================
// PLACE ORDER
// =====================================
let currentOrderId = null;

async function placeOrder() {

    const customer =
        document.getElementById(
            "customerName"
        ).value.trim();

    const product =
        document.getElementById(
            "product"
        ).value;

    const qty =
        document.getElementById(
            "qty"
        ).value;

    if (!customer) {

        alert(
            "Please enter customer name."
        );

        return;
    }

    try {

        const response =
            await fetch(

                "/api/place-order",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                        "application/json"

                    },

                    body: JSON.stringify({

                        customer,
                        product,
                        qty

                    })

                }

            );

        const result =
            await response.json();

        alert(
            "Order Created!\n\n" +
            result.order_id
        );

        loadOrders();

    }
    catch (error) {

        console.error(error);

        alert(
            "Failed to create order."
        );
    }
}

// =====================================
// LOAD CUSTOMER ORDERS
// =====================================

async function loadOrders() {

    const customer =
        document.getElementById(
            "customerName"
        ).value.trim();

    if (!customer) {
        // Do not expose other customers' orders. Clear table and timeline.
        document.getElementById("ordersTable").innerHTML = "";
        document.getElementById("timelineContainer").innerHTML = "";
        document.getElementById("timelineTitle").textContent = "Order Timeline";
        return;
    }

    const url = `/api/customer/orders/${encodeURIComponent(customer)}`;

    try {


        const response = await fetch(url);

        const orders =
            await response.json();

        let html = "";

        orders.forEach(order => {

            let badgeColor =
                "bg-blue-100 text-blue-700";

            if (
                String(order.status)
                .includes("Completed")
            ) {

                badgeColor =
                    "bg-green-100 text-green-700";
            }

            if (
                String(order.status)
                .includes("Pending") ||
                String(order.status)
                .includes("Queue")
            ) {

                badgeColor =
                    "bg-yellow-100 text-yellow-700";
            }

            html += `

            <tr
                onclick="loadTimeline('${order.id}')"
                class="
                hover:bg-slate-50
                cursor-pointer
                transition">

                <td class="px-6 py-4 font-mono">

                    ${order.id}

                </td>

                <td class="px-6 py-4">

                    ${order.product}

                </td>

                <td class="px-6 py-4">

                    ${order.qty}

                </td>

                <td class="px-6 py-4">

                    <span
                        class="
                        px-3
                        py-1
                        rounded-full
                        text-xs
                        font-semibold
                        ${badgeColor}">

                        ${order.status}

                    </span>

                </td>

                <td class="px-6 py-4 font-mono text-xs">

                    ${order.tracking || "-"}

                </td>

            </tr>

            `;
        });

        document.getElementById(
            "ordersTable"
        ).innerHTML = html;

    }
    catch (error) {

        console.error(error);
    }
}

// =====================================
// LOAD TIMELINE
// =====================================

async function loadTimeline(orderId) {

    currentOrderId = orderId;
    try {

        document.getElementById(
            "timelineTitle"
        ).textContent =
            `Order Timeline: ${orderId}`;

        const response =
            await fetch(

                `/api/timeline/${orderId}`

            );

        const events =
            await response.json();

        let html = "";

        events.forEach(event => {

            html += `

            <div
                class="
                relative
                z-10
                flex
                items-start">

                <div
                    class="
                    absolute
                    -left-10
                    w-10
                    h-10
                    rounded-full
                    bg-blue-600
                    text-white
                    flex
                    items-center
                    justify-center">

                    ✓

                </div>

                <div
                    class="
                    ml-6">

                    <h4
                        class="
                        font-semibold">

                        ${event.stage}

                    </h4>

                    <p
                        class="
                        text-sm
                        text-slate-500">

                        ${event.timestamp || ""}

                    </p>

                </div>

            </div>

            `;
        });

        document.getElementById(
            "timelineContainer"
        ).innerHTML = html;

    }
    catch (error) {

        console.error(error);
    }
}

// =====================================
// AUTO REFRESH
// =====================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        const customerInput =
            document.getElementById(
                "customerName"
            );

        if (customerInput) {

            customerInput.addEventListener(

                "change",

                loadOrders

            );

            customerInput.addEventListener(

                "blur",

                loadOrders

            );
        }

        // initial load
        loadOrders();

        setInterval(async () => {
            await loadOrders();

            if (currentOrderId) {
                await loadTimeline(currentOrderId);
            }
        }, 2000);

    }

);