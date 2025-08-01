let mediaRecorder;
let audioChunks = [];
let silenceTimer;
let stream;
let isRunning = false;

const startBtn = document.getElementById("startBtn");
const endBtn = document.getElementById("endBtn");
const chatBox = document.getElementById("chatBox");
const statusDisplay = document.getElementById("statusDisplay");

startBtn.onclick = async () => {
  isRunning = true;
  startBtn.disabled = true;
  endBtn.disabled = false;
  statusDisplay.innerText = "🎤 ಧ್ವನಿಯನ್ನು ಕೇಳುತ್ತಿದೆ...";

  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  await startRecordingLoop();
};

endBtn.onclick = () => {
  isRunning = false;
  stopRecording();
  statusDisplay.innerText = "🛑 ನಿಲ್ಲಿಸಲಾಗಿದೆ.";

  // Call backend to clear chat
  fetch("http://localhost:8000/clear_chat", {
    method: "POST"
  })
  .then(response => response.json())
  .then(data => {
    console.log(data.message); // Optional: show feedback
  })
  .catch(error => {
    console.error("Error clearing chat:", error);
  });
};


async function startRecordingLoop() {
  if (!isRunning) return;

  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    if (audioChunks.length === 0 || !isRunning) return;

    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');

    statusDisplay.innerText = "🔄 ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ...";

    try {
      const res = await fetch('http://localhost:8000/voice', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      addToChat(data.user_text, data.bot_text);
      await playAudio(data.audio_url);
    } catch (err) {
      console.error("❌ ದೋಷ:", err);
      statusDisplay.innerText = "❌ ದೋಷವಾಯಿತು. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.";
    }

    if (isRunning) {
      statusDisplay.innerText = "🎤 ಧ್ವನಿಯನ್ನು ಕೇಳುತ್ತಿದೆ...";
      await startRecordingLoop();
    }
  };

  mediaRecorder.start();
  detectSilence(stream, 2000);
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  if (silenceTimer) clearTimeout(silenceTimer);
}

function detectSilence(stream, silenceDuration = 3000) {
  const audioCtx = new AudioContext();
  const source = audioCtx.createMediaStreamSource(stream);
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  source.connect(analyser);

  const data = new Uint8Array(analyser.fftSize);

  const checkSilence = () => {
    analyser.getByteTimeDomainData(data);
    const maxVolume = Math.max(...data);
    const silence = maxVolume < 130;

    if (silence) {
      if (!silenceTimer) {
        silenceTimer = setTimeout(() => {
          stopRecording();
        }, silenceDuration);
      }
    } else {
      if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
      }
    }

    if (isRunning) {
      requestAnimationFrame(checkSilence);
    }
  };

  checkSilence();
}

function addToChat(user, bot) {
  chatBox.innerHTML += `
    <p class="user-msg">🙋‍♂️ ${user}</p>
    <p class="bot-msg">🤖 ${bot}</p>
    <hr/>
  `;
  chatBox.scrollTop = chatBox.scrollHeight;
}

function playAudio(url) {
  return new Promise((resolve) => {
    const audio = new Audio(url);
    audio.onended = () => resolve();
    audio.onerror = () => resolve();
    audio.play();
  });
}
