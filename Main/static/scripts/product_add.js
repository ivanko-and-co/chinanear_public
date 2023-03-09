let _form = document.form1;
_form.onsubmit = function(event) {
    event.preventDefault();
    send_form();
}

async function send_form() {
    let xhr = new XMLHttpRequest();
    let form = new FormData();
    img_count = 1;
    img_count_load = 0;

    //Картинки
    form.append('preview_img', _form.querySelector("[name='preview']").files[0]);
    _form.querySelectorAll("[name^='image']").forEach((element, index) => {
        if (element.files[0]) {
            form.append('images_' + index.toString(), element.files[0])
        }
    });

    //Название товара
    let name = {};
    _form.querySelectorAll("[id^='name[']").forEach(element => name[element.dataset.name] = element.value);
    form.append('product_name', JSON.stringify(name));

    //Краткое описание
    let short = {};
    _form.querySelectorAll("[id^='short[']").forEach(element => short[element.dataset.name] = element.value);
    form.append('short_description', JSON.stringify(short));
    
    //Описание товара
    let description = {};
    let description_img = {"ru":{},"en-us":{}};
    _form.querySelectorAll("iframe").forEach(element => {
        //Получаем HTML разметку
        var localization = element.contentWindow.document.body.dataset.id.slice(6,-2)
        description[localization] = element.contentWindow.document.body.innerHTML,
        
        //Добавляем картинки из описания в форму
        element.contentWindow.document.body.querySelectorAll('img').forEach(img => {
            img_count++;
            fetch(img.src).then(s => s.blob()).then(blob => {
                const file = new File([blob], 'name', { type: blob.type });
                readFile(localization, img.src, file)
            });
        })
    });
    async function readFile(localization, name, file) {
        const fr = new FileReader();
        fr.readAsDataURL(file);
        fr.addEventListener('load', () => {
            res = fr.result;
            description_img[localization][name] = res
            img_count_load++;
            if (img_count == img_count_load) {
                send_form();
            }
        })
    };
    form.append('description', JSON.stringify(description));

    //Категория
    form.append('category', _form.querySelector('[name="category_3"]').value);

    //Единицы измерения
    form.append('units', _form.querySelector('[name="units"]').value);

    //Товаров на складе
    form.append('stock', _form.querySelector('[name="stock"]').value);

    //Диапазоны товаров
    let price = [];
    _form.querySelectorAll("[class='quantity_price_container_top']").forEach(element => price.push({
        "price": element.querySelector('[name="q_price"]').value,
        "quantity-min": element.querySelector('[name="q_from"]').value,
        "quantity-max": element.querySelector('[name="q_to"]').value
    }));
    _form.querySelectorAll("[class='quantity_price_container_other']").forEach(element => price.push({
        "price": element.querySelector('[name="q_price"]').value,
        "quantity-min": element.querySelector('[name="q_from"]').value,
        "quantity-max": element.querySelector('[name="q_to"]').value
    }));
    form.append('price', JSON.stringify(price));

    //Активность товара
    if (_form.querySelector("[name='is_active']").checked == true) {
        form.append('is_active', 1)
    } else {
        form.append('is_active', 0)
    };
    img_count_load++;
    if (img_count == img_count_load) {
        send_form();
    };
    function send_form() {
        form.append('description_img', JSON.stringify(description_img));
        xhr.open("post", "/profile/product_add_save", true);
        xhr.send(form)
    }
}