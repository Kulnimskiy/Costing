let website_btn = document.getElementById("interact_btn")
if (website_btn) {
    document.getElementById("interact_btn").addEventListener("click", changeWebsite);
}


function changeWebsite() {
    let website_div = document.getElementById("website")
    let old_html = website_div.innerHTML;
    let old_website = website_div.innerText;
    console.log("old: " + old_website);
    website_div.innerHTML = `<input id='new_website' value='${old_website}'>`;
    document.getElementById("new_website").addEventListener("keypress", function (e) {
        if (e.key === 'Enter') {
            let new_website = document.getElementById('new_website').value;
            console.log("new: " + new_website);

             // here u get the response from the server
//             $.ajax({
//                 url: $(this).attr('action'), // Здесь указываем URL-адрес серверного обработчика
//                 type: "post",
//                 data: new_website,
//                 success: function (response) {
//                     // Обработка успешной отправки данных
//                     $("#peek_results").html(response)
//                     console.log("there has been a responce");
//                 },
//                 error: function (error) {
//                     // Обработка ошибок при отправке данных
//                     $("#peek_results").html("There has been an error!")
//                     console.error("Ошибка при отправке данных: ", error);
//                 },
//             });


            website_div.innerHTML = old_html;
            website_div.querySelector("a").innerText = new_website;
            document.getElementById("interact_btn").addEventListener("click", changeWebsite);
        }
    });
}


