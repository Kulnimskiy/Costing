$(document).ready(function () {
    $("#form-peek").on("submit", function (event) {
        event.preventDefault(); // Отменяем стандартное поведение формы

        // Получаем данные из полей формы
        var formData = $(this).serialize();
        $("#peek_results").html("<img class='text-center' style='width: 80px; display: block; margin-left: auto; margin-right: auto;' src='/static/images/loading.gif'>");
        // Отправляем данные на сервер с помощью AJAX
        $.ajax({
            url: $(this).attr('action'), // Здесь указываем URL-адрес серверного обработчика
            type: "post",
            data: formData,
            success: function (response) {
                // Обработка успешной отправки данных
                $("#peek_results").html(response)
                document.querySelectorAll('.btn_link_items').forEach((el) => {
                    el.addEventListener('click', AddConnectionTo)
                console.log("there has been a responce");
                })
            },
            error: function (error) {
                // Обработка ошибок при отправке данных
                $("#peek_results").html("There has been an error!")
                console.error("Ошибка при отправке данных: ", error);
            },
        });
    });
});


$(document).ready(function () {
    $('#add_connection_item').select2({
        ajax: {
            url: "/items_owned",
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data, function (item) {
                        return {id: item.item_id, text: item.name};
                    })
                };
            }
        },
        placeholder: "Item name...",
        allowClear: true,
        minimumInputLength: 0,
    });
});

function SearchUserItem(){
    let item = document.getElementById("select2-add_connection_item-container").title;
    console.log(item)
    $("#item_info").val(item);
    let formData = $("#form-peek").serialize();
    console.log(formData);
    $("#peek_results").html("<img class='text-center' style='width: 80px; display: block; margin-left: auto; margin-right: auto;' src='/static/images/loading.gif'>");
    $.ajax({
        url: $("#form-peek").attr('action'), // Здесь указываем URL-адрес серверного обработчика
        type: "post",
        data: formData,
        success: function (response) {
            // Обработка успешной отправки данных
            $("#peek_results").html(response)
            document.querySelectorAll('.btn_link_items').forEach((el) => {
                el.addEventListener('click', AddConnectionTo)
            console.log("there has been a responce");
            })
        },
        error: function (error) {
            // Обработка ошибок при отправке данных
            $("#peek_results").html("There has been an error!")
            console.error("Ошибка при отправке данных: ", error);
        },
    });
}


document.querySelectorAll('.btn_link_items').forEach((el) => {
        el.addEventListener('click', AddConnectionTo)
})

function AddConnectionTo() {
        let btn_add_con = $(this);
        let item = document.getElementById("select2-add_connection_item-container");
        let item_id_el = $("#add_connection_item").children();
            let item_id = null;
            for (let i = 0; i < item_id_el.length; i++) {
                let item_searched = item.title
                if (!item_searched.localeCompare(item_id_el[i].innerText)) {
                    item_id = item_id_el[i].value;
                    console.log(item_id);
                }
            }
        if (item_id) {
            btn_add_con.html("<img class='text-center' style='width: 10px; display: block; margin-left: auto; margin-right: auto;' src='/static/images/loading.gif'>");
            let comp_inn = $(this).siblings()[0].value;
            let new_link = $(this).siblings()[1].value;
            let data = {"item_id": item_id, "comp_inn": comp_inn, "new_link": new_link}
            $.ajax({
                url: "/profile/link_items", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: data,
                success: function (response) {
                    // Обработка успешной отправки данных
                    btn_add_con.html("<img src='/static/images/added.avif'  class='mb-1' style='width:20px; pointer-events: none;'>");
                    btn_add_con.css("background-color","black");
                    document.querySelectorAll('.btn_link_items').forEach((el) => {
                            el.addEventListener('click', AddConnectionTo)
                    })
                    console.log("there has been a responce");
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    btn_add_con.html("Error connecting");
                    btn_add_con.css("background-color","red");
                    console.error("Ошибка при отправке данных: ", error);
                },
            });

        }
        else {
            let new_link = $(this).siblings()[1].value;
            $.ajax({
                url: "/company-goods", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: {"item_link" : new_link},
                success: function (response) {
                    btn_add_con.html("<img src='/static/images/added.avif'  class='mb-1' style='width:20px; pointer-events: none;'>");
                    btn_add_con.css("background-color","black");
                    console.log("there has been a responce");
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    btn_add_con.html("Error Adding");
                    btn_add_con.css("background-color","red");
                    console.error("Ошибка при отправке данных: ", error);
                },
            });
        }
};
