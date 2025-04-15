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

function sort_reports() {}

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