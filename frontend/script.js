function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = async function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("output").textContent = "You said: " + transcript;

        const response = await fetch("http://localhost:8000/transcribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript: transcript })
        });
        const result = await response.json();
        console.log(result);
    };

    recognition.start();
}
