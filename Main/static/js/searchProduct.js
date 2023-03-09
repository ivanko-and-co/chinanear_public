$('#seller-search').keyup(function() {
    let text = $(this).val();
    //  Скрытие выпадающего меню
    if (text === '') {
        $('#sellers-list').hide()
        return;
    }
    //  Очистка старых записей в меню
    $('#sellers-list').empty()
    
    text = text.toLowerCase()
    $.ajax({
        url: '/search_seller',
        data: {
            search: text,
        },
        method: 'POST'
    }).done(function(result) {
        $('#sellers-list').empty()

        //  Заполнение новыми записями в выпадающем меню
        if (result.length == 0) {
            $('#sellers-list').append(`<li class="sellers-list__li">Продавец не найден.</li>`)
            $('#sellers-list').show()
            return;
        }
        result.forEach(product => {
            $('#sellers-list').append(`<li class="sellers-list__li"><a href="product/${product[1]}">${product[0]}</a></li>`)
        })
        $('#sellers-list').show()
    })
})