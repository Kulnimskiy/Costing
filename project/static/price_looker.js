$(document).ready(function () {
  $("#form-peek").on("submit", function (event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    // Получаем данные из полей формы
    var formData = $(this).serialize();
    console.log("in");
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