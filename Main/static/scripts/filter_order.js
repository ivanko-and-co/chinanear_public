//  Применить фильтры
filterParams = ['status', 'min_date', 'max_date']
$('#apply-filters').click(function() {
    let status = $('#offer-status').val()
    if ($('#offer-status').prop('selectedIndex') !== 0)
        url.searchParams.set('status', status)
    else
        url.searchParams.delete('status')

    let minDate = $('#min-date').val()
    if (minDate != '')
        url.searchParams.set('min_date', minDate)
    else
        url.searchParams.delete('min_date')

    let maxDate = $('#max-date').val()
    if (maxDate != '')
        url.searchParams.set('max_date', maxDate)
    else
        url.searchParams.delete('max_date')

    window.location = url
})

$(() => {
    //  Загрузка фильтров при загрузке страницы
    let status = url.searchParams.get('status')
    if (status != null)
        $('#offer-status').val(status)

    let minDate = url.searchParams.get('min_date')
    if (minDate != null)
        $('#min-date').val(minDate)

    let maxDate = url.searchParams.get('max_date')
    if (maxDate != null)
        $('#max-date').val(maxDate)
})