document.getElementById("login").addEventListener("input", checkLogin);
document.getElementById("company_inn").addEventListener("change", checkInn);

function checkLogin() {
    let cur_login = document.getElementById("login").value;
    cur_login = cur_login.replace(/\s/g, "");
    let login_status = document.getElementById("login_status");
    if (!cur_login.localeCompare("")) {
        login_status.innerText = "";
        return;
    }
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            let result = Number(xhttp.response);
            if (result == 1) {
                login_status.innerText = `Login ${cur_login} is not desirable`
            } else if (result == 2) {
                login_status.innerText = `Login ${cur_login} already exists`
            } else {
                login_status.innerText = `Login ${cur_login} is terrific`
            }
        }
    }
    xhttp.open("Get", "/checklogin/" + cur_login, true);
    xhttp.send();
}

function checkInn() {
    let cur_inn = document.getElementById("company_inn").value;
    cur_inn = cur_inn.replace(/\s/g, "");
    let inn_status = document.getElementById("company_inn_status");
    if (!cur_inn.localeCompare("")) {
        inn_status.innerText = "";
        return;
    }
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            let result = Number(xhttp.response);
            if (result == 1) {
                inn_status.innerText = `INN ${cur_inn} is not desirable`
            } else if (result == 2) {
                inn_status.innerText = `INN ${cur_inn} already exists`
            } else {
                inn_status.innerText = `INN ${cur_inn} is terrific`
            }
        }
    }
    xhttp.open("Get", "/checkinn/" + cur_inn, true);
    xhttp.send();
}

// the 2 functions look simular but the might be a need to reconfigure them differently in the future