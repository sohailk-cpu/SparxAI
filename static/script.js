<input type="text" id="chat-input" placeholder="Type here..." />
<button onclick="send()">Send</button>

<div class="chat-area"></div>

<script>
  function send() {
    const inputElement = document.getElementById("chat-input");
    const input = inputElement.value.trim();
    if (input === "") return;

    const chat = document.createElement("div");
    chat.className = "chat-response";
    chat.textContent = "You said: " + input;
    document.querySelector(".chat-area").appendChild(chat);

    inputElement.value = "";  // ✅ Clear input
  }

fetch("/voice-chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: transcript }) // transcript = mic से लिया गया input
})
.then(res => res.json())
.then(data => {
  if (data.audio_url) {
    const audio = new Audio(data.audio_url);
    audio.play();
  }
});

</script>
