document.addEventListener("DOMContentLoaded", function () {

    const signInPanel = document.querySelector(".sign-in");
    const signUpPanel = document.querySelector(".sign-up");

    const navSignIn = document.getElementById("navSignIn");
    const navSignUp = document.getElementById("navSignUp");

    const switchToSignUp = document.getElementById("switchToSignUp");
    const switchToSignIn = document.getElementById("switchToSignIn");

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
       USER ACTIONS ONLY
       (NO AUTO SWITCH ON LOAD)
    ------------------------------ */

    navSignIn.addEventListener("click", showSignIn);
    navSignUp.addEventListener("click", showSignUp);

    switchToSignUp.addEventListener("click", showSignUp);
    switchToSignIn.addEventListener("click", showSignIn);

    // ❌ REMOVED AUTO MODE LOGIC
    // Django template controls initial state using `mode`
});
