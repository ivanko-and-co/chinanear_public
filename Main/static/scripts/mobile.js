const mobileMenu = document.querySelector(".mobile-user");
const mobileClose = document.querySelector(".mobile-user__close");


function openUserMenu(){
  mobileMenu.classList.add("mobile-opened");
  if (typeof hideAllPopups !== 'undefined')
    hideAllPopups()
}

function closeUserMenu(){
  mobileMenu.classList.remove("mobile-opened");
}


$('.mobile-user__inputs select').change(function() {
  let selected = $(this).find('option:selected')
  let url = selected.data('url')
  if (url)
    location.href = url
})