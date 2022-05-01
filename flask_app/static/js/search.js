const form = document.querySelector("form")
const tbody = document.querySelector("tbody")

$('.selectpicker').selectpicker();

form.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/filter', new FormData(form))
    .then(result => {
        tbody.innerHTML = ""
        const results = result.data.data
        for (let row of results) {
            const tr = document.createElement("tr")
            for (let key in row) {
                const td = document.createElement("td");
                td.innerText = row[key];
                tr.prepend(td);
            }
            tbody.append(tr);
        }
    })
    .catch(err => console.error(err))
})