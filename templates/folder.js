const toggler = document.getElementsByClassName('folder');

for (let i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener('click', function () {
        const cl = this.getElementsByClassName('bi')[0].classList;
        cl.toggle('bi-folder-fill');
        cl.toggle('bi-folder');
        this.parentElement.querySelector('.nested_in_folder').classList.toggle('active_folder');
    });
}