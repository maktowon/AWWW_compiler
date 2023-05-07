const toggler = document.getElementsByClassName('folder');

for (let i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener('click', function () {
        this.parentElement.querySelector('.nested_in_folder').classList.toggle('active_folder');
    });
}