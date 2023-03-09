function updateRedNotifyCounters() {
    $.ajax({
        url: '/get_notify_count'
    }).done(function (data) {
        // Количество товаров в корзине
        if (data.cart == 0)
            $('#cart-counter').hide()
        else {
            $('#cart-counter').show()
            $('#cart-counter').text(data.cart)
        }
    
        // Количество заказов
        if (data.order == 0)
            $('#orders-counter').hide()
        else {
            $('#orders-counter').show()
            $('#orders-counter').text(data.order)
        }
    })
}
updateRedNotifyCounters()