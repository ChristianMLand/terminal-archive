const form = document.querySelector("form")
const thead = document.querySelector("thead")
const tbody = document.querySelector("tbody")

form.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/filter', new FormData(form))
    .then(result => {
        tbody.innerHTML = ""
        thead.innerHTML = ""
        const results = result.data.data
        let tr = document.createElement("tr");
        for (let key in results[0]) {
            const th = document.createElement("th");
            th.innerText = key;
            tr.append(th);
        }
        thead.append(tr);
        for (let row of results) {
            let tr = document.createElement("tr")
            for (let key in row) {
                const td = document.createElement("td");
                td.innerText = row[key];
                tr.append(td);
            }
            tbody.append(tr);
        }
        console.log(results);
    })
    .catch(err => console.error(err))
})