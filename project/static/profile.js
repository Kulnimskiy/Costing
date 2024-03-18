change_available = document.getElementById("interact_btn");
if (change_available) {
    change_available.addEventListener("click", changeWebsite);
}
let link_buttons = document.getElementsByName("interact_btn")
document.querySelectorAll('.item_link').forEach((el) => {
    el.addEventListener('click', changeConnection)
})
//    btn.addEventListener("click", changeConnection);
// window.addEventListener('load', loadConnections () {
//   alert("It's loaded!")
// })

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

function changeConnection(e) {
    let link_span_el = $(this)[0].parentElement.parentElement;
    let link_span_html_old = link_span_el.innerHTML;
    let el_id = link_span_el.getElementsByClassName("element_id")[0].value;
    let old_link = link_span_el.querySelector("a").getAttribute('href');
    link_span_el.innerHTML = `<input type='text' class='form-control' name='new_item_link' id='${el_id}' placeholder='link for item' value='${old_link}'>`;

    document.getElementById(el_id).addEventListener("keypress", function (e) {
        if (e.key === 'Enter') {
            let new_link = document.getElementById(el_id).value;
            connection_info = el_id.split("_");
            item_id = connection_info[0];
            comp_inn = connection_info[1];
            console.log("new: " + new_link, "item id: " + item_id, "comp_inn: " + comp_inn);

//             here u get the response from the server

            $.ajax({
                url: "/profile/link_items", // Здесь указываем URL-адрес серверного обработчика
                type: "post",
                data: {"new_link": new_link, "item_id": item_id, "comp_inn": comp_inn},
                success: function (response) {
                    // Обработка успешной отправки данных
                    link_span_el.innerHTML = link_span_html_old;
                    if (!response.toString().includes("http")) {
                        link_span_el.querySelector("a").innerText = "Error";
                        link_span_el.querySelector("a").style.color = "red";
                        console.log(response);
                        console.log("Error! link is not valid or sth went wrong or u deleted it");
                        document.querySelectorAll('.item_link').forEach((el) => {
                            el.addEventListener('click', changeConnection)
                        })
                    }
                    else {
                        link_span_el.querySelector("a").innerText = response.toString().slice(0,25) + "...";
                        link_span_el.querySelector("a").style.color = "green";
                        document.querySelectorAll('.item_link').forEach((el) => {
                            el.addEventListener('click', changeConnection)
                        })
                        console.log("there has been a responce " + response);
                    }
                },
                error: function (error) {
                    // Обработка ошибок при отправке данных
                    console.error("Ошибка при отправке данных: ", error);
                },
            });
        }
    });
}