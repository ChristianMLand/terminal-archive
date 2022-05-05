const form = document.querySelector("form")
const tbody = document.querySelector("tbody")

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

function fetchCurrentData() {
    axios.get('/availabilites/fetch')
    .then(console.log)
    .catch(console.error);
}