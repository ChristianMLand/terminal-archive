const terminalForm = document.querySelector("#terminal-form")
const terminalSelect = terminalForm.querySelector("select")

const accessForm = document.querySelector("#access-form");
const accessGrantedAlert = document.querySelector("#access-granted-alert")
const userList = document.querySelector("#user-list")

terminalSelect.addEventListener('change', e => {
    const terminalEmail = terminalForm.querySelector('input[type=email]')
    const terminalPassword = terminalForm.querySelector('input[type=text]')

    axios.get(`/terminals/${e.target.value}`)
    .then(data => {
        const terminal = data.data.terminal;
        terminalEmail.value = terminal.auth_email
        terminalPassword.value = terminal.auth_password
        console.log(data)
    })
    .catch(console.error)
    console.log(terminalEmail)
});


accessForm.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/grant-access', new FormData(accessForm))
    .then(data => {
        const user = data.data;
        accessGrantedAlert.classList.add('d-flex', 'alert', 'alert-success');
        accessGrantedAlert.innerText = `Granted user access with password: ${user.password}`;

        const userLi = document.createElement("li");
        userLi.classList.add('list-group-item', 'd-flex', 'gap-4', 'justify-content-between', 'align-items-center');
        userLi.innerHTML = `
            <span class="me-auto w-25">${user.email}</span>
            <select onchange="updateAccess(this)" data-user-id="${user.id}" name="account_level" class="w-25 form-select">
                <option value="1" selected>Basic</option>
                <option value="2">Admin</option>
            </select>
            <button onclick="removeAccess(this)" data-user-id="${user.id}" class="btn btn-sm btn-outline-danger">Remove</button>
            `
        userList.append(userLi);
    })
})

function updateAccess(elem) {
    axios.post('/update-access', {
        "account_level" : elem.value,
        "id" : elem.getAttribute("data-user-id")
    })
    .then(console.log)
    .catch(console.error);
}

function removeAccess(elem) {
    axios.post('/remove-access', {
        "id" : elem.getAttribute('data-user-id')
    })
    .then(data => {
        data = data.data;
        if (data.status == "success") {
            elem.parentNode.remove();
        }
        console.log(data);
    })
    .catch(console.error)
}


