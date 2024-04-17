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

function changeColor() {
    let operations = document.getElementsByClassName("price_change")
    for (let operation of operations) {
        let last_operation_price = operation.parentElement.getElementsByClassName("last_price")[0]

        let operation_value = operation.innerText.toString().toLowerCase()
        if (operation_value.includes("-")) {
            last_operation_price.style.color = "red";
            last_operation_price.style.fontWeight = "700";
            operation.style.color = "red";
            operation.style.fontWeight = "700";
        } else if (operation_value.localeCompare("0.0")) {
            last_operation_price.style.color = "green";
            last_operation_price.style.fontWeight = "700";
            operation.style.color = "green";
            operation.style.fontWeight = "700";
        }
    }
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
    }
}

changeColor()
formatPrice()

function filterFunction() {
    // Объявить переменные
    let input, filter, table, tr, td, i, txtValue, by_color1, by_color2, td_price, one_color, two_color;
    input = document.getElementById("filterInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("goodsTable");
    tr = table.getElementsByTagName("tr");
    by_color1 = document.getElementById("inlineCheckbox1").checked;
    by_color2 = document.getElementById("inlineCheckbox2").checked;
    one_color = document.getElementById("inlineCheckbox1Color").innerText.toLowerCase();
    two_color = document.getElementById("inlineCheckbox2Color").innerText.toLowerCase();
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1];
        let color_filter1 = false;
        let color_filter2 = false;
        td_price = tr[i].getElementsByTagName("td")[5];
        if (td) {
            if (by_color1 && !td_price.style.color.localeCompare(one_color)) {
                color_filter1 = true;
            }
            if (by_color2 && !td_price.style.color.localeCompare(two_color)) {
                color_filter1 = true;
            }
            // if none of the color filters has been checked
            if (!by_color2 && !by_color1){
                color_filter1 = true;
                color_filter2 = true;
            }
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                if (color_filter1 || color_filter2) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function filterByColor(color, id) {
    if (document.getElementById('inlineCheckbox1').checked) {
        $('#inlineCheckbox2').attr('disabled', true);
    }
    if (document.getElementById('inlineCheckbox2').checked) {
        $('#inlineCheckbox1').attr('disabled', true);
    }
    let by_color1 = document.getElementById(id).checked;
    let table, tr, td, i;
    table = document.getElementById("goodsTable");
    tr = table.getElementsByTagName("tr");
    if (by_color1) {
        // Перебирайте все строки таблицы и скрывайте тех, кто не соответствует поисковому запросу
        // Поиск по столбцу с индексом ("td")[1]
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[5];
            if (td) {
                if (td.style.color.localeCompare(color) == 0 && tr[i].style.display.localeCompare("") == 0) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    } else {
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[5];
            if (td) {
                tr[i].style.display = "";
            }
        }
        $('#inlineCheckbox2').attr('disabled', false);
        $('#inlineCheckbox1').attr('disabled', false);
        filterFunction();
    }
}