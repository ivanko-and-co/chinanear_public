var socket = io();

socket.on('connect', function(data) {
    console.log('Connected')
    // Загрузка списка диалогов
    createDialogues(data);
    registerDialoguesEvents();
});


socket.on('disconnect', function() {
    console.log('Disconnected')
});


// Загрузка сообщений в диалоге при клике на него
function loadDialogue(dialogueId) {
    socket.emit('load_dialogue', dialogueId)
}
socket.on('load_dialogue', function(data) {
    // Очистка текущих сообщений, загрузка новых
    createMessages(data.id, data.messages)
    if (data.adminInvited) {
        $('.chat-admin-add').addClass('disabled')
    }
    else {
        $('.chat-admin-add').removeClass('disabled')
    }
})


// Отправка нового сообщения
function sendMessage(dialogueId, text) {
    socket.emit('send_message', {id: dialogueId, message: text})
}


// Получение нового сообщения (Так же срабатывает для прогрузки сообщения отправленного самим пользоваетелм)
socket.on('message_received', function(data) {
    receiveMessage(data.id, data.message)
})

window.onbeforeunload = function () {
    socket.disconnect()
}


function inviteAdmin(dialogueId) {
    socket.emit('invite_admin', dialogueId)
}