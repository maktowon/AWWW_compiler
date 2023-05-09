const content = document.querySelector(".content");
const files = document.getElementsByClassName("file");
for (let i = 0; i < files.length; ++i) {
    files[i].addEventListener("click", function() {
        content.textContent = this.getAttribute("data-file");
    });
}

var standard = document.querySelectorAll('#t1 input[type="radio"]');
standard.forEach(function (radio) {
    radio.addEventListener('click', function () {
        // Update the value of the hidden input field with the selected radio button's value
        document.querySelector('#standard').value = this.value;
    });
});

var optimization = document.querySelectorAll('#t2 input[type="checkbox"]');
optimization.forEach(function (checkbox) {
    checkbox.addEventListener('click', function () {
        // Update the value of the hidden input field with the selected radio button's value
        document.querySelector('#optimizations').value += this.value + " ";
    });
});

var processor = document.querySelectorAll('#t3 input[type="radio"]');
processor.forEach(function (radio) {
    radio.addEventListener('click', function () {
        // Update the value of the hidden input field with the selected radio button's value
        document.querySelector('#processor').value = this.value;
    });
});

var MCSoption = document.querySelectorAll('#t4 input[type="radio"]');
MCSoption.forEach(function (radio) {
    radio.addEventListener('click', function () {
        // Update the value of the hidden input field with the selected radio button's value
        document.querySelector('#MCSoption').value = this.value;
    });
});

var STM8option = document.querySelectorAll('#t4 input[type="radio"]');
STM8option.forEach(function (radio) {
    radio.addEventListener('click', function () {
        // Update the value of the hidden input field with the selected radio button's value
        document.querySelector('#STM8option').value = this.value;
    });
});

var Z80option = document.querySelectorAll('#t4 input[type="radio"]');
Z80option.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#Z80option').value = this.value;
    });
});
