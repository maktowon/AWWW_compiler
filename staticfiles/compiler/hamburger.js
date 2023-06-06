const hamburger = document.querySelector(".hamburger");
const navbar = document.querySelector(".navbar ul");

hamburger.addEventListener("click", function() {
    hamburger.classList.toggle("active");
    navbar.classList.toggle("active");
})