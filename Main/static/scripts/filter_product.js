//  Применить фильтры
filterParams = ['status', 'category_1', 'category_2', 'category_3']
$('#apply-filters').click(function() {
    let status = $('#product-status')
    if (status.length > 0) {
        status = status.val()
        if ($('#product-status').prop('selectedIndex') !== 0)
            url.searchParams.set('status', status)
        else
            url.searchParams.delete('status')
    }

    let category_1 = $('#category_1').val()
    if ($('#category_1').prop('selectedIndex') !== 0)
        url.searchParams.set('category_1', category_1)
    else
        url.searchParams.delete('category_1')

    let category_2 = $('#category_2').val()
    if ($('#category_2').prop('selectedIndex') !== 0)
        url.searchParams.set('category_2', category_2)
    else
        url.searchParams.delete('category_2')

    let category_3 = $('#category_3').val()
    if ($('#category_3').prop('selectedIndex') !== 0)
        url.searchParams.set('category_3', category_3)
    else
        url.searchParams.delete('category_3')

    window.location = url
})

$(() => {
    //  Загрузка фильтров при загрузке страницы
    let status = url.searchParams.get('status')
    if (status != null)
        $('#product-status').val(status)

    let category_1 = url.searchParams.get('category_1')
    if (category_1 != null) {
        $('#category_1').val(category_1)
        loadSubcategory(category_1, 1, () => {
            let category_2 = url.searchParams.get('category_2')
            if (category_2 != null) {
                $('#category_2').val(category_2)
                loadSubcategory(category_2, 2, () => {
                    let category_3 = url.searchParams.get('category_3')
                    if (category_3 != null)
                        $('#category_3').val(category_3)
                })
            }
        })
    }
})