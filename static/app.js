// =====================================
// LOAD DASHBOARD
// =====================================

async function loadDashboard() {

    await loadOrders();

    await loadWorkers();
}

// =====================================
// LOAD ORDERS
// =====================================

async function loadOrders(searchText = "") {

    try {

        const response =
            await fetch("/api/orders");

        const orders =
            await response.json();

        let html = "";

        let queue = 0;
        let processing = 0;
        let completed = 0;

        orders.forEach(order => {

            const search =
                searchText.toLowerCase();

            if (
                search &&
                !String(order.id).toLowerCase().includes(search) &&
                !String(order.customer).toLowerCase().includes(search) &&
                !String(order.product).toLowerCase().includes(search)
            ) {
                return;
            }

            const status =
                String(order.status);

            if (
                status.includes("Queue") ||
                status.includes("Pending")
            ) {

                queue++;

            }
            else if (
                status.includes("Completed")
            ) {

                completed++;

            }
            else {

                processing++;
            }

            let badgeClass =
                "bg-blue-100 text-blue-700";

            if (
                status.includes("Completed")
            ) {

                badgeClass =
                    "bg-green-100 text-green-700";
            }

            if (
                status.includes("Queue") ||
                status.includes("Pending")
            ) {

                badgeClass =
                    "bg-yellow-100 text-yellow-700";
            }

            html += `

            <tr
                class="hover:bg-slate-50 cursor-pointer transition"
                onclick="loadTimeline('${order.id}')">

                <td class="px-6 py-4 font-mono text-sm">

                    ${order.id}

                </td>

                <td class="px-6 py-4">

                    ${order.customer}

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
                        ${badgeClass}">

                        ${order.status}

                    </span>

                </td>

                <td class="px-6 py-4">

                    ${(order.worker || "-").replaceAll("-", " ")}

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

        document.getElementById(
            "queueCount"
        ).textContent = queue;

        document.getElementById(
            "processingCount"
        ).textContent = processing;

        document.getElementById(
            "completedCount"
        ).textContent = completed;

        document.getElementById(
            "totalCount"
        ).textContent = orders.length;

    }
    catch (error) {

        console.error(error);
    }
}

// =====================================
// LOAD WORKERS
// =====================================

async function loadWorkers() {

    try {

        const response =
            await fetch("/api/workers");

        const workers =
            await response.json();

        let html = "";

        Object.entries(workers).forEach(

            ([name, status]) => {

                html += `

                <div
                    class="
                    border
                    border-slate-200
                    rounded-2xl
                    p-5">

                    <div
                        class="
                        flex
                        justify-between
                        items-center">

                        <h3
                            class="
                            font-bold
                            text-lg">

                            ${name}

                        </h3>

                        <span
                            class="
                            text-green-600
                            text-sm
                            font-semibold">

                            ● ACTIVE

                        </span>

                    </div>

                    <div
                        class="
                        mt-4
                        text-slate-600">

                        Current Status

                    </div>

                    <div
                        class="
                        mt-1
                        font-semibold">

                        ${status}

                    </div>

                </div>

                `;
            }
        );

        document.getElementById(
            "workersContainer"
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

    try {

        document.getElementById(
            "selectedOrder"
        ).textContent = orderId;

        const response =
            await fetch(
                `/api/timeline/${orderId}`
            );

        const timeline =
            await response.json();

        let html = "";

        timeline.forEach(event => {

            html += `

            <div
                class="
                flex
                gap-4">

                <div
                    class="
                    w-4
                    h-4
                    rounded-full
                    bg-blue-600
                    mt-1
                    shrink-0">

                </div>

                <div>

                    <div
                        class="
                        font-semibold">

                        ${event.stage}

                    </div>

                    <div
                        class="
                        text-sm
                        text-slate-500">

                        ${event.timestamp}

                    </div>

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
// GENERATE ORDERS
// =====================================

async function generateOrders(count) {

    try {

        await fetch(

            `/api/generate/${count}`,

            {
                method: "POST"
            }

        );

        loadDashboard();

    }
    catch (error) {

        console.error(error);
    }
}

// =====================================
// CLEAR DATABASE
// =====================================

async function clearDatabase() {

    if (
        !confirm(
            "Delete all orders?"
        )
    ) {
        return;
    }

    try {

        await fetch(

            "/api/clear",

            {
                method: "POST"
            }

        );

        loadDashboard();

        document.getElementById(
            "timelineContainer"
        ).innerHTML = "";

    }
    catch (error) {

        console.error(error);
    }
}

// =====================================
// SEARCH
// =====================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        const searchBox =
            document.getElementById(
                "searchBox"
            );

        if (searchBox) {

            searchBox.addEventListener(

                "input",

                () => {

                    loadOrders(
                        searchBox.value
                    );
                }
            );
        }

        loadDashboard();

        setInterval(

            loadDashboard,

            2000
        );
    }
);