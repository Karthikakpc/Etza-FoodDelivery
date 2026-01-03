document.addEventListener("DOMContentLoaded", () => {
    const img1 = document.getElementById("img1");
    const img2 = document.getElementById("img2");

    let showFirst = true;

    setInterval(() => {
        if (showFirst) {
            img1.classList.remove("active");
            img2.classList.add("active");
        } else {
            img2.classList.remove("active");
            img1.classList.add("active");
        }
        showFirst = !showFirst;
    }, 5000); // every 5 seconds
});
