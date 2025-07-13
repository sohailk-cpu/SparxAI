function send() {
  const input = document.getElementById("chat-input").value;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: input })
  })
  .then(res => res.json())
  .then(data => {
    document.querySelector(".chat-response").textContent = data.response;
    document.getElementById("chat-input").value = "";
  });
}

function startMic() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "hi-IN";
  recognition.start();
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("chat-input").value = transcript;
    send();
  };
}
