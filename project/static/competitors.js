function filterFunction() {
        // Объявить переменные
        let input, filter, table, tr, td, i, txtValue;
        input = document.getElementById("filterInput");
        filter = input.value.toUpperCase();
        table = document.getElementById("competitorsTable");
        tr = table.getElementsByTagName("tr");

        // Перебирайте все строки таблицы и скрывайте тех, кто не соответствует поисковому запросу
        // Поиск по столбцу с индексом ("td")[1]
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[1];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }


//Вообще не обязательно. Не нравится, перезапиши конкурента. Пока и без этого можно обойтись

//document.getElementsByName("interact_btn").addEventListener("click", changeWebsite);
//
//function changeWebsite() {
//    let website_div = document.getElementById("website")
//    let old_html = website_div.innerHTML;
//    let old_website = website_div.innerText;
//    let inn = old_html.getElementById("inn").value;
//    console.log("old: " + inn);
//    website_div.innerHTML = `<form action="/profile/change_web" method="get">
//                                <input id='new_website' value='${old_website}'>
//                                <input name="inn" value="{{competitor.competitor_inn}}" hidden="hidden">
//                            </form>`;
//    document.getElementById("new_website").addEventListener("keypress", function (e) {
//        if (e.key === 'Enter') {
//            let new_website = document.getElementById('new_website').value;
//            console.log("new: " + new_website);
//
////             here u get the response from the server
//
//             $.ajax({
//                 url: "/profile/change_web", // Здесь указываем URL-адрес серверного обработчика
//                 type: "get",
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
//}