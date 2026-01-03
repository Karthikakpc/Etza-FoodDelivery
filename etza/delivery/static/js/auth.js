document.addEventListener("DOMContentLoaded", function () {

    const signInPanel = document.querySelector(".sign-in");
    const signUpPanel = document.querySelector(".sign-up");

    const navSignIn = document.getElementById("navSignIn");
    const navSignUp = document.getElementById("navSignUp");

    const switchToSignUp = document.getElementById("switchToSignUp");
    const switchToSignIn = document.getElementById("switchToSignIn");

    /* SAFETY CHECK */
    if (!signInPanel || !signUpPanel) return;

    /* ------------------------------
       FUNCTIONS
    ------------------------------ */

    function showSignIn() {
        signInPanel.classList.add("active");
        signUpPanel.classList.remove("active");

        navSignIn.classList.add("active");
        navSignUp.classList.remove("active");
    }

    function showSignUp() {
        signUpPanel.classList.add("active");
        signInPanel.classList.remove("active");

        navSignUp.classList.add("active");
        navSignIn.classList.remove("active");
    }

    /* ------------------------------
       TOGGLE BUTTONS
    ------------------------------ */

    navSignIn.addEventListener("click", showSignIn);
    navSignUp.addEventListener("click", showSignUp);

    switchToSignUp.addEventListener("click", showSignUp);
    switchToSignIn.addEventListener("click", showSignIn);

    /* ------------------------------
       AUTO MODE FROM URL
    ------------------------------ */

    const params = new URLSearchParams(window.location.search);
    const mode = params.get("mode");

    if (mode === "signup") {
        showSignUp();
    } else {
        showSignIn(); // default
    }
});
