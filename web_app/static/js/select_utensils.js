
// hides the utensils checkboxes and shows appliances
function showAppliances() {
    document.getElementById("utensils").style.display = "none";
    document.getElementById("appliances").style.display = "block";
    document.getElementById("nextButton").style.display = "none";
    document.getElementById("backButton").style.display = "inline";
    document.getElementById("saveButton").style.display = "inline";
}
// hides the appliances checkboxes and shows utensils
function showUtensils() {
    document.getElementById("appliances").style.display = "none";
    document.getElementById("utensils").style.display = "block";
    document.getElementById("nextButton").style.display = "inline";
    document.getElementById("backButton").style.display = "none";
    document.getElementById("saveButton").style.display = "none";
}
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

function showToast(message, isSuccess = true) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.backgroundColor = isSuccess ? "#4caf50" : "#f44336";
    toast.className = "toast show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}
