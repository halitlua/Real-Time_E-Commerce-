// =====================================
// PLACE ORDER
// =====================================
let currentOrderId = null;
let currentFilter = 'all';
let allOrders = [];

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

async function placeOrder() {
    const product = document.getElementById("product").value;
    const qty = document.getElementById("qty").value;

    if (!product) {
        showToast("Please select a product.", 'error');
        return;
    }

    try {
        const response = await fetch("/api/place-order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product, qty })
        });

        if (!response.ok) {
            const error = await response.json();
            showToast(error.error || "Failed to create order.", 'error');
            return;
        }

        const result = await response.json();

        showToast(`✓ Order submitted successfully\n\nOrder ID: ${result.order_id}\n\nTrack your order using the Order History section.`);

        loadOrders();
    }
    catch (error) {
        console.error(error);
        showToast("Failed to create order.", 'error');
    }
}

// =====================================
// LOAD CUSTOMER ORDERS
// =====================================

async function loadOrders() {
    const url = '/api/my-orders';

    try {
        const response = await fetch(url);
        const orders = await response.json();
        
        allOrders = orders;
        renderOrdersTable();
    }
    catch (error) {
        console.error(error);
    }
}

function renderOrdersTable() {
    let html = "";
    
    const ordersToDisplay = allOrders.filter(order => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'pending') {
            return String(order.status).includes("Pending") || String(order.status).includes("Queue");
        }
        if (currentFilter === 'completed') {
            return String(order.status).includes("Completed");
        }
        if (currentFilter === 'out-of-stock') {
            return String(order.status).includes("Out of Stock");
        }
        return true;
    });

    ordersToDisplay.forEach(order => {
        let badgeColor = "bg-blue-100 text-blue-700";

        if (String(order.status).includes("Completed")) {
            badgeColor = "bg-green-100 text-green-700";
        }

        if (String(order.status).includes("Pending") || String(order.status).includes("Queue")) {
            badgeColor = "bg-yellow-100 text-yellow-700";
        }
        
        if (String(order.status).includes("Out of Stock")) {
            badgeColor = "bg-red-100 text-red-700";
        }

        const isSelected = order.id === currentOrderId ? "bg-blue-50" : "";

        html += `
            <tr
                onclick="selectOrder('${order.id}')"
                class="
                hover:bg-slate-50
                cursor-pointer
                transition
                ${isSelected}">

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

    document.getElementById("ordersTable").innerHTML = html;
}

function selectOrder(orderId) {
    currentOrderId = orderId;
    loadTimeline(orderId);
    renderOrdersTable();
}

function filterOrders(filter) {
    currentFilter = filter;
    
    // Update filter button styles
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white');
        btn.classList.add('border', 'border-outline', 'text-slate-700', 'hover:bg-slate-50');
    });
    
    const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('border', 'border-outline', 'text-slate-700', 'hover:bg-slate-50');
        activeBtn.classList.add('bg-primary', 'text-white');
    }
    
    renderOrdersTable();
}

// =====================================
// LOAD TIMELINE
// =====================================

async function loadTimeline(orderId) {
    currentOrderId = orderId;
    try {
        document.getElementById("timelineTitle").textContent = `Order Timeline: ${orderId}`;

        const response = await fetch(`/api/timeline/${orderId}`);
        const events = await response.json();

        let html = "";

        events.forEach(event => {
            html += `
            <div class="relative z-10 flex items-start">
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

                <div class="ml-6">
                    <h4 class="font-semibold">${event.stage}</h4>
                    <p class="text-sm text-slate-500">${event.timestamp || ""}</p>
                </div>

            </div>

            `;
        });

        document.getElementById("timelineContainer").innerHTML = html;
        
        // Update progress bar
        calculateProgress(events);

    }
    catch (error) {
        console.error(error);
    }
}

function calculateProgress(events) {
    if (!events || events.length === 0) {
        document.getElementById('progressSection').classList.add('hidden');
        return;
    }

    document.getElementById('progressSection').classList.remove('hidden');
    
    const stages = ['Generating Shipping Label', 'Assigned to Worker', 'Processing', 'Packaging', 'Shipped'];
    const completedCount = Math.min(events.length, stages.length);
    const progressPercentage = Math.round((completedCount / stages.length) * 100);
    
    document.getElementById('progressBar').style.width = progressPercentage + '%';
    document.getElementById('progressPercentage').textContent = progressPercentage + '%';
    
    const currentStage = events.length > 0 ? events[events.length - 1].stage : 'Initializing';
    document.getElementById('progressStage').textContent = currentStage;
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
// AUTO REFRESH
// =====================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        // initial loads
        loadOrders();
        loadProducts();

        // refresh orders/timeline every 2s
        setInterval(async () => {
            await loadOrders();

            if (currentOrderId) {
                await loadTimeline(currentOrderId);
            }
        }, 2000);

        // refresh product list every 3s
        setInterval(loadProducts, 3000);

    }

);


// =====================================
// LOAD PRODUCTS (for customer dropdown)
// =====================================
async function loadProducts() {

    const sel = document.getElementById('product');

    if (!sel) return;

    try {
        // Store the currently selected product before clearing
        const previousSelection = sel.value;

        const resp = await fetch('/api/products');
        const products = await resp.json();

        // clear current options
        sel.innerHTML = '';

        if (!products || products.length === 0) {
            const opt = document.createElement('option');
            opt.textContent = 'No products available';
            opt.disabled = true;
            opt.selected = true;
            sel.appendChild(opt);
            return;
        }

        // store map for quick lookup
        window._products = {};
        products.forEach(p => {
            window._products[p.product] = p;
            const opt = document.createElement('option');
            opt.value = p.product;
            opt.textContent = `${p.product} (${p.stock} available)`;
            sel.appendChild(opt);
        });

        // when selection changes, update product details
        // Remove any existing listener first to prevent duplicates
        sel.removeEventListener('change', showProductDetails);
        sel.addEventListener('change', showProductDetails);

        // Restore previous selection if it still exists, otherwise use first product
        let selectionToShow = sel.options[0].value; // default to first
        if (previousSelection && window._products[previousSelection]) {
            // Product still exists, restore selection
            sel.value = previousSelection;
            selectionToShow = previousSelection;
        }

        // show details for selected (or restored) product
        if (selectionToShow) showProductDetails({ target: { value: selectionToShow } });

    } catch (err) {
        console.error('Failed to load products', err);
    }
}

function showProductDetails(evt) {
    const prodName = evt.target ? evt.target.value : evt;
    const data = window._products && window._products[prodName];
    const thumb = document.getElementById('prodThumb');
    const title = document.getElementById('prodTitle');
    const priceEl = document.getElementById('prodPrice');
    const stockEl = document.getElementById('prodStockAvailable');
    const submitBtn = document.getElementById('submitBtn');
    const qtySelect = document.getElementById('qty');

    if (!data) {
        if (thumb) { thumb.src = ''; thumb.classList.add('hidden'); }
        if (title) title.textContent = '';
        if (priceEl) priceEl.textContent = '';
        if (stockEl) stockEl.textContent = '';
        if (submitBtn) submitBtn.disabled = true;
        return;
    }

    if (data.image_path) {
        thumb.src = `/static/${data.image_path}`;
        thumb.classList.remove('hidden');
    } else {
        thumb.src = '';
        thumb.classList.add('hidden');
    }

    if (title) title.textContent = `${data.product}`;
    if (priceEl) priceEl.textContent = data.price ? `₱${Number(data.price).toFixed(2)}` : '-';
    
    // Stock status badge
    let stockText = '';
    let stockClass = '';
    if (data.stock <= 0) {
        stockText = 'Out of stock';
        stockClass = 'text-red-600 font-semibold';
        if (submitBtn) submitBtn.disabled = true;
    } else if (data.stock <= 5) {
        stockText = `Low stock - ${data.stock} available`;
        stockClass = 'text-orange-600 font-semibold';
        if (submitBtn) submitBtn.disabled = false;
    } else {
        stockText = `In stock - ${data.stock} available`;
        stockClass = 'text-green-600 font-semibold';
        if (submitBtn) submitBtn.disabled = false;
    }
    
    if (stockEl) {
        stockEl.textContent = stockText;
        stockEl.className = `text-sm mt-1 ${stockClass}`;
    }
    
    // Store the currently selected quantity before rebuilding
    const previousQty = parseInt(qtySelect.value) || 1;
    
    // Update quantity dropdown based on stock
    qtySelect.innerHTML = '';
    const maxQty = Math.min(data.stock, 10);
    for (let i = 1; i <= maxQty; i++) {
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = i;
        qtySelect.appendChild(opt);
    }
    
    // Restore the previous quantity if it's still valid
    if (previousQty <= maxQty && previousQty > 0) {
        qtySelect.value = previousQty;
    } else if (maxQty > 0) {
        // If previous quantity exceeds new stock, select the maximum available
        qtySelect.value = maxQty;
    }
    
    if (maxQty === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'Out of stock';
        opt.disabled = true;
        opt.selected = true;
        qtySelect.appendChild(opt);
    }
}