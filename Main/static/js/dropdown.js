//  Скрытие всех развёрнутых dropdown меню
function hideAllDropdowns() {
  $('.dropdown > .dropdown-content').each(function() {
    $(this).hide()
  })
}

$(() => {
  //  Развёртывание dropdown меню
  $('.dropdown > button').click(function() {
    event.preventDefault()
    
    let content = $(this).parent().find('.dropdown-content')
    
    if (content.length != 0) {
      let isHiddenBefore = content.is(':hidden')
      hideAllDropdowns()

      if (isHiddenBefore)
        content.show()
    }
    else
      hideAllDropdowns()
  })

  //  Клик за пределами открытого dropdown меню скрывает его
  $(window).click(function(e) {
    if ($(e.target).closest('.dropdown').length == 0)
      hideAllDropdowns()
  })
})
