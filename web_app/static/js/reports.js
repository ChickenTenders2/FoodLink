/**
 * Fetches all item reports from the server and populates the table.
 * Stores them in a global `window.reports` variable.
 */
async function get_reports() {

    // Sends update command and waits for response
    const response = await fetch('/items/reports/get');

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        window.reports = result.reports;
        fill_table(result.reports);
    } else {
        alert('There was an fetching the reports. Error: ' + result.error);
    }
}

/**
 * Filters and sorts the report list based on user selection.
 * Updates the report table display.
 */
function sort_filter_reports() {
    let reports = [];
    const checked = document.getElementById("show_null_assign").checked;
    const sort_by = document.getElementById("sort_by").value;
    // Copies reports array
    for (let report of window.reports) {
        //If showing not assinged reports is unchecked, skip null values
        if (checked || report[4] != null) {
            reports.push(report);
        }
    }

    // Sorts by error type with missing appearing first
    if (sort_by == "error_type") {
        reports.sort((a, b) => {
            // If report error_type is missing assign value 0
            error_value = (report) => report[2] == "missing" ? 0:1;
            return error_value(a) - error_value(b);
        });
    } else if (sort_by == "date_asc") {
        reports.sort((a, b) => {
            date_value = (report) => new Date(report[3]);
            return date_value(a) - date_value(b);
        });
    } else if (sort_by == "date_desc") {
        reports.sort((a, b) => {
            date_value = (report) => new Date(report[3]);
            return date_value(b) - date_value(a);
        });
    }
    fill_table(reports);
}

/**
 * Populates the HTML table with the given reports.
 * 
 * @param {Array} reports - List of report arrays to display.
 */
function fill_table(reports) {
    const table_body = document.getElementById("table_body");
    table_body.innerHTML = "";
    // Loop through each report and create a row
    for (let report of reports) {
        const [new_item_id, item_id, error_type, date_created, username, new_item_name] = report;
        // Create a new table row with report details
        const row = document.createElement("tr");
        row.innerHTML = `<td>${new_item_id}</td>
                        <td>${new_item_name}</td>
                        <td>${error_type}</td>
                        <td>${date_created}</td>
                        <td>${username}</td>`;
        // Clicking the row redirects to the individual report page
        row.onclick = () => window.location.href = "/items/reports/" + new_item_id + "/" + item_id;

        // Create a cell for the "Assign to Me" button
        const assignCell = document.createElement("td");
        const assignBtn = document.createElement("button");
        assignBtn.innerText = "Assign to Me";
        // Clicking the button assigns the report to the current user
        assignBtn.onclick = async (event) => assign_report(event, new_item_id);
        
        assignBtn.style.fontSize = "12px";
        assignBtn.style.marginTop = "0px"; 
        
        assignCell.appendChild(assignBtn);
        row.appendChild(assignCell);

        table_body.appendChild(row);
    }
}

/**
 * Assigns a report to the currently logged-in admin.
 * Prompts for confirmation and handles reassignment if already assigned.
 * 
 * @param {MouseEvent} event - Click event (used to stop row navigation).
 * @param {string} new_item_id - The ID of the item being reported.
 */
async function assign_report(event, new_item_id) {
    event.stopPropagation();
    const confirmAssign = confirm(`Assign report?`);
    if (!confirmAssign) return;
    // Check if the report is already assigned to someone
    const response = await fetch("/items/reports/check_assigned/"+ new_item_id);
    const result = await response.json();
    if (!result.success) {
        alert(result.error); // Show error if check failed
    }
    // If already assigned to another admin, ask if user wants to reassign
    if (result.admin_id) {
        const confirmReplace = confirm(`This report is already assigned to an admin. Reassign it to yourself?`);
        if (!confirmReplace) return;
    }
    // Proceed with assigning the report to the current admin
    const response2 = await fetch("/items/reports/assign/"+ new_item_id);
    const result2 = await response2.json();
    if (result2.success) {
        alert("Successfully assigned report!");
        get_reports(); // Refresh the table with updated assignments
    } else {
        alert(result2.error); // Show error if assignment fails
    }
}


/**
 * Automatically fetches and displays reports when the page is loaded.
 */
window.onload = function(){
    get_reports();
}