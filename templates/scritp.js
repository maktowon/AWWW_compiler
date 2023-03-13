const toggle = document.getElementById('toggle_mode')
const body = document.querySelector('body');
const root = document.documentElement;
const nav = document.querySelector('nav')

toggle.addEventListener('click', function(){
    this.classList.toggle('bi-moon');
    if(this.classList.toggle('bi-brightness-high-fill')) {
        root.style.setProperty('--bg', 'white');
        root.style.setProperty('--color', 'black');
        body.style.transition = '2s';
        nav.style.transition = '2s';
    } else {
        root.style.setProperty('--bg', 'black');
        root.style.setProperty('--color', 'white');
        body.style.transition = '2s';
        nav.style.transition = '2s';
    }
})