
//  Добавление товара в корзину
function addToCart(uid) {
    $.ajax({
        url: `/cart/add/${uid.toUpperCase()}`,
        method: 'get',
    }).done(() => {
        updateRedNotifyCounters()
    })
}

//  Удаление товара из корзины (На странице содержимого корзины)
function removeFromCart(uid) {
    let item = $(`.orders[data-uid="${uid}"]`)
    let delivery = item.parent()
    
    item.remove()
    if (delivery.find('.orders').length == 0) // Товаров от этого продавца не осталось
        delivery.remove() // Удаляем блок продавца

    delete cart[uid.toUpperCase()]

    $.ajax({
        url: `/cart/delete/${uid.toUpperCase()}`,
        method: 'get',
    }).done(() => {
        //  Товары в корзине закончились
        if (Object.keys(cart).length == 0)
            location.reload()
        else
            updateRedNotifyCounters()
    })
}

//  Подсчёт стоимости всех товаров в корзине (На странице содержимого корзины)
function calcCartPrice() {
    let total = 0
    $('.total-price').each(function() {
        total += Number($(this).text())
    })
    $('.full-cart-price').text(total)
}

$(() => {
    //  Кнопка "Добавить в корзину" на странице с товаром
    $('button[name="addtocart"].price__button').click(function() {
        let uid = window.location.href.split('/').slice(-1)[0]
        addToCart(uid)
    })

    //  Кнопка "Отправить" при предложении своей цены на странице с товаром
    $('#send-quantity-price').click(function() {
        event.preventDefault()
        let form = $(this).closest('.quantity-price')
        let productUid = form.data('p_uid')
        let sellerUid = form.data('seller_uid')
        let quantity = Number($('#quantityQuan').val())
        let price = Number($('#quantityPrice').val())
        
        $.ajax({
            url: '/order/custom_add',
            data: {
                productUid: productUid,
                sellerUid: sellerUid,
                quantity: quantity,
                price: price
            }
        })
    })

    //  Чекбокс "Выбрать все" в корзине
    $('.cart__menu input#cb1').change(function() {
        let checked = $(this).prop('checked')
        $('.tovar__check .checkbox__box').each(function() {
            $(this).prop('checked', checked)
        })
    })

    //  Кнопка "Удалить" под товаром в корзине
    $('.delete-order-link').click(function() {
        event.preventDefault()
        let order = $(this).closest('.orders')
        removeFromCart(order.data('uid'))
    })

    //  Кнопка "Удалить выбранные" в корзине
    $('.cart__menu .delete__button').click(function() {
        event.preventDefault()
        $('.tovar__check .checkbox__box:checked').each(function() {
            let order = $(this).closest('.orders')
            removeFromCart(order.data('uid'))
        })
    })

    //  Прогрузка корзины
    $('.orders').each(function() {
        let inp = $(this).find('input.number')
        let uid = $(this).data('uid').toUpperCase()

        let minAmount = 9999999999 // Минимум для покупки
        let maxAmount = 1 // Максимум
        let curAmount = inp.val()
        let pricePerItem = 0

        cart[uid].forEach(function(offer) {
            if (offer['quantity-max'] > maxAmount)
                maxAmount = offer['quantity-max']

            if (offer['quantity-min'] < minAmount)
                minAmount = offer['quantity-min']
        })

        inp.attr('min', minAmount)
        inp.attr('max', maxAmount)
        if (curAmount < minAmount)
            curAmount = minAmount
        else if (curAmount > maxAmount)
            curAmount = maxAmount
        inp.val(curAmount)

        cart[uid].forEach(function(offer) {
            if (offer['quantity-min'] <= curAmount && offer['quantity-max'] >= curAmount)
                pricePerItem = offer['price']
        })

        $(this).find('.item-price').text(pricePerItem)
        $(this).find('.total-price').text(pricePerItem * curAmount)
    })
    calcCartPrice()

    //  Смена количества товара в корзине
    $('.order__counter input').change(function() {
        let order = $(this).closest('.orders')
        let uid = order.data('uid').toUpperCase()
        let curAmount = Number($(this).val())

        if (curAmount < $(this).attr('min')) {
            curAmount = $(this).attr('min')
        }
        else if (curAmount > $(this).attr('max')) {
            curAmount = $(this).attr('max')
        }
        $(this).val(curAmount)

        let pricePerItem = 0
        
        cart[uid].forEach(function(offer) {
            if (offer['quantity-min'] <= curAmount && offer['quantity-max'] >= curAmount)
                pricePerItem = offer['price']
        })

        order.find('.item-price').text(pricePerItem)
        order.find('.total-price').text(pricePerItem * curAmount)
        calcCartPrice()
    })

    //  Кнопка "Оформить" в корзине
    $('#send-offer').click(function() {
        $('#send-offer').attr('disabled', true)
        $('.delivery').each(function() {
            let offer = {}
            offer['seller_uid'] = $(this).find('.deliver').data('uid').toUpperCase()
            offer['comment'] = $(this).find('.order__textarea').val()
            offer['address'] = $('.delivery__adress').text()

            offer['orders'] = []
            $(this).find('.orders').each(function() {
                let order = {
                    uid: $(this).data('uid').toUpperCase(),
                    amount: Number($(this).find('.order__counter input').val()),
                    itemPrice: Number($(this).find('.item-price').text()),
                    totalPrice: Number($(this).find('.total-price').text())
                }
                offer['orders'].push(order)
            })

            $.ajax({
                type: 'POST',
                url: '/order/add',
                data: JSON.stringify(offer),
                dataType: 'application/json',
                async: false,
                encode: true
            })
        })
        location.reload()
    })
    //  Выключение кнопки "Оформить" в корзине если корзина пустая
    if ($('.delivery').length == 0) {
        if ($('#send-offer').length != 0)
            $('#send-offer').attr('disabled', true)
    }

    //  Количество товаров на странице каталога
    let perPage = 15
    if (Cookies.get('perpage'))
        perPage = Cookies.get('perpage')
    $('#perpage-select').val(perPage)

    $('#perpage-select').change(function() {
        let perPage = $(this).find(':selected').val()
        Cookies.set('perpage', perPage, { expires: 28, path: '/' })
        location.reload()
    })

    //  Переключение страниц
    let url = new URL(window.location);
    let page = Number(url.searchParams.get('page'))
    if (!page)
        page = 1
    //  Назад
    $('#prev-page').click(function() {
        url.searchParams.set('page', page-1)
        window.location = url
    })
    //  Вперёд
    $('#next-page').click(function() {
        url.searchParams.set('page', page+1)
        window.location = url
    })
    //  Конкретная страница
    $('.pagescounter__link').click(function() {
        event.preventDefault()
        page = Number($(this).text())
        url.searchParams.set('page', page)
        window.location = url
    })
})