async function getMessage() {
    const response = await fetch("/message");

    const data = await response.json();
    
    document.getElementById("message").textContent = data.message;
}

document.getElementById("get-message").addEventListener("click", getMessage);