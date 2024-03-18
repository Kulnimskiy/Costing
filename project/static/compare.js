function formatPrice() {
    let operations = document.getElementsByClassName("price")
    for (let operation of operations) {
        let operation_value = operation.innerText.toString();
        operation_value = operation_value.slice(0, -2);
        if (!isNaN(operation_value)){
                let [_, num, suffix] = operation_value.match(/^(.*?)((?:[,.]\d+)?|)$/);
                operation.innerText = `${num.replace(/\B(?=(?:\d{3})*$)/g, ' ')}${suffix}`
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
            if (my_price >= min_price) {
                el_my_price.style.color = "red";
            } else {
                el_my_price.style.color = "green";
            }
            let cr_prices = row.getElementsByClassName("result");
            for (let price of cr_prices) {
                let float_price = price.innerText;
                if (float_price) {
                    float_price = parseFloat(float_price);
                    if (float_price < my_price) {
                        price.style.color = "red";
                    }
                }
            }
        }
    }
}

changeColor()
formatPrice()