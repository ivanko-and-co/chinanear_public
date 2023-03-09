$(".search > input").on("keyup", function () {
  var rex = new RegExp($(this).val(), "i");
  $(".people .person").hide();
  $(".people .person")
    .filter(function () {
      return rex.test($(this).text());
    })
    .show();
});

function registerDialoguesEvents() {
  $(".user-list-box .person").on("click", function (event) {
    if ($(this).hasClass(".active")) {
      return false;
    } else {
      var findChat = $(this).attr("data-chat");
      loadDialogue(findChat);
      var personName = $(this).find(".user-name").text();
      var personImage = $(this).find("img").attr("src");
      var hideTheNonSelectedContent = $(this)
        .parents(".chat-system")
        .find(".chat-box .chat-not-selected")
        .hide();
      var showChatInnerContent = $(this)
        .parents(".chat-system")
        .find(".chat-box .chat-box-inner")
        .show();

      if (window.innerWidth <= 767) {
        $(".chat-box .current-chat-user-name .name").html(personName.split(" ")[0]);
      } else if (window.innerWidth > 767) {
        $(".chat-box .current-chat-user-name .name").html(personName);
      }
      $(".chat-box .current-chat-user-name img").attr("src", personImage);
      $(".chat").removeClass("active-chat");
      $(".user-list-box .person").removeClass("active");
      $(".chat-box .chat-box-inner").css("height", "100%");
      $(".chat-box .overlay-phone-call").css("display", "block");
      $(".chat-box .overlay-video-call").css("display", "block");
      $(this).addClass("active");
      $(".chat[data-chat = " + findChat + "]").addClass("active-chat");
    }
    if ($(this).parents(".user-list-box").hasClass("user-list-box-show")) {
      $(this).parents(".user-list-box").removeClass("user-list-box-show");
    }
    $(".chat-meta-user").addClass("chat-active");
    $(".chat-box").css("height", "calc(100vh - 250px)");
    $(".chat-footer").addClass("chat-active");

    if ($('.current-chat-user-name .name').text() == 'Admin')
      $('.chat-admin-add').hide()
    else
      $('.chat-admin-add').show()

    const ps = new PerfectScrollbar(".chat-conversation-box", {
      suppressScrollX: true,
    });

    const getScrollContainer = document.querySelector(".chat-conversation-box");
    getScrollContainer.scrollTop = getScrollContainer.scrollHeight;
  });
}

const avatarColors = ['f9dcdc', 'dcf9dd', 'f9dcf3', 'dcf2f9', 'dfdcf9', 'f8f9dc']
function getAvatarColor(name) {
  let pointer = 0
  let strLen = name.length
  let color = avatarColors[0]
  while (strLen > 0) {
    strLen -= 1
    pointer += 1
    if (avatarColors[pointer])
      color = avatarColors[pointer]
    else
      pointer = 0
  }
  return color
}

function createDialogues(data) {
  // Список чатов
  let pList = $("#peoples-list");
  pList.empty();
  // Содержимое чатов
  let cList = $("#chat-conversation-box-scroll");
  cList.empty();

  if (!data) return;

  data.forEach(function (dialogue, key) {
    let borderNone = "border-none";
    if (data.length !== key + 1) borderNone = "";

    //  Берём первую букву из имени и фамилии для аватара
    let avatar = dialogue[1].split(' ')
    if (avatar[0] == '')
      avatar = 'A' // Аккаунт администратора
    else {
      avatar = Array.from(avatar[0])[0] + Array.from(avatar[1])[0]
      avatar = avatar.toUpperCase()
    }

    //  Цвет фона аватара
    let avatarColor = getAvatarColor(dialogue[1])
    let avatarTextColor = ''
    if (avatar == 'A') { // Аккаунт администратора
      avatarColor = '428bca' 
      avatarTextColor = 'style="color: white;"'
      dialogue[1] = 'Admin'
    }

    pList.append(`
        <div class="person ${borderNone}" data-chat="${dialogue[0]}">
            <div class="user-info">
                <div class="f-head">
                    <div class="avatar-user" style="background: #${avatarColor}">
                      <span class="user-initials" ${avatarTextColor}>${avatar}</span>
                    </div>
                </div>
                <div class="f-body">
                    <div class="meta-info">
                        <span class="user-name" data-name="${dialogue[1]}">${dialogue[1]}</span>
                    </div>
                    <span class="preview"></span>
                </div>
            </div>
        </div>
      `);

    cList.append(`<div class="chat" data-chat="${dialogue[0]}"></div>`);
  });
}

function createMessages(dialogueId, messages) {
  chat = $(`.chat[data-chat="${dialogueId}"]`);
  chat.empty();

  if (!messages) return;

  messages.forEach(function (msg) {
    msgType = msg[0];
    msgText = msg[1];
    senderNameBlock = ''
    if (msg[2])
      senderNameBlock = `<div class="sender_name">${msg[2]}</div>`

    chat.append(`
      <div class="bubble ${msgType}">
        ${senderNameBlock}
        ${msgText}
      </div>
    `);
  });
}

function receiveMessage(dialogueId, message) {
  let activeChat = $(".chat.active-chat");
  if (activeChat.length && activeChat.data("chat") == dialogueId) {
    // Добавление сообщения в окно чата
    msgType = message[0];
    msgText = message[1];
    senderNameBlock = ''
    if (message[2])
      senderNameBlock = `<div class="sender_name">${message[2]}</div>`

    activeChat.append(`
      <div class="bubble ${msgType}">
        ${senderNameBlock}
        ${msgText}
      </div>
    `);

    const getScrollContainer = document.querySelector(".chat-conversation-box");
    getScrollContainer.scrollTop = getScrollContainer.scrollHeight;
  }
  // Обновление списка диалогов
}

const ps = new PerfectScrollbar(".people", {
  suppressScrollX: true,
});

$(".mail-write-box").on("keydown", function (event) {
  if (event.key === "Enter") {
    var chatInput = $(this);
    var chatMessageValue = chatInput.val();
    if (chatMessageValue === "") {
      return;
    }

    let chatId = $(this).parents(".chat-system").find(".active-chat").data("chat");
    sendMessage(chatId, chatMessageValue);
    var clearChatInput = chatInput.val("");
  }
});

$(".hamburger, .chat-system .chat-box .chat-not-selected p").on("click", function (event) {
  $(this).parents(".chat-system").find(".user-list-box").toggleClass("user-list-box-show");
});

//  Приглашение админа в чат
$(".chat-admin-add").click(function() {
  if ($(this).is('.disabled'))
    return
  $(this).addClass('disabled')

  let chatId = $(this).parents(".chat-system").find(".active-chat").data("chat");
  inviteAdmin(chatId)
})