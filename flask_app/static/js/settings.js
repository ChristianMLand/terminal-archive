const terminalForm = document.querySelector("#terminal-form")
const terminalSelect = document.querySelector("#terminal-form select")
const terminalEmail = document.querySelector('#terminal-form input[type=email]')
const terminalPassword = document.querySelector('#terminal-form input[type=text]')

const accessForm = document.querySelector("#access-form");
const accessGrantedAlert = document.querySelector("#access-granted-alert")
const userList = document.querySelector("#user-list")

const passwordForm = document.querySelector("#password-form")

const accountLimit = userList ? userList.getAttribute("data-account-limit") : 0;

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
        createMessage(accessForm, user);
        if (user.status != "error") {
            const userLi = document.createElement("li");
            userLi.classList.add('list-group-item', 'd-flex', 'gap-4', 'justify-content-between', 'align-items-center');
            
            const span = document.createElement("span");
            span.classList.add("me-auto", "w-25");
            span.innerText = user.email;

            const select = document.createElement("select");
            select.classList.add("w-25", "form-select");
            select.name = "account_level";
            select.addEventListener("change", e => {
                updateAccess(e.target)
            });
            select.setAttribute("data-user-id", user.id);

            const accountLevels = ["Basic", "Admin"];
            for (let i = 0; i < accountLevels.length && i < accountLimit; i++) {
                const option = document.createElement("option");
                option.innerText = accountLevels[i];
                option.value = i + 1
                if (accountLimit == 1) {
                    select.disabled = true;
                }
                select.append(option);
            }

            const button = document.createElement("button");
            button.setAttribute("data-user-id", user.id);
            button.classList.add("btn", "btn-sm", "btn-outline-danger");
            button.addEventListener("click", e => {
                removeAccess(e.target);
            })
            button.innerText = "Remove";

            userLi.append(span, select, button);
            userList.append(userLi);
        }
    })
    .catch(console.error)
});

passwordForm && passwordForm.addEventListener("submit", e => {
    e.preventDefault();
    axios.post("/api/users/update", new FormData(passwordForm))
    .then(data => {
        createMessage(passwordForm, data.data);
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
        "id" : parseInt(elem.getAttribute("data-user-id"))
    })
    .then(data => {
        createMessage(accessForm, data.data)
    })
    .catch(console.error);
}

function removeAccess(elem) {
    axios.post('/api/users/delete', {
        "id" : parseInt(elem.getAttribute('data-user-id'))
    })
    .then(data => {
        createMessage(accessForm, data.data)
        if (data.data.status == "success") {
            elem.parentNode.remove();
        }
    })
    .catch(console.error)
}