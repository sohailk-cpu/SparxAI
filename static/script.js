<script>
  let fromMic = false;

  function send() {
    const input = document.getElementById("chat-input").value;
    fromMic = false; // 🔇 Text se bhejne par bolna band

    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    })
    .then(res => res.json())
    .then(data => {
      document.querySelector(".chat-response").textContent = data.response;

      // 🎙️ Sirf mic se input pe bol
      if (fromMic) {
        speak(data.response);
      }

      document.getElementById("chat-input").value = "";
    });
  }

  function startVoiceChat() {
    fromMic = true; // 🔊 Mic se bolne par awaaz allow

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "hi-IN";
    recognition.start();

   recognition.onresult = function(event) {
  const transcript = event.results[0][0].transcript;
  document.getElementById("voice-response").innerText = "Thinking...";

  // Immediately send to backend
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: transcript })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("voice-response").innerText = data.response;
    speakText(data.response);  // Voice bolne ke liye
  });
};

  function speak(text) {
    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = "hi-IN";  // Hindi (India) accent
    msg.rate = 1.0;
    msg.pitch = 1.2;
    window.speechSynthesis.speak(msg);
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'hi-IN'; // Hindi me sunao
    synth.speak(utterance);
  }
</script>
