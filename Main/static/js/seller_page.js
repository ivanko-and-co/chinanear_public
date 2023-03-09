tinymce.init({
    selector: 'textarea.full_description',
    plugins: 'lists image link',
    menubar: false,
    toolbar: 'bold italic underline | alignleft aligncenter alignright | bullist numlist | link image | undo redo',
    image_title: true,
    automatic_uploads: true,
    file_picker_types: 'image',
    file_picker_callback: function (cb, value, meta) {
        var input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');

        input.onchange = function () {
            var file = this.files[0];

            var reader = new FileReader();
            reader.onload = function () {
                var id = 'blobid' + (new Date()).getTime();
                input.setAttribute('name', 'tinymce_img')
                var blobCache =  tinymce.activeEditor.editorUpload.blobCache;
                var base64 = reader.result.split(',')[1];
                var blobInfo = blobCache.create(id, file, base64);
                blobCache.add(blobInfo);

                cb(blobInfo.blobUri(), { title: file.name });
            };
            reader.readAsDataURL(file);
        };

        input.click();
    },
});

$(() => {
    //  Скрытие уведомления о непривязанном домене в tinymce
    let timerId = setInterval(() => {
        if ($('.tox-notifications-container').length > 0 && $('.tox-notifications-container').is(':visible')) {
            $('.tox-notifications-container').hide()
            //clearInterval(timerId)
        }
    }, 200);

    //  Клик по картинке открывает выбор файла
    $('.product_img_preview img').click(function() {
        $(this).parent().find('input')[0].click()
    })
    //  При выборе файла картинка становится превью
    $('.product_img_preview input').change(function() {
        let [file] = this.files
        if (file) {
            $(this).parent().find('img').attr('src', URL.createObjectURL(file))
        }
    })

    //  Добавление количеств товара
    $('#add-quantity-price').click(function() {
        let html = `
            <div class="quantity_price_container_other">
                <div class="quantity_price-choosing">
                    <div class="label">
                        <label>Quantity from</label>
                    </div>
                    <input type="number" placeholder="100" name="q_from">
                </div>
                <div class="quantity_price-choosing">
                    <div class="label">
                        <label>Quantity to</label>
                    </div>
                    <input type="number" placeholder="999" name="q_to">
                </div>
                <div class="quantity_price-choosing">
                    <div class="label">
                        <label>Price</label>
                    </div>
                    <input class="price" type="number" placeholder="0.0" name="q_price">
                </div>
                <button><img src="/static/img/delete.svg"></button>
            </div>
        `
        $(html).insertBefore('.quantity_price_container > .more')
    })
    $('#add-quantity-price').click()

    //  Удаление количеств товара
    $(document).on('click', '.quantity_price_container_other button', function() {
        $(this).parent().remove()
    })

    $('form').submit(function() {
        tinymce.triggerSave();
    })
})