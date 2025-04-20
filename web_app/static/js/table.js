// Editing keeps track of if the user is modifying a row.
editing = false;

async function reset(event) {
    if (!editing) {
        event.currentTarget.style.backgroundColor = "";
    }
}

function interact(event) {
    if (!editing) {
        event.currentTarget.style.backgroundColor = "#053b0585";
    }
}

function options(event, recipe = false) {
    const collection = event.currentTarget.children;
    // Switches to editing if a row is pressed.
    if (!editing) {
        editing = true
        current = event.currentTarget
    }
    // Switches editing to false only if the current row is pressed again.
    else if (editing && (current == event.currentTarget)) {
        editing = false
    }
    if (editing && (current == event.currentTarget)) {
        // If a row is clicked on, the last two buttons (edit and delete are made visible).
        collection[collection.length - 1].style.visibility = "visible";
        collection[collection.length - 2].style.visibility = "visible";
        if (recipe) {
            collection[collection.length - 3].style.visibility = "visible";
        }
    }
    else {
         // If a row is clicked on a second time, the last two buttons (edit and 
         // delete are made hidden).
        collection[collection.length - 1].style.visibility = "hidden";
        collection[collection.length - 2].style.visibility = "hidden";
        if (recipe) {
            collection[collection.length - 3].style.visibility = "hidden";
        }
    }
}


