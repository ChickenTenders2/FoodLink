async function get_reports() {

    // Sends update command and waits for response
    const response = await fetch('/items/get_reports');

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        window.reports = result.reports;
        fill_table(result.reports);
    } else {
        alert('There was an fetching the reports. Error: ' + result.error);
    }
}

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
    console.log(reports);
    fill_table(reports);
}

function fill_table(reports) {
    const table_body = document.getElementById("table_body");
    table_body.innerHTML = "";
    for (let report of reports) {
        const [new_item_id, item_id, error_type, date_created, username] = report;
        const row = document.createElement("tr");
        row.innerHTML = `<td>${new_item_id}</td><td>${item_id}</td><td>${error_type}</td><td>${date_created}</td><td>${username}</td>`;
        row.onclick = () => window.location.href = "/items/reports/" + new_item_id;
        table_body.appendChild(row);
    }
}

window.onload = function(){
    get_reports();
}