(function () {
  const state = document.querySelector("[data-location-state]");
  const message = document.querySelector("[data-punch-message]");
  const video = document.querySelector("[data-selfie-video]");
  const canvas = document.querySelector("[data-selfie-canvas]");
  const selfieToggle = document.querySelector("[data-selfie-toggle]");
  let stream = null;

  function csrfToken() {
    return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1] || "";
  }

  function setState(text, ok = false) {
    if (state) {
      state.querySelector("span").textContent = text;
      state.style.borderColor = ok ? "#1f7a63" : "";
    }
  }

  function locate() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation is not supported by this browser."));
        return;
      }
      setState("Requesting GPS location...");
      navigator.geolocation.getCurrentPosition(
        position => {
          const coords = position.coords;
          setState(`GPS ready · accuracy ${Math.round(coords.accuracy)}m`, true);
          resolve({ latitude: coords.latitude, longitude: coords.longitude, accuracy_m: coords.accuracy });
        },
        error => reject(new Error(error.message || "Location permission denied.")),
        { enableHighAccuracy: true, timeout: 14000, maximumAge: 0 }
      );
    });
  }

  async function ensureCamera() {
    if (!selfieToggle?.checked) return "";
    if (!stream) {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
      video.srcObject = stream;
      video.hidden = false;
      await video.play();
    }
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.82);
  }

  async function punch(action) {
    const button = document.querySelector(`[data-punch="${action}"]`);
    button.disabled = true;
    try {
      const location = await locate();
      const selfie_data = await ensureCamera();
      const response = await fetch(`/api/attendance/records/punch-${action}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ ...location, selfie_data })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Attendance could not be marked.");
      message.textContent = `${action === "in" ? "Punch in" : "Punch out"} recorded successfully.`;
      message.classList.remove("text-secondary");
      message.classList.add("text-success");
      window.setTimeout(() => window.location.reload(), 900);
    } catch (error) {
      message.textContent = error.message;
      message.classList.remove("text-secondary", "text-success");
      message.classList.add("text-danger");
    } finally {
      button.disabled = false;
    }
  }

  document.querySelectorAll("[data-punch]").forEach(button => {
    button.addEventListener("click", () => punch(button.dataset.punch));
  });

  locate().catch(error => setState(error.message));
})();
