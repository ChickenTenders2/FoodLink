/**
 * Toggles the responsive class on the top navigation bar.
 * Adds "responsive" to the class name to show the mobile menu.
 * Removes it to revert back to the default desktop view.
 */
function navbar() {
    const nav = document.getElementById("myTopnav");
    // If the current class is "topnav", add "responsive" to make it mobile-friendly
    if (nav.className === "topnav") {
      nav.className += " responsive"; // Becomes "topnav responsive"
    } else {
      // If already responsive, reset it back to "topnav"
      nav.className = "topnav";
    }
  }  