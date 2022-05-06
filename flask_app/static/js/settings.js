const terminalForm = document.querySelector("#terminal-form")
const terminalSelect = document.querySelector("#terminal-form select")
const terminalEmail = document.querySelector('#terminal-form input[type=email]')
const terminalPassword = document.querySelector('#terminal-form input[type=text]')

const accessForm = document.querySelector("#access-form");
const accessGrantedAlert = document.querySelector("#access-granted-alert")
const userList = document.querySelector("#user-list")

const passwordForm = document.querySelector("#password-form")

//TODO make function for generating and displaying alert messages

terminalSelect && terminalSelect.addEventListener('change', e => {
    axios.get(`/api/terminals/${e.target.value}`)
    .then(data => {
        //TODO handle if status == "error" and show alert messge
        const terminal = data.data.terminal;
        terminalEmail.value = terminal.auth_email
        terminalPassword.value = terminal.auth_password
        console.log(data)
    })
    .catch(console.error)
    console.log(terminalEmail)
});

terminalForm && terminalForm.addEventListener('submit', e => {
    //TODO attempt to make a request to the auth_url with new credentials (with axios)
    //TODO show validation alert on page if request fails and do not update in DB
    e.preventDefault();
    axios.post('/api/terminals/update', new FormData(terminalForm))
    .then(data => {
        //TODO handle if status == "error" and show alert message
        console.log(data.data);
    })
    .catch(console.error)
});

accessForm && accessForm.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/api/users/create', new FormData(accessForm))
    .then(data => {
        //TODO handle if status == "error"
        //TODO refactor alert creation into seperate method
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
    .catch(console.error)
});

passwordForm && passwordForm.addEventListener("submit", e => {
    e.preventDefault();
    axios.post("/api/users/update", new FormData(passwordForm))
    .then(data => {
        console.log(data.data);
        //TODO alert that confirms it was updated successfully
        //TODO handle status == "error" and create error alert
    })
    .catch(console.error)
})

function updateAccess(elem) {
    axios.post('/api/users/update', {
        "account_level" : parseInt(elem.value),
        "id" : elem.getAttribute("data-user-id")
    })
    .then(console.log)
    .catch(console.error);
}

function removeAccess(elem) {
    axios.post('/api/users/delete', {
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