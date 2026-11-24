
//  Mobile Menu
const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector(".main-nav");

if (menu && nav) {
    menu.addEventListener("click", function () {
        nav.classList.toggle("open");

        menu.textContent = nav.classList.contains("open") ? "×" : "☰";
    });

    nav.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", function () {
            nav.classList.remove("open");
            menu.textContent = "☰";
        });
    });
}

const year = document.getElementById("year");
if (year) {
    year.textContent = new Date().getFullYear();
}
