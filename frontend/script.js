function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = async function(event) {
        const transcript = event.results[event.resultIndex][0].transcript.trim();
        console.log("Final transcript:", transcript);
        document.getElementById("output").textContent = transcript;

        const response = await fetch("http://localhost:8000/transcribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ transcript })
        });

        const result = await response.json();
        console.log("Backend response:", result);
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
    };

    recognition.onend = function() {
        console.log("Speech ended. Restarting...");
        recognition.start(); // Auto-restart after silence
    };

    recognition.start();
}