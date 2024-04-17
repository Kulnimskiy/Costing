let website_btn = document.getElementById("refresh_all")
if (website_btn) {
    website_btn.addEventListener("click", showLoader);
}

function showLoader() {
    let image_html = "<img class='text-center' style='width: 50px; display: block; margin-left: auto; margin-right: auto;' src='/static/images/loading.gif'>"
    $("#loading_icon").html(image_html);
    website_btn.innerHTML = "Please wait..."
    console.log("in")
}

function formatPrice() {
    let operations = document.getElementsByClassName("price")
    for (let operation of operations) {
        let operation_value = operation.innerText.toString();
        operation_value = operation_value.slice(0, -2);

        if (!isNaN(operation_value)) {
            let [_, num, suffix] = operation_value.match(/^(.*?)((?:[,.]\d+)?|)$/);
            operation.innerText = `${num.replace(/\B(?=(?:\d{3})*$)/g, ' ')}${suffix}`
        }
        if (!operation_value.localeCompare("0")) {
            operation.innerHTML = "No price";
            console.log(operation.innerHTML)
        }
    }
}


function changeColor() {
    let rows = document.getElementsByTagName("table")[0].rows;
    for (let row of rows) {
        let el_my_price = row.getElementsByClassName("my_price")[0];
        let el_min_price = row.getElementsByClassName("min_price")[0];
        if (el_my_price || el_min_price) {
            let my_price = parseFloat(el_my_price.innerText);
            let min_price = parseFloat(el_min_price.innerText);
            if (my_price >= min_price && min_price > 0) {
                el_my_price.style.color = "red";
                el_my_price.style.fontWeight = 600;
            } else {
                el_my_price.style.color = "green";
                el_my_price.style.fontWeight = 600;
            }
            let cr_prices = row.getElementsByClassName("result");
            for (let price of cr_prices) {
                let float_price = price.innerText;
                if (float_price) {
                    float_price = parseFloat(float_price);
                    if (float_price < my_price && float_price > 0) {
                        price.style.color = "red";
                        price.style.fontWeight = 600;
                    }
                }
            }
        }
    }
}

function filterByColor(color) {
    let btn_checked = document.getElementById("flexCheckDefault")
    let table, tr, td, i, txtValue;
    table = document.getElementById("compTable");
    tr = table.getElementsByTagName("tr");
    if (btn_checked.checked) {
        // Перебирайте все строки таблицы и скрывайте тех, кто не соответствует поисковому запросу
        // Поиск по столбцу с индексом ("td")[1]
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[2];
            if (td) {
                console.log(tr[i].style.display)
                if (td.style.color.localeCompare(color) == 0 && tr[i].style.display.localeCompare("") == 0) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    } else {
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[2];
            if (td) {
                tr[i].style.display = "";
            }
        }
        filterFunction();
    }
}

function filterFunction() {
    // Объявить переменные
    let input, filter, table, tr, td, i, txtValue, by_color, td_price, the_color;
    input = document.getElementById("filterInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("compTable");
    tr = table.getElementsByTagName("tr");
    by_color = document.getElementById("flexCheckDefault").checked;
    the_color = document.getElementById("flexCheckDefaultColor").innerText.toLowerCase();
    console.log(the_color)
    // Перебирайте все строки таблицы и скрывайте тех, кто не соответствует поисковому запросу
    // Поиск по столбцу с индексом ("td")[1]
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1];
        let color_filter = true;
        td_price = tr[i].getElementsByTagName("td")[2];
        if (td) {
            if (by_color && !td_price.style.color.localeCompare(the_color) == 0) {
                console.log("in")
                color_filter = false;
            }
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1 && color_filter) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

changeColor()
formatPrice()