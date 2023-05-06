const darkmode = document.getElementById('toggle_dark_mode');
const root = document.documentElement;

darkmode.addEventListener('click', function() {
    this.classList.toggle('bi-brightness-high-fill');
    if (this.classList.toggle('bi-moon-stars-fill')) {
        root.style.setProperty('--color1', 'gray');
        root.style.setProperty('--color2', 'beige');
        root.style.setProperty('--color3', 'white');
        root.style.setProperty('--color', 'black');
        root.style.setProperty('--folder_fill', 'url(folder-fill.svg)')
        root.style.setProperty('--file_fill', 'url(file-code-fill.svg)')
    } else {
        root.style.setProperty('--color1', 'var(--color1_dm)');
        root.style.setProperty('--color2', 'var(--color2_dm)');
        root.style.setProperty('--color3', 'var(--color3_dm)');
        root.style.setProperty('--color', 'white');
        root.style.setProperty('--folder_fill', 'url(folder-fill-darkmode.svg)')
        root.style.setProperty('--file_fill', 'url(file-code-fill-darkmode.svg)')
    }
})