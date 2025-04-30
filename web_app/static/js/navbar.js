// Function to toggle responsive class on the navigation bar
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