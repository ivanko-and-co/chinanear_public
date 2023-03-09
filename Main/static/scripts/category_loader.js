//  Подгрузка категорий
function loadSubcategory(category, level, callback) {
    $.ajax({
        url: `/get_subcategory/${level}/${category}`
    }).done(function(data) {
        // Загруженная подкатегория
        let loaded = $(`#category_${level+1}`)
        loaded.attr('disabled', null)

        // Очистка списка категорий в подкатегории
        let firstOption = loaded.find('option:disabled')
        firstOption.nextAll().remove()

        // Загрузка новых категорий в подкатегорию
        data.forEach(option => {
            loaded.append(`<option value="${option[1]}">${option[0]}</option>`)
        });

        if (typeof callback !== 'undefined')
            callback()
    })
}

$('#category_1').change(function() {
    loadSubcategory($(this).val(), 1)
})

$('#category_2').change(function() {
    loadSubcategory($(this).val(), 2)
})