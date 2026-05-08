(function () {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("officeflow-theme");
  if (savedTheme) root.setAttribute("data-bs-theme", savedTheme);

  document.querySelector("[data-theme-toggle]")?.addEventListener("click", () => {
    const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-bs-theme", next);
    localStorage.setItem("officeflow-theme", next);
  });

  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => {
    document.querySelector(".sidebar")?.classList.toggle("open");
  });

  const toast = document.querySelector("[data-live-toast]");
  function showLiveToast(title, message) {
    if (!toast) return;
    toast.innerHTML = `<strong>${title}</strong><div>${message || ""}</div>`;
    toast.hidden = false;
    window.setTimeout(() => { toast.hidden = true; }, 5500);
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  if (window.location.pathname !== "/accounts/login/") {
    try {
      const socket = new WebSocket(`${protocol}://${window.location.host}/ws/officeflow/`);
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.kind === "notification") showLiveToast(data.title, data.message);
        if (data.kind === "attendance") showLiveToast("Attendance update", `${data.user} ${data.event.replace("_", " ")}`);
      };
    } catch (error) {
      console.debug("WebSocket unavailable", error);
    }
  }

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("/service-worker.js").catch(() => null));
  }
})();
