// HERO IMAGE SWAP
const img1 = document.getElementById("img1");
const img2 = document.getElementById("img2");
let showFirst = true;

setInterval(() => {
    img1.classList.toggle("active", showFirst);
    img2.classList.toggle("active", !showFirst);
    showFirst = !showFirst;
}, 5000);

// AUTO SCROLL RESTAURANTS
const carousel = document.getElementById("restaurantCarousel");

let scrollAmount = 0;
setInterval(() => {
    if (!carousel) return;
    scrollAmount += 1;
    carousel.scrollLeft += 1;

    if (carousel.scrollLeft + carousel.clientWidth >= carousel.scrollWidth) {
        carousel.scrollLeft = 0;
    }
}, 20);
