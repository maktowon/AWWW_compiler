const toggle = document.getElementById('toggle_mode')
const root = document.documentElement;

toggle.addEventListener('click', function() {
    this.classList.toggle('bi-brightness-high-fill');
    if(this.classList.toggle('bi-moon-stars-fill')) {
        root.style.setProperty('--bg', 'beige');
        root.style.setProperty('--color', 'black');
        root.style.setProperty('--hover_text', 'slateblue');
    } else {
        root.style.setProperty('--bg', 'black');
        root.style.setProperty('--color', 'white');
        root.style.setProperty('--hover_text', 'slategray');
    }
})