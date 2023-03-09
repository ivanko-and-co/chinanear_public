console.log(window.innerWidth);

const productsBody = document.querySelectorAll(".products-row");
const productBody = document.querySelectorAll(".product-row__item");
const productInfo = document.querySelectorAll(".product-row__info");
const infoCol = document.querySelectorAll(".info-col");
const toCol = document.querySelectorAll(".info-row__sb");
const rowDeliver = document.querySelectorAll(".info-row__deliver");
const rowText = document.querySelectorAll(".info-row__text");
const pageNav = document.querySelectorAll(".page-navigation");
const price = document.querySelectorAll(".product-row__item-price");
const bodyPrice = document.querySelectorAll(".info__price");
const logo = document.querySelectorAll(".product-row__logo");
const prodTitle = document.querySelectorAll(".info-row__title");
const bottomNavigation = document.querySelectorAll(".page-navigation");
const catalogMenu = document.querySelectorAll(".top-nav__right");



if (innerWidth < 768) {
  blockMenuSet();
}

function rowMenuSet(setCookie = true) {
  if (setCookie)
    Cookies.set('products_grid', 'V', { expires: 28, path: '/' })
  document.querySelector("#blockMenu").src = "../../../static/img/col-menu.svg";
  document.querySelector("#rowMenu").src = "../../../static/img/row-menu__active.svg";

  rowDeliver.forEach((x21) =>
    x21.classList.replace("disnone", "info-row__deliver")
  );
  rowText.forEach((x22) => x22.classList.replace("disnone", "info-row__text"));

  productsBody.forEach((x122) =>
    x122.classList.replace("products", "products-row")
  );
  productBody.forEach((x222) =>
    x222.classList.replace("product__item", "product-row__item")
  );
  productInfo.forEach((x322) =>
    x322.classList.replace("product__item", "product-row__info")
  );
  bodyPrice.forEach((x422) =>
    x422.classList.replace("info__price", "info-row__sb")
  );
  price.forEach((x522) =>
    x522.classList.replace("info__price", "product-row__item-price")
  );
  price.forEach((x622) => x622.classList.remove("ordmone"));
  toCol.forEach((x722) =>
    x722.classList.replace("product__info", "info-row__sb")
  );
  logo.forEach((x822) =>
    x822.classList.replace("product__logo", "product-row__logo")
  );
  prodTitle.forEach((x922) =>
    x922.classList.replace("info__text", "info-row__title")
  );
  infoCol.forEach((x1022) => (x1022.style.padding = "1rem 0 0.5rem 0"));
  bottomNavigation.forEach((x1222) => x1222.classList.remove("transpbg"));
  bodyPrice.forEach((x1422) => x1422.classList.add("info-row__sb"));
}

function blockMenuSet(setCookie = true) {
  if (setCookie)
    Cookies.set('products_grid', 'H', { expires: 28, path: '/' })
  document.querySelector("#blockMenu").src ="../../../static/img/col-menu__active.svg";
  document.querySelector("#rowMenu").src ="../../../static/img/row-menu.svg";

  rowDeliver.forEach((x) =>
    x.classList.replace("info-row__deliver", "disnone")
  );
  rowText.forEach((x) => x.classList.replace("info-row__text", "disnone"));

  productsBody.forEach((x1) =>
    x1.classList.replace("products-row", "products")
  );
  productBody.forEach((x2) =>
    x2.classList.replace("product-row__item", "product__item")
  );
  productInfo.forEach((x3) =>
    x3.classList.replace("product-row__info", "product__item")
  );
  toCol.forEach((x4) => x4.classList.replace("info-row__sb", "info__price"));
  price.forEach((x5) =>
    x5.classList.replace("product-row__item-price", "info__price")
  );
  price.forEach((x6) => x6.classList.add("ordmone"));
  toCol.forEach((x7) => x7.classList.replace("info__price", "product__info"));
  logo.forEach((x8) =>
    x8.classList.replace("product-row__logo", "product__logo")
  );
  prodTitle.forEach((x9) =>
    x9.classList.replace("info-row__title", "info__text")
  );
  infoCol.forEach((x10) => (x10.style.padding = 0));
  bottomNavigation.forEach((x12) => x12.classList.add("transpbg"));
}

function updateGridFromCookie() {
  let grid = Cookies.get('products_grid')
  if (grid && grid == 'H')
    blockMenuSet()
  else
    rowMenuSet()
}
//  Применение отображения грида при загрузке страницы
if ($(window).width() <= 766)
  blockMenuSet(false)
else
  updateGridFromCookie()

$(window).resize(function() {
  if ($(this).width() <= 766)
    blockMenuSet(false)
  else
    updateGridFromCookie()
})

//  Добавление в корзину
$(document).on('click', '.product-row__btn', function() {
  let uid = $(this).data('uid')
  if (uid)
    addToCart(uid)
})