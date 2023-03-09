//  Сбросить фильтры
$('#reset-filters').click(function() {
    if (typeof filterParams !== 'undefined') {
        filterParams.forEach(param => {
            url.searchParams.delete(param)
        })
        window.location = url
    }
    else
        location.reload()
})

//  Переключение страниц
let url = new URL(window.location);
let page = Number(url.searchParams.get('page'))
if (!page)
    page = 1
//  Назад
$('.prev-page').click(function() {
    url.searchParams.set('page', page-1)
    window.location = url
})
//  Вперёд
$('.next-page').click(function() {
    url.searchParams.set('page', page+1)
    window.location = url
})
//  Конкретная страница
$('.pages-list a').click(function() {
    event.preventDefault()
    page = Number($(this).text())
    url.searchParams.set('page', page)
    window.location = url
})

//  Чекбокс "Выбрать все"
$('.table_product input#cb').change(function() {
    let checked = $(this).prop('checked')
    $('.table_product .custom-checkbox').each(function() {
        $(this).prop('checked', checked)
    })
})

//  Dropdown "Действие"
$('.action > .dropdown > button').click(function() {
    $(this).parent().find('div').toggle()
})