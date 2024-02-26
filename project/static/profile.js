document.getElementById("interact_btn").addEventListener("click", changeWebsite);

function changeWebsite() {
    let website_div = document.getElementById("website")
    let old_html = website_div.innerHTML;
    let old_website = website_div.innerText;
    let inn = document.getElementById("user_inn").innerText;
    console.log("old: " + old_website);
    website_div.innerHTML = `<input id='new_website' value='${old_website}'>`;
    document.getElementById("new_website").addEventListener("keypress", function (e) {
        if (e.key === 'Enter') {
            let new_website = document.getElementById('new_website').value;
            console.log("new: " + new_website);

//             here u get the response from the server

             $.ajax({
                 url: "/profile/change_web", // Здесь указываем URL-адрес серверного обработчика
                 type: "post",
                 data: {"new_web": new_website, "inn": inn},
                 success: function (response) {
                     // Обработка успешной отправки данных
                        website_div.innerHTML = old_html;
                        website_div.querySelector("a").innerText = response;
                        document.getElementById("interact_btn").addEventListener("click", changeWebsite);
                        console.log("there has been a responce " + response);
                 },
                 error: function (error) {
                     // Обработка ошибок при отправке данных
                        console.error("Ошибка при отправке данных: ", error);
                 },
             });
        }
    });
}