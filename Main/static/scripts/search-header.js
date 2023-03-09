//  Ввод текста в поле для поиска
$('.header__search input').keyup(function() {
    let resultsBlock = $('.header__serch-menu')
    let text = $(this).val().toLowerCase()

    if (text == '') {
        resultsBlock.hide()
        return
    }

    $.ajax({
        url: '/search_product_and_img',
        data: {
            search: text,
        },
        method: 'POST'
    }).done(function(result) {
        if (result.length == 0) {
            resultsBlock.hide()
            return
        }
        resultsBlock.empty()

        result.forEach(product => {
            let img = JSON.parse(product[1])
            let imgUrl = img['photo-url']
            if (!imgUrl)
                imgUrl = ''

            resultsBlock.append(`
                <a class="serch-menu__item" data-uid="${product[2]}">
                    <img src="${imgUrl}" class="serch-menu__img">
                    <div class="serch-menu__title">${product[0]}</div>
                </a>
            `)
        })
        resultsBlock.show()
    })
})

//  Нажатие на кнопку поиска
$('.header__search button').click(function() {
    event.preventDefault()
    $('.header__search input').focus()
})

//  Нажатие на найденый товар
$(document).on('click', '.header__search a', function() {
    event.preventDefault()
    let uid = $(this).data('uid')
    location.href = `/get_product_url_by_uid/${uid}`
})