
/**
 * Switches the view from utensils to appliances.
 * Hides the "Next" button and shows "Back" and "Save" buttons.
 */
function showAppliances() {
    document.getElementById("utensils").style.display = "none";
    document.getElementById("appliances").style.display = "block";
    document.getElementById("nextButton").style.display = "none";
    document.getElementById("backButton").style.display = "inline";
    document.getElementById("saveButton").style.display = "inline";
}

/**
 * Switches the view from appliances back to utensils.
 * Hides the "Back" and "Save" buttons and shows "Next".
 */
function showUtensils() {
    document.getElementById("appliances").style.display = "none";
    document.getElementById("utensils").style.display = "block";
    document.getElementById("nextButton").style.display = "inline";
    document.getElementById("backButton").style.display = "none";
    document.getElementById("saveButton").style.display = "none";
}

/**
 * Handles submission of the utensils/appliances selection form.
 * Sends selected tools to the server and redirects to dashboard on success.
 */
document.getElementById("tool-form").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const response = await fetch("/tools/save", {
        method: "POST",
        body: formData
    });

    const result = await response.json();
    
    if (result.success) {
        showToast(result.message, true);
        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 2000); // delay before redirect
    } else {
        showToast(result.message, false);
    }
});

/**
 * Displays a temporary toast message to indicate success or failure.
 * 
 * @param {string} message - The message to display.
 * @param {boolean} isSuccess - Whether the toast indicates success (true) or error (false).
 */
function showToast(message, isSuccess = true) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.backgroundColor = isSuccess ? "#4caf50" : "#f44336";
    toast.className = "toast show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}
