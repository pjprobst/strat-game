document.addEventListener('DOMContentLoaded', () => {
    setOpp();
    getMessage();
});

async function setOpp() {
    const form = document.getElementById('game-settings');
    const oppRadios = document.querySelectorAll('input[name="opp"]');
    const minimaxWrapper = document.getElementById('minimaxWrapper');
    const depthInput = document.getElementById('depth');
    const depthValue = document.getElementById('depthValue');
    const output = document.getElementById('opp');

    oppRadios.forEach((radio) => {
        radio.addEventListener('change', (event) => {
          const isMinimax = event.target.value === 'minimax';
          minimaxWrapper.classList.toggle('hidden', !isMinimax);
          depthInput.disabled = !isMinimax;
        });
    });

    depthInput.addEventListener('input', () => {
        depthValue.textContent = depthInput.value;
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        
        const color = formData.get('color');
        const opponent = formData.get('opp');
        const depth = formData.get('depth');
    
        const payload = {
            opp: opponent,
            depth: depth,
            color: color
        }

        try {
            const response = await fetch("/game", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Server response:", result);
            output.textContent = JSON.stringify(result);
        } 
            catch (error) {
                console.error("Failed to send data:", error);
                output.textContent = error;
            }
    });
}

async function getMessage() {
    const response = await fetch("/message");

    const data = await response.json();
    
    document.getElementById("message").textContent = data.message;
}