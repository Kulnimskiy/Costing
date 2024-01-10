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
            login_status.style.color = "red"
            if (result == 1) {
                login_status.innerText = `Login ${cur_login} is not desirable`
            } else if (result == 2) {
                login_status.innerText = `Login ${cur_login} already exists`
            } else {
                login_status.innerText = `Login ${cur_login} is terrific`
                login_status.style.color = "#096"
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
            inn_status.style.color = "red"
            if (result == 1) {
                inn_status.innerText = `INN ${cur_inn} is not desirable`
            } else if (result == 2) {
                inn_status.innerText = `INN ${cur_inn} already exists`
            } else {
                inn_status.innerText = `INN ${cur_inn} is terrific`
                inn_status.style.color = "#096"
            }
        }
    }
    xhttp.open("Get", "/checkinn/" + cur_inn, true);
    xhttp.send();
}


function getPasswordStrength(password) {
    let s = 4;  // the number of requirements for the user's password
    let mistake;
    if (!/[a-z]/.test(password)) {
        s--;
        mistake = "Lower case letters"
    }
    if (password.length < 6) {
        s--;
        mistake = "6 characters minimum"
    }
    if (!/[A-Z]/.test(password)) {
        s--;
        mistake = "Upper case letters"
    }
    if (!/[0-9]/.test(password)) {
        s--;
        mistake = "Numbers"
    }
    return [s, mistake];
}

document.getElementById("password").addEventListener("focus", function(){
    document.querySelector(".pw-strength").style.display = "block";
});

document.getElementById("password").addEventListener("input", function(e){
    let password = e.target.value;
    let [strength, mistake] = getPasswordStrength(password);
    let passwordStrengthSpans = document.querySelectorAll(".pw-strength span");
    strength = Math.max(strength, 1);
    passwordStrengthSpans[1].style.width = strength * 25 + "%";
    passwordStrengthSpans[0].innerText = mistake;
    if (strength < 2) {
        passwordStrengthSpans[0].innerText = mistake;
        passwordStrengthSpans[0].style.color = "red";
        passwordStrengthSpans[1].style.color = "#111";
        passwordStrengthSpans[1].style.background = "#d13636";
    } else if (strength >= 2 && strength <=3) {
        passwordStrengthSpans[0].innerText = mistake;
        passwordStrengthSpans[0].style.color = "#111";
        passwordStrengthSpans[1].style.color = "#111";
        passwordStrengthSpans[1].style.background = "#e6da44";
    } else if (strength > 3) {
        passwordStrengthSpans[0].innerText = "Everything is fine!";
        passwordStrengthSpans[0].style.color = "#096";
        passwordStrengthSpans[1].style.color = "#fff";
        passwordStrengthSpans[1].style.background = "#20a820";
    }
});
// the 2 functions look simular but the might be a need to reconfigure them differently in the future