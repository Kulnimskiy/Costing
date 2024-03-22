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
                console.log("there has been a responce");
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

function AddConnectionTo() {
        let item_id_el = $("#add_connection_item").children()[1];
        if (item_id_el.value) {
            console.log(item_id_el.value);
            let item_id = item_id_el.value;
            let comp_inn = $(this).siblings()[0].value;
            let new_link = $(this).siblings()[1].value;
            let data = {"item_id": item_id, "comp_inn": comp_inn, "new_link": new_link}
            $.ajax({
                url: "/profile/link_items", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: data,
                success: function (response) {
                    // Обработка успешной отправки данных
                    item_id_el.innerHTML = "Done con";
                    console.log("there has been a responce");
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    item_id_el.innerHTML = "Error connecting";
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
                    item_id_el.innerHTML = "Added";
                    console.log("there has been a responce");
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    item_id_el.innerHTML = "Error Adding";
                    $("#peek_results").html("There has been an error!")
                    console.error("Ошибка при отправке данных: ", error);
                },
            });

        }
};
//$.ajax({
//    url: "/items_owned", // Здесь указываем URL-адрес серверного обработчика
//    type: "get",
//    success: function (response) {
//        // Обработка успешной отправки данных
//        json = JSON.parse(response);
//        let vector = [];
//        $.each(json, function (index, value) {
//            let tem =
//                {
//                    id: index,
//                    text: value.name
//                };
//            vector.push(tem);
//        })
//        content = {
//            "result": vector
//        };
//        $(".prompt").select2({
//            data: content,
//            minimumInputLength: 1,
//            width: '100%',
//            placeholder: "Item name...",
//            templateResult: formatState,
//            templateSelection: formatRepoSelection
//        });
//        console.log(content)
//
//    },
//    error: function (error) {
//        // Обработка ошибок при отправке данных
//        console.error("Ошибка при отправке данных: ", error);
//    },
//});