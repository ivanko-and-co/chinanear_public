function removeOffer(id, status) {
    console.log(id, status);
    $.ajax({
        url: `/profile/order_change_status/${id}/${status}`,
        method: 'post',
    })
}


//  Кнопка "Отменить" в заказах
$('#cancel-all').click(function() {
    event.preventDefault()
    $('.offer .custom-checkbox:checked').each(function() {
        let offer = $(this).closest('.offer')
        removeOffer(offer.data('id'), 'Cancelled')
    })
})
//  Отмена конкретного заказа через три точки
$('.cancel_offer').click(function() {
    event.preventDefault()
    let offer = $(this).closest('.offer')
    removeOffer(offer.data('id'), 'Cancelled')
})