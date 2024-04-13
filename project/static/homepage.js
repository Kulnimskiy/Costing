let website_btn = document.getElementById("change_web_btn")
if (website_btn) {
    website_btn.addEventListener("click", changeWebsite);
}

let email_btn = document.getElementById("change_email_btn")
if (email_btn) {
    email_btn.addEventListener("click", changeEmail);
}


function changeWebsite() {
    let website_div = document.getElementById("website");
    let old_html = website_div.innerHTML;
    let old_website = website_div.innerText;
    console.log("old site: " + old_website);
    let inn = document.getElementById("company_inn").innerText;
    website_div.innerHTML = `<input id='new_website' value='${old_website}'>`;
    document.getElementById("new_website").addEventListener("keypress", function (e) {
        if (e.key === 'Enter') {
            let new_website = document.getElementById('new_website').value;
            console.log("new: " + new_website);

            $.ajax({
                url: "/profile/change_web", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: {"new_web": new_website, "inn": inn},
                success: function (response) {
                    // Обработка успешной отправки данных
                    website_div.innerHTML = old_html;
                    website_div.querySelector("a").innerText = response;
                    website_div.querySelector("a").setAttribute("href", response)
                    document.getElementById("change_web_btn").addEventListener("click", changeWebsite);
                    console.log("there has been a responce " + response);
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    console.error("Ошибка при отправке данных: ", error);
                    website_div.innerHTML = old_html;
                    website_div.querySelector("a").innerText = "Error sending";
                    document.getElementById("change_web_btn").addEventListener("click", changeWebsite);
                },
            });
        }
    });
}

function changeEmail() {
    let email_div = document.getElementById("email");
    let old_html = email_div.innerHTML;
    let old_email = email_div.innerText;
    console.log("old email: " + old_email);
    email_div.innerHTML = `<input id='new_email' value='${old_email}'>`;
    document.getElementById("new_email").addEventListener("keypress", function (e) {
        if (e.key === 'Enter') {
            let new_email = document.getElementById('new_email').value;
            console.log("new: " + new_email);

            // here u get the response from the server
            $.ajax({
                url: "/profile/change_email", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: {"new_email": new_email},
                success: function (response) {
                    // Обработка успешной отправки данных
                    email_div.innerHTML = old_html;
                    email_div.querySelector("span").innerText = response;
                    document.getElementById("change_email_btn").addEventListener("click", changeEmail);
                    console.log("there has been a responce " + response);
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    console.error("Ошибка при отправке данных: ", error);
                    email_div.innerHTML = old_html;
                    email_div.querySelector("span").innerText = "Error sending";
                    document.getElementById("change_email_btn").addEventListener("click", changeEmail);
                },
            });
        }
    });
}
