// =====================================
// TOAST NOTIFICATIONS
// =====================================

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// =====================================
// LOAD DASHBOARD
// =====================================

let currentSelectedOrder = null;

async function loadDashboard() {

    await loadOrders();

    await loadWorkers();
    await loadInventory();
}

// =====================================
// LOAD INVENTORY
// =====================================

async function loadInventory() {

    try {

        const response = await fetch("/api/inventory");

        const inventory = await response.json();

        let html = "";

        inventory.forEach(item => {

            const low = item.stock <= item.reorder_level;

            html += `

            <tr>

                <td class="px-6 py-4">${item.product}</td>

                <td class="px-6 py-4">${item.stock} ${low ? '<span class="text-sm text-red-600 font-semibold">Low Stock</span>' : ''}</td>

            </tr>

            `;

        });

        const el = document.getElementById("inventoryTable");

        if (el) el.innerHTML = html;

    }
    catch (err) {

        console.error(err);
    }

}


// =====================================
// ADMIN: Inventory Management
// =====================================

async function loadInventoryAdmin() {

    try {
        const res = await fetch('/api/inventory');
        const items = await res.json();

        let html = '';
        let totalProducts = items.length;
        let lowStockCount = 0;
        let outOfStockCount = 0;
        let totalValue = 0;

        items.forEach(it => {
            let statusClass = '';
            let statusText = '';
            
            if (it.stock <= 0) {
                statusClass = 'bg-red-50 text-red-700';
                statusText = 'Out of stock';
                outOfStockCount++;
            } else if (it.stock <= it.reorder_level) {
                statusClass = 'bg-yellow-50 text-yellow-700';
                statusText = 'Low stock';
                lowStockCount++;
            } else {
                statusClass = 'bg-green-50 text-green-700';
                statusText = 'In stock';
            }
            
            const imgHtml = it.image_path ? `<img src="/static/${it.image_path}" class="w-10 h-10 object-cover rounded-lg" />` : '<div class="w-10 h-10 bg-slate-100 rounded-lg"></div>';
            const price = it.price ? parseFloat(it.price) : 0;
            totalValue += price * it.stock;
            
            html += `
                        <tr class="hover:bg-slate-50 transition">
                            <td class="px-6 py-4 font-medium">${it.product}</td>
                            <td class="px-6 py-4">${imgHtml}</td>
                            <td class="px-6 py-4 font-semibold">${it.stock}</td>
                            <td class="px-6 py-4">${it.reorder_level}</td>
                            <td class="px-6 py-4">₱${price.toFixed(2)}</td>
                            <td class="px-6 py-4">
                                <span class="px-3 py-1 rounded-full text-xs font-semibold ${statusClass}">
                                    ${statusText}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex gap-2">
                                    <button onclick="openEdit(${it.id})" class="px-3 py-1 text-sm rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-medium transition">Edit</button>
                                    <button onclick="removeItem(${it.id})" class="px-3 py-1 text-sm rounded-lg bg-red-50 text-red-600 hover:bg-red-100 font-medium transition">Delete</button>
                                </div>
                            </td>
                        </tr>`;
        });

        const el = document.getElementById('adminInventoryTable');
        if (el) el.innerHTML = html;

        // Update summary cards
        if (document.getElementById('totalProducts')) document.getElementById('totalProducts').textContent = totalProducts;
        if (document.getElementById('lowStockCount')) document.getElementById('lowStockCount').textContent = lowStockCount;
        if (document.getElementById('outOfStockCount')) document.getElementById('outOfStockCount').textContent = outOfStockCount;
        updateInventoryValue(totalValue);
    } catch (e) {
        console.error(e);
    }
}

function updateInventoryValue(totalValue) {
    const el = document.getElementById('inventoryValue');
    if (!el) return;

    const value = '₱' + totalValue.toFixed(2);
    el.textContent = value;

    let fontSize = 48;
    const minFontSize = 20;
    el.style.fontSize = fontSize + 'px';
    el.style.lineHeight = '1';

    while (
        el.parentElement &&
        el.scrollWidth > el.parentElement.clientWidth &&
        fontSize > minFontSize
    ) {
        fontSize -= 2;
        el.style.fontSize = fontSize + 'px';
    }
}

function showModal(title) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal').classList.add('flex');
}

function hideModal() {
    document.getElementById('modal').classList.add('hidden');
    document.getElementById('modal').classList.remove('flex');
}

document.addEventListener('DOMContentLoaded', () => {
    const show = document.getElementById('showAdd');
    if (show) {
        show.addEventListener('click', () => {
            window._editId = null;
            document.getElementById('prodName').value = '';
            document.getElementById('prodStock').value = '';
            document.getElementById('prodReorder').value = '';
            document.getElementById('prodPrice').value = '';
            const preview = document.getElementById('prodPreview');
            const imageInput = document.getElementById('prodImage');
            if (preview) { preview.src = ''; preview.classList.add('hidden'); }
            if (imageInput) imageInput.value = '';
            showModal('Add product');
        });

        document.getElementById('cancelBtn').addEventListener('click', hideModal);

        document.getElementById('saveBtn').addEventListener('click', async () => {
            const name = document.getElementById('prodName').value.trim();
            const stock = document.getElementById('prodStock').value;
            const reorder = document.getElementById('prodReorder').value;
            const price = document.getElementById('prodPrice').value;
            const imageInput = document.getElementById('prodImage');
            const imageFile = imageInput && imageInput.files && imageInput.files[0] ? imageInput.files[0] : null;

            if (!name) {
                showToast('Product name required', 'error');
                return;
            }

            if (window._editId) {
                // update
                // support multipart/form-data to upload image
                const form = new FormData();
                form.append('stock', stock);
                form.append('reorder_level', reorder);
                form.append('price', price);
                if (imageFile) form.append('image', imageFile, imageFile.name);

                const res = await fetch(`/api/inventory/${window._editId}`, {
                    method: 'PUT',
                    body: form
                });
                const j = await res.json();
                if (!j.success) {
                    showToast(j.message || 'Error updating product', 'error');
                    return;
                }
                showToast('Product updated successfully', 'success');
            } else {
                const form = new FormData();
                form.append('product', name);
                form.append('stock', stock);
                form.append('reorder_level', reorder);
                form.append('price', price);
                if (imageFile) form.append('image', imageFile, imageFile.name);

                const res = await fetch('/api/inventory', {
                    method: 'POST',
                    body: form
                });
                const j = await res.json();
                if (!j.success) {
                    showToast(j.message || 'Error creating product', 'error');
                    return;
                }
                showToast('Product created successfully', 'success');
            }

            hideModal();
            if (document.getElementById('adminInventoryTable')) loadInventoryAdmin();
            if (document.getElementById('inventoryTable')) loadInventory();
        });
    }
    // if admin inventory table exists on page, load it
    if (document.getElementById('adminInventoryTable')) {
        loadInventoryAdmin();
    }
    // SPA: show dashboard by default
    if (typeof showSection === 'function') showSection('dashboard');
});

function showSection(section) {
    document.querySelectorAll('.content-section').forEach(el => {
        el.classList.add('hidden');
    });

    const sel = document.getElementById(section + 'Section');
    if (sel) sel.classList.remove('hidden');

    document.querySelectorAll('nav a[data-section]').forEach(a => {
        if (a.dataset.section === section) {
            a.classList.add('bg-primary');
        } else {
            a.classList.remove('bg-primary');
        }
    });

    // trigger section-specific loaders
    if (section === 'inventory') {
        if (window.loadInventoryAdmin) loadInventoryAdmin();
    }

    if (section === 'dashboard') {
        if (window.loadDashboard) loadDashboard();
    }
    if (section === 'analytics') {
        if (window.loadAnalytics) loadAnalytics();
    }
}

// =====================================
// ANALYTICS
// =====================================

async function loadAnalytics() {
    try {
        const [aRes, wRes] = await Promise.all([
            fetch('/api/analytics'),
            fetch('/api/worker-metrics')
        ]);

        if (!aRes.ok || !wRes.ok) {
            showToast('Failed to load analytics', 'error');
            return;
        }

        const analytics = await aRes.json();
        const workers = await wRes.json();

        // summary - with safety checks
        const totalEl = document.getElementById('analytic_total');
        const completedEl = document.getElementById('analytic_completed');
        const pendingEl = document.getElementById('analytic_pending');
        const outofstockEl = document.getElementById('analytic_outofstock');

        if (totalEl) totalEl.textContent = analytics.summary.total || 0;
        if (completedEl) completedEl.textContent = analytics.summary.completed || 0;
        if (pendingEl) pendingEl.textContent = analytics.summary.pending || 0;
        if (outofstockEl) outofstockEl.textContent = analytics.summary.out_of_stock || 0;

        // products chart
        const products = analytics.most_ordered || [];
        const labels = products.map(p => p.product);
        const data = products.map(p => p.count);
        if (!window._charts) window._charts = {};
        const chartProductsEl = document.getElementById('chartProducts');
        if (chartProductsEl) {
            const ctxP = chartProductsEl.getContext('2d');
            if (window._charts.products) window._charts.products.destroy();
            window._charts.products = new Chart(ctxP, {
                type: 'bar',
                data: { labels, datasets: [{ label: 'Orders', data, backgroundColor: '#0f172a' }] },
                options: { responsive: true }
            });
        }

        // workers chart
        const chartWorkersEl = document.getElementById('chartWorkers');
        if (chartWorkersEl) {
            const wlabels = Object.keys(workers.workers || {});
            const wdata = wlabels.map(k => workers.workers[k].orders_processed || 0);
            const ctxW = chartWorkersEl.getContext('2d');
            if (window._charts.workers) window._charts.workers.destroy();
            window._charts.workers = new Chart(ctxW, {
                type: 'doughnut',
                data: { labels: wlabels, datasets: [{ data: wdata, backgroundColor: ['#334155','#0f172a','#475569'] }] },
                options: { responsive: true }
            });
        }

        // worker stats text
        const statEl = document.getElementById('workerStats');
        if (statEl) {
            let statHtml = '';
            for (const [name, m] of Object.entries(workers.workers || {})) {
                statHtml += `<div class="mb-2"><strong>${name}</strong>: ${m.orders_processed} orders • ${m.busy_time_seconds}s • ${m.utilization_percent}%</div>`;
            }
            statEl.innerHTML = statHtml;
        }

    } catch (err) {
        console.error('Failed to load analytics', err);
        showToast('Error loading analytics', 'error');
    }
}

async function runBenchmark(count) {
    const resEl = document.getElementById('benchmarkTable');
    if (!resEl) return;

    // Check if row already exists for this count
    const existingRow = Array.from(resEl.querySelectorAll('tr')).find(row => {
        const firstCell = row.querySelector('td');
        return firstCell && firstCell.textContent.trim() === count.toString();
    });

    let tr;
    if (existingRow) {
        // Update existing row
        tr = existingRow;
        tr.innerHTML = `<td class="px-3 py-2">${count}</td><td class="px-3 py-2">Running...</td><td class="px-3 py-2">Running...</td>`;
    } else {
        // Create new row
        tr = document.createElement('tr');
        tr.innerHTML = `<td class="px-3 py-2">${count}</td><td class="px-3 py-2">Running...</td><td class="px-3 py-2">Running...</td>`;
        resEl.prepend(tr);
    }

    try {
        const resp = await fetch(`/api/benchmark?count=${count}`);
        if (!resp.ok) {
            showToast(`Benchmark failed for ${count} orders`, 'error');
            tr.innerHTML = `<td class="px-3 py-2">${count}</td><td class="px-3 py-2">Error</td><td class="px-3 py-2">Error</td>`;
            return;
        }
        const j = await resp.json();
        tr.innerHTML = `<td class="px-3 py-2">${j.count}</td><td class="px-3 py-2">${Number(j.sequential_seconds).toFixed(2)}</td><td class="px-3 py-2">${Number(j.parallel_seconds).toFixed(2)}</td>`;
    } catch (err) {
        console.error('Benchmark error:', err);
        tr.innerHTML = `<td class="px-3 py-2">${count}</td><td class="px-3 py-2">Error</td><td class="px-3 py-2">Error</td>`;
    }
}

async function openEdit(id) {
    const res = await fetch('/api/inventory');
    const items = await res.json();
    const it = items.find(x => x.id === id);
    if (!it) return alert('Item not found');
    window._editId = id;
    document.getElementById('prodName').value = it.product;
    document.getElementById('prodStock').value = it.stock;
    document.getElementById('prodReorder').value = it.reorder_level;
    document.getElementById('prodPrice').value = it.price || '';
    const preview = document.getElementById('prodPreview');
    const imageInput = document.getElementById('prodImage');
    if (it.image_path) {
        preview.src = `/static/${it.image_path}`;
        preview.classList.remove('hidden');
    } else {
        preview.src = '';
        preview.classList.add('hidden');
    }
    if (imageInput) imageInput.value = '';
    showModal('Edit product');
}

async function removeItem(id) {
    if (!confirm('Delete this item?')) return;
    try {
        const res = await fetch(`/api/inventory/${id}`, {method: 'DELETE'});
        const j = await res.json();
        if (!j.success) {
            showToast(j.message || 'Error deleting product', 'error');
            return;
        }
        showToast('Product deleted successfully', 'success');
        if (document.getElementById('adminInventoryTable')) loadInventoryAdmin();
        if (document.getElementById('inventoryTable')) loadInventory();
    } catch (err) {
        console.error('Delete error:', err);
        showToast('Error deleting product', 'error');
    }
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
        let outOfStock = 0;

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
            else if (
                status.includes("Out of Stock")
            ) {
                // Don't count out-of-stock in processing
            }
            else if (
                status.includes("Out of Stock")
            ) {
                outOfStock++;
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
                status.includes("Out of Stock")
            ) {
                badgeClass =
                    "bg-red-100 text-red-700";
            }

            if (
                status.includes("Queue") ||
                status.includes("Pending")
            ) {

                badgeClass =
                    "bg-yellow-100 text-yellow-700";
            }

            const isSelected = order.id === currentSelectedOrder ? "bg-blue-50" : "";

            html += `

            <tr
                class="hover:bg-slate-50 cursor-pointer transition ${isSelected}"
                onclick="selectOrder('${order.id}')">

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
            "outOfStockCount"
        ).textContent = outOfStock;

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

                let statusColor = "text-gray-600";
                let statusIndicator = "● ";
                let displayStatus = status;

                if (String(status).toLowerCase().includes("idle")) {
                    statusColor = "text-gray-500";
                    statusIndicator = "● ";
                    displayStatus = "Idle";
                } else if (String(status).toLowerCase().includes("active") || String(status).toLowerCase().includes("processing")) {
                    statusColor = "text-green-600";
                    statusIndicator = "● ";
                    displayStatus = "Active";
                } else {
                    statusColor = "text-slate-600";
                    displayStatus = status;
                }

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
                            ${statusColor}
                            text-sm
                            font-semibold">

                            ${statusIndicator}${displayStatus}

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
// SELECT ORDER (with highlighting)
// =====================================

function selectOrder(orderId) {
    currentSelectedOrder = orderId;
    loadTimeline(orderId);
    loadOrders();
}

// =====================================
// LOGOUT
// =====================================

function logout() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/login';
        })
        .catch(err => {
            console.error('Logout failed:', err);
            showToast('Logout failed', 'error');
        });
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
// RESET DATABASE (Admin Feature)
// =====================================

function confirmReset() {
    const modal = document.getElementById('resetModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function cancelReset() {
    const modal = document.getElementById('resetModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

async function executeReset() {
    try {
        const response = await fetch('/api/admin/reset-database', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showToast('✓ Database reset successfully.', 'success');
            
            // Close modal
            cancelReset();
            
            // Refresh all dashboard sections
            await loadDashboard();
            await loadInventoryAdmin();
            await loadAnalytics();
            
            // Clear timeline
            const timelineContainer = document.getElementById('timelineContainer');
            if (timelineContainer) {
                timelineContainer.innerHTML = '';
            }
            
            // Update filter to show all
            if (document.getElementById('filterAll')) {
                filterOrders('all');
            }
        } else {
            showToast('✕ Failed to reset database.', 'error');
        }
    } catch (error) {
        console.error('Reset error:', error);
        showToast('✕ Failed to reset database.', 'error');
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
