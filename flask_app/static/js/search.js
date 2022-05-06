const form = document.querySelector("form")
const tbody = document.querySelector("tbody")
const fetchBtn = document.querySelector("#actions button")
const actions = document.querySelector("main")

$('.selectpicker').selectpicker();

form.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/availabilities/filter', new FormData(form))
    .then(result => {
        tbody.innerHTML = ""
        const results = result.data.data
        for (let row of results) {
            const tr = document.createElement("tr")
            const cells = [row.terminal, row.ssl, row.container, row.created_at, row.type]
            for (let cell of cells) {
                const td = document.createElement("td");
                td.innerText = cell;
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