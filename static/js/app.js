(function () {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("officeflow-theme");
  if (savedTheme) root.setAttribute("data-theme", savedTheme);

  const themeToggle = document.querySelector("[data-theme-toggle]");
  themeToggle?.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("officeflow-theme", next);
  });

  const sidebar = document.querySelector(".sidebar");
  const sidebarBackdrop = document.querySelector("[data-sidebar-backdrop]");

  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => {
    sidebar?.classList.toggle("open");
    if (sidebarBackdrop) sidebarBackdrop.classList.toggle("hidden");
  });

  sidebarBackdrop?.addEventListener("click", () => {
    sidebar?.classList.remove("open");
    sidebarBackdrop.classList.add("hidden");
  });

  document.querySelectorAll("[data-dropdown-toggle]").forEach((button) => {
    const menu = button.closest(".relative")?.querySelector("[data-dropdown-menu]");
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      menu?.classList.toggle("hidden");
    });
  });

  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    const passwordInput = button.closest(".form-field")?.querySelector("input[type='password']");
    if (!passwordInput) return;
    button.addEventListener("click", () => {
      const show = passwordInput.type === "password";
      passwordInput.type = show ? "text" : "password";
      button.innerHTML = show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
    });
  });

  document.addEventListener("click", (event) => {
    document.querySelectorAll("[data-dropdown-menu]").forEach((menu) => {
      if (!menu.closest(".relative")?.contains(event.target)) {
        menu.classList.add("hidden");
      }
    });
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
