const terminalForm = document.querySelector("#terminal-form")
const terminalSelect = terminalForm.querySelector("select")

terminalSelect.addEventListener('change', e => {
    const terminalEmail = terminalForm.querySelector('input[type=email]')
    const terminalPassword = terminalForm.querySelector('input[type=text]')

    axios.get(`/terminals/${e.target.value}`)
    .then(data => {
        terminal = data.data.terminal;
        terminalEmail.value = terminal.auth_email
        terminalPassword.value = terminal.auth_password
        console.log(data)
    })
    .catch(console.error)
    console.log(terminalEmail)
})



