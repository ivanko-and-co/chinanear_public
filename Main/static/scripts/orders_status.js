function change_status(data) {
    fetch('/profile/order_change_status', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
}

var orders_check = document.querySelectorAll("[name='checkbox']")
button = document.querySelector("#cancel-all")
button.addEventListener('click', function() {
    let data = {};
    orders_check.forEach(order => {
        if (order.checked) {
            data[order.closest('.offer').dataset.id] = 'Cancelled'
        }
    });
    change_status(data)
})

document.querySelectorAll(".cancel_offer").forEach(button => {
    button.addEventListener('click', function() {
        let data = {};
        data[button.closest('.offer').dataset.id] = 'Cancelled';
        change_status(data)
    })
})