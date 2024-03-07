document.getElementById("interact_btn").addEventListener("click", changeWebsite);
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
    let input_html = `<input type='text' class='form-control' name='new_item_link' id='${el_id}' placeholder='link for item'>`;
    link_span_el.innerHTML = input_html;
    let link_buttons = document.getElementById(el_id);
//    document.querySelectorAll('.item_link').forEach((el) => {
//        el.addEventListener('click', changeConnection)
//    })

    //  reset the event listener
    document.querySelectorAll('.item_link').forEach((el) => {
    el.addEventListener('click', changeConnection)
    })
//    website_div.innerHTML = `<input id='new_website' value='${old_website}'>`;
//    document.getElementById("new_website").addEventListener("keypress", function (e) {
//        if (e.key === 'Enter') {
//            let new_website = document.getElementById('new_website').value;
//            console.log("new: " + new_website);
//
////             here u get the response from the server
//
//             $.ajax({
//                 url: "/profile/change_web", // Здесь указываем URL-адрес серверного обработчика
//                 type: "post",
//                 data: {"new_web": new_website, "inn": inn},
//                 success: function (response) {
//                     // Обработка успешной отправки данных
//                        website_div.innerHTML = old_html;
//                        website_div.querySelector("a").innerText = response;
//                        document.getElementById("interact_btn").addEventListener("click", changeWebsite);
//                        console.log("there has been a responce " + response);
//                 },
//                 error: function (error) {
//                     // Обработка ошибок при отправке данных
//                        console.error("Ошибка при отправке данных: ", error);
//                 },
//             });
//        }
//    });
}