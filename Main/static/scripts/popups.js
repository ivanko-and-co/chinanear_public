$(() => {
    //  Переключение видимости пароля
    $('.passvis, .passw').click(function() {
        let input = $(this).parent().find('input')
        if (input.attr('type') === 'password')
            input.attr('type', 'text')
        else
            input.attr('type', 'password')
    })

    //  Проверка пароля - Форма смены пароля
    $('#new-password, #new-password-confirm').change(function() {
        let button = $(this).closest('.popup__body').find('button')
        let warning = $(this).closest('.popup__body').find('.popup__aht')
        let requirements = $(this).closest('.popup__body').find('.popup__input-info')
        
        requirements.css('color', '')
        if ($('#new-password').val() != $('#new-password-confirm').val() || !$(this).val()) {
            //  Пароли не совпадают или поля для ввода пустые
            button.prop('disabled', true)
            if ($(this).val())
                warning.show()
            else
                warning.hide()
        }
        else {
            //  Пароли совпадают
            warning.hide()
            if (checkPassword($(this).val()))
                button.prop('disabled', false)
            else {
                requirements.css('color', 'red')
            }
        }
    })

    //  Проверка пароля - Форма регистрации
    $('#password, #password-confirm').change(function() {
        let button = $('.reg__body').find('button')
        if ($('#password').val() != $('#password-confirm').val() || !$(this).val() || !checkPassword($(this).val())) {
            //  Пароли не совпадают ИЛИ поля для для ввода пустые ИЛИ пароль не отвечает требованиям
            button.prop('disabled', true)
        }
        else
            button.prop('disabled', false)
    })
})

//  Таймер обратного отсчёта
function decreaseTimer(timer) {
    let curTime = Number(timer.text()) - 1
    timer.text(curTime)

    if (curTime <= 0) {
        timer.parent().hide()
        timer.closest('.popup__body').find('button').prop('disabled', false)
    }
    else
        setTimeout(decreaseTimer, 1000, timer)
}

function startTimer(popupTimerInfo, fromTime = 60) {
    popupTimerInfo = $(popupTimerInfo)
    popupTimerInfo.show()
    popupTimerInfo.parent().find('button').prop('disabled', true)
    let timer = popupTimerInfo.find('span')
    timer.text(fromTime)
    setTimeout(decreaseTimer, 1000, timer)
}

function checkPassword(password) {
    return /[A-Z]/.test(password)       // Имеется заглавная буква
            && /[a-z]/.test(password)   // Имеется строчная буква
            && /\d/.test(password)      // Имеется цифра
            && password.length >= 8     // От 8 символов
}



function hideAllPopups() {
    $(`.popup_wrapper`).hide()
}
//  Логика переходов popup меню
$(() => {
    //  Скрытие popup при клике за пределами
    $('.popup_wrapper, .reg-container, .popup_wrapper > .container, .popup_wrapper > .container > .row').click(function(e) {
        if ($('#popup-email-confirm-email').is(':visible'))
            location.reload()

        if ($('#popup-password-change').is(':visible'))
            return

        if ($('#popup-password-changed').is(':visible'))
            location.href = '/'

        if (e.target == this)
            hideAllPopups()
    })

    //  Клик на кнопку "Войти" в хедере
    $('#login-btn, #login-btn-mobile').click(function() {
        closeUserMenu()
        $('#popup-login').show()
    })
    //  Клик на кнопку "Войти" в popup
    $('#popup-login form').submit(function() {
        event.preventDefault()
        $.ajax({
            type: 'POST',
            url: '/auth',
            data: {
                login: $('input[name="login"]').val(),
                password: $('input[name="password"]').val()
            },
            dataType: 'json',
            encode: true
        }).done(function(data) {
            if (!data.success) {
                $('#popup-login .popup__aht').show()
            }
            else {
                location.reload()
            }
        })
    })

    //  Клик на ссылку "Забыли пароль?"
    $('#url-password-recovery').click(function() {
        hideAllPopups()
        $('#password-recovery-button').attr('disabled', null)
        $('#popup-password-recovery').show()
    })
    //  Клик на кнопку "Отправить" в форме восстановления пароля
    $('#password-recovery-button').click(function() {
        let email = $('#popup-password-recovery input').val()
        if (!email)
            return;

        let btn = $('#password-recovery-button')
        btn.attr('disabled', true)
        $.ajax({
            type: 'POST',
            url: '/recovery',
            data: {
                email: email
            },
            dataType: 'json',
            encode: true
        }).done(function() {
            btn.attr('disabled', null)

            hideAllPopups()
            $('#popup-password-recovery-email .popup__email').text(email)
            $('#popup-password-recovery-email').show()
        })
    })

    //  Клик на ссылку "Зарегистрироваться"
    $('#url-register').click(function() {
        hideAllPopups()
        $('#popup-register').show()
    })
    //  Клик на кнопку "Зарегистрироваться" в форме регистрации
    $('#popup-register form').submit(function() {
        event.preventDefault()
        let data = {}
        $('#popup-register form input').each(function() {
            let name = $(this).attr('name')
            let value = $(this).val()
            if (name)
                data[name] = value
        })
        $.ajax({
            type: 'POST',
            url: '/register',
            data: data,
            dataType: 'json',
            encode: true
        }).done(function(data) {
            if (data.success) {
                hideAllPopups()
                $('#popup-email-confirm-email').show()
                $('#popup-email-confirm-email .popup__email').text($('#popup-register input[name="email"]').val())
            }
        })
    })
    //  Клик на кнопку "Закрыть" после регистрации
    $('#popup-email-confirm-email button').click(function() {
        event.preventDefault()
        location.reload()
    })

    //  Клик на кнопку "Сохранить" при смене пароля
    $('#popup-password-change form').submit(function() {
        event.preventDefault()
        
        $('#popup-password-change button').attr('disabled', true)
        $.ajax({
            type: 'POST',
            url: '/change_password',
            data: {
                password: $('#new-password').val(),
                token: $('#token').val()
            }
        }).done((data) => {
            if (data.success == true) {
                hideAllPopups()
                $('#popup-password-changed').show()
            }
            else
                location.reload()
        }).fail(() => {
            $('#popup-password-change button').attr('disabled', null)
        })
    })
    //  Клик на кнопку "Закрыть" после смены пароля
    $('#popup-password-changed button').click(function() {
        event.preventDefault()
        location.href = '/'
    })
})