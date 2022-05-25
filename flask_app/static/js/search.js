const form = document.querySelector("form")
const tbody = document.querySelector("tbody")
const fetchBtn = document.querySelector("#actions button")
const actions = document.querySelector("main")

$('.selectpicker').selectpicker();

function convertTZ(date, tzString) {
    return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: tzString}));   
}

(() => {
    let today = new Date()
    today.setUTCHours(today.getUTCHours() - 7)
    today.setUTCHours(0)
    today.setUTCMinutes(0)
    today.setUTCMilliseconds(0)
    today.setUTCSeconds(0)
    document.querySelector("input[name=start_date]").value = today.toISOString().substring(0,16)
})()

form.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/availabilities/filter', new FormData(form))
    .then(data => {
        tbody.innerHTML = ""
        const results = data.data
        if (results.status == "error") {
            return
        }
        for (let row of results) {
            const tr = document.createElement("tr")
            const cells = [row.terminal, row.ssl, row.container, row.first_available, row.last_available, row.type]
            for (let i = 0; i < cells.length; i++) {
                const td = document.createElement("td");
                const cell = cells[i];
                if (i === 3 || i === 4) {
                    console.log(cell);
                    const cellDate = convertTZ(cell, "America/Los_Angeles")
                    cellDate.setUTCHours(cellDate.getUTCHours() + 7)
                    td.innerText = cellDate
                } else {
                    td.innerText = cell;
                }
                tr.append(td);
            }
            tbody.append(tr);
        }
    })
    .catch(err => console.error(err))
})

fetchBtn.addEventListener("click", e => {
    if (confirm("Fetch current data from the terminal websites? This may take several seconds")) {
        axios.get('/availabilites/fetch')
        .then(result => {
            const msg = document.createElement("div")
            msg.classList.add("alert","text-center","msg", "alert-dismissable", "fade", "show", "align-items-center", "d-flex", "justify-content-between", "gap-5")
            const span = document.createElement("span")
            const btn = document.createElement("button")
            btn.type = "button"
            btn.classList.add("btn-close")
            btn.setAttribute("data-bs-dismiss","alert")
            btn.setAttribute("aria-label","Close")
            if (result.data.status == "success") {
                msg.classList.add("alert-success")
                span.innerText = "Data fetched successfuly"
            } else if (result.data.status == "error") {
                msg.classList.add("alert-danger")
                span.innerText = "Error: Something went wrong"
            }
            msg.append(span,btn)
            actions.append(msg)
        })
        .catch(console.error);
    }
})