// GLOBAL FUNCTIONS
window.changeQty = function (id, delta) {
    const qtySpan = document.getElementById(`qty${id}`);
    if (!qtySpan) return;

    let qty = parseInt(qtySpan.innerText);
    let newQty = qty + delta;

    // Update backend
    updateCartQty(id, delta);

    if (newQty <= 0) {
        const item = document.getElementById(`item-${id}`);
        if (item) item.remove();
    } else {
        qtySpan.innerText = newQty;
    }

    // ✅ UPDATE TOTAL AFTER CHANGE
    updateTotal();
};

window.updateCartQty = function (productId, change) {
    const formData = new FormData();
    formData.append("product_id", productId);
    formData.append("change", change);

    fetch("/update-cart-qty/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData
    });
};

window.getCookie = function (name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.split("=")[1]);
        }
    });
    return cookieValue;
};

// ✅ TOTAL CALCULATION
function updateTotal() {
    let total = 0;

    document.querySelectorAll('.wishlist-item').forEach(item => {
        const price = parseFloat(item.dataset.price);
        const id = item.dataset.id;
        const qtySpan = document.getElementById(`qty${id}`);

        if (qtySpan) {
            const qty = parseInt(qtySpan.innerText);
            total += price * qty;
        }
    });

    document.getElementById('totalPrice').innerText = total.toFixed(2);
}
