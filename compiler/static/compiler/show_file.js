// const content = document.querySelector("#code");
const files = document.getElementsByClassName("file");
const fileInput = document.getElementById("file_id");
const textarea = document.getElementById("code")
for (let i = 0; i < files.length; ++i) {
    files[i].addEventListener("click", function() {
        // content.textContent = this.getAttribute("data-file");
        textarea.value = this.getAttribute("data-file")
        fileInput.value = this.getAttribute("file-id");
    });
}

var standard = document.querySelectorAll('#t1 input[type="radio"]');
standard.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#standard').value = this.value;
    });
});

var optimization = document.querySelectorAll('#t2 input[type="checkbox"]');
optimization.forEach(function (checkbox) {
    checkbox.addEventListener('click', function () {
        document.querySelector('#optimizations').value += this.value + " ";
    });
});

var processor = document.querySelectorAll('#t3 input[type="radio"]');
processor.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#processor').value = this.value;
    });
});

var MCSoption = document.querySelectorAll('#t41 input[type="radio"]');
MCSoption.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#MCSoption').value = this.value;
    });
});

var STM8option = document.querySelectorAll('#t42 input[type="radio"]');
STM8option.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#STM8option').value = this.value;
    });
});

var Z80option = document.querySelectorAll('#t43 input[type="radio"]');
Z80option.forEach(function (radio) {
    radio.addEventListener('click', function () {
        document.querySelector('#Z80option').value = this.value;
    });
});

// var fileContent = document.getElementById("download_asm")
// var fileName = 'compiled.asm';
// const blob = new Blob([fileContent], { type: 'text/plain' });
// const a = document.createElement('a');
// a.setAttribute('download', fileName);
// a.setAttribute('href', window.URL.createObjectURL(blob));
// a.click();
