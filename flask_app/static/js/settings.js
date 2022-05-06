const terminalForm = document.querySelector("#terminal-form")
const terminalSelect = document.querySelector("#terminal-form select")
const terminalEmail = document.querySelector('#terminal-form input[type=email]')
const terminalPassword = document.querySelector('#terminal-form input[type=text]')

const accessForm = document.querySelector("#access-form");
const accessGrantedAlert = document.querySelector("#access-granted-alert")
const userList = document.querySelector("#user-list")

const passwordForm = document.querySelector("#password-form")

terminalSelect && terminalSelect.addEventListener('change', e => {
    axios.get(`/api/terminals/${e.target.value}`)
    .then(data => {
        const terminal = data.data.terminal;
        terminalEmail.value = terminal.auth_email
        terminalPassword.value = terminal.auth_password
        console.log(data)
    })
    .catch(console.error)
    console.log(terminalEmail)
});
//TODO attempt to make a request to the auth_url with new credentials (with axios)
terminalForm && terminalForm.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/api/terminals/update', new FormData(terminalForm))
    .then(data => {
        createMessage(terminalForm, data.data)
    })
    .catch(console.error)
});

accessForm && accessForm.addEventListener('submit', e => {
    e.preventDefault();
    axios.post('/api/users/create', new FormData(accessForm))
    .then(data => {
        const user = data.data;
        console.log(user)
        createMessage(accessForm, user)
        if (user.status != "error") {
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
        }
    })
    .catch(console.error)
});

passwordForm && passwordForm.addEventListener("submit", e => {
    e.preventDefault();
    axios.post("/api/users/update", new FormData(passwordForm))
    .then(data => {
        createMessage(passwordForm, data.data)
    })
    .catch(console.error)
})

function createMessage(form, data) {
    clearMessages();
    const message = document.createElement("div");
    message.classList.add("alert","mt-2", "msg", "text-center", "alert-dismissable", "fade", "show", "align-items-center", "d-flex", "justify-content-between", "gap-5")
    const span = document.createElement("span")
    const btn = document.createElement("button")
    btn.type = "button"
    btn.classList.add("btn-close")
    btn.setAttribute("data-bs-dismiss","alert")
    btn.setAttribute("aria-label","Close")
    if (data.status == "error") {
        message.classList.add("alert-danger");
        span.innerText = "Error: Something went wrong"
    } else if (data.status == "success") {
        message.classList.add("alert-success")
        span.innerText = "Successfully updated"
    } else {
        message.classList.add("alert-success")
        span.innerText = `User ${data.email} added with password: ${data.password}`
    }
    message.append(span,btn)
    form.append(message)
}

function clearMessages() {
    for (const msg of document.querySelectorAll(".msg")) {
        msg.remove()
    }
}

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
    })
    .catch(console.error)
}