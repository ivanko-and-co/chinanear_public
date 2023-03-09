$(function () {
  //  Загрузка списка диалогов
  getDialogues();
});

function getDialogues() {
  //  Получение списка диалогов с сервера
  $.ajax({
    url: "/get_dialogues",
    method: "post",
    dataType: "json",
    success: function (data) {
      let pList = $("#peoples-list");
      pList.empty();
      //  Заполняем список диалогов
      data.forEach(function (dialogue, key) {
        let borderNone = "border-none";
        if (data.length !== key + 1) borderNone = "";

        pList.append(`
                    <div class="person ${borderNone}" data-id="${dialogue[0]}">
                        <div class="user-info">
                            <div class="f-head">
                                <img src="static/img/90x90.jpg" class="avatar-user" alt="avatar">
                            </div>
                            <div class="f-body">
                                <div class="meta-info">
                                    <span class="user-name" data-name="${dialogue[1]}">${dialogue[1]}</span>
                                </div>
                                <span class="preview">${dialogue[2]}</span>
                            </div>
                        </div>
                    </div>
                `);
      });

      //  Привязка к новым диалогам ивентов
      $(".user-list-box .person").on("click", function (event) {
        if ($(this).hasClass(".active")) {
          return false;
        } else {
          var findChat = $(this).attr("data-chat");
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
          $(".user-list-box .person").removeClass("active");
          $(".chat-box .chat-box-inner").css("height", "100%");
          $(".chat-box .overlay-phone-call").css("display", "block");
          $(".chat-box .overlay-video-call").css("display", "block");
          $(this).addClass("active");
        }
        if ($(this).parents(".user-list-box").hasClass("user-list-box-show")) {
          $(this).parents(".user-list-box").removeClass("user-list-box-show");
        }
        $(".chat-meta-user").addClass("chat-active");
        $(".chat-box").css("height", "calc(100vh - 250px)");
        $(".chat-footer").addClass("chat-active");

        const ps = new PerfectScrollbar(".chat-conversation-box", {
          suppressScrollX: true,
        });

        const getScrollContainer = document.querySelector(".chat-conversation-box");
        getScrollContainer.scrollTop = 0;
      });
    },
  });
}

function getMessages(dialogue_id) {
  //  Получение списка сообщений для указанного диалога
  $.ajax({
    url: "/get_messages/" + dialogue_id,
    method: "post",
    dataType: "json",
    success: function (data) {
      let pList = $("#peoples-list");
      pList.empty();
      //  Заполняем список диалогов
      data.forEach(function (dialogue, key) {
        let borderNone = "border-none";
        if (data.length !== key + 1) borderNone = "";

        pList.append(`
                    <div class="person ${borderNone}" data-id="${dialogue[0]}">
                        <div class="user-info">
                            <div class="f-head">
                                <img src="static/img/90x90.jpg" class="avatar-user" alt="avatar">
                            </div>
                            <div class="f-body">
                                <div class="meta-info">
                                    <span class="user-name" data-name="${dialogue[1]}">${dialogue[1]}</span>
                                </div>
                                <span class="preview">${dialogue[2]}</span>
                            </div>
                        </div>
                    </div>
                `);
      });
    },
  });
}
