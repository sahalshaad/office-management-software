document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".notifications-form");
  if (!form) return;

  const recipientCards = Array.from(form.querySelectorAll(".recipient-card"));
  const searchInput = form.querySelector("[data-recipient-search]");
  const departmentFilter = form.querySelector("[data-department-filter]");
  const roleFilter = form.querySelector("[data-role-filter]");
  const selectAllCheckbox = form.querySelector("[data-select-all]");
  const recipientCount = form.querySelector("[data-recipient-count]");
  const globalCheckbox = form.querySelector("#id_is_global");
  const previewButton = form.querySelector(".preview-button");
  const cancelButton = form.querySelector(".cancel-button");
  const sendButton = form.querySelector(".send-button");
  const spinner = sendButton.querySelector(".spinner-border");
  const previewModalElement = document.getElementById("notificationPreviewModal");
  const previewTitle = previewModalElement.querySelector("[data-preview-title]");
  const previewType = previewModalElement.querySelector("[data-preview-type]");
  const previewTarget = previewModalElement.querySelector("[data-preview-target]");
  const previewRecipients = previewModalElement.querySelector("[data-preview-recipients]");
  const previewMessage = previewModalElement.querySelector("[data-preview-message]");
  const previewConfirmButton = previewModalElement.querySelector(".preview-confirm-button");

  const titleInput = form.querySelector("#id_title");
  const typeInput = form.querySelector("#id_notification_type");
  const targetRoleInput = form.querySelector("#id_target_role");
  const messageInput = form.querySelector("#id_message");

  const previewModal = previewModalElement ? new bootstrap.Modal(previewModalElement) : null;

  function showToast(title, message, variant = "primary") {
    const toast = document.querySelector("[data-live-toast]");
    if (!toast) return;
    toast.innerHTML = `<strong>${title}</strong><div>${message || ""}</div>`;
    toast.hidden = false;
    toast.classList.remove("toast-success", "toast-danger", "toast-primary");
    toast.classList.add(`toast-${variant}`);
    window.setTimeout(() => {
      toast.hidden = true;
    }, 5500);
  }

  function updateRecipientDisplay() {
    const visibleCards = recipientCards.filter((card) => card.offsetParent !== null);
    const checkedCards = visibleCards.filter((card) => card.querySelector(".recipient-checkbox").checked);
    const totalChecked = recipientCards.filter((card) => card.querySelector(".recipient-checkbox").checked).length;
    const totalCards = recipientCards.length;

    recipientCards.forEach((card) => {
      const checkbox = card.querySelector(".recipient-checkbox");
      if (checkbox.checked) {
        card.classList.add("selected");
      } else {
        card.classList.remove("selected");
      }
    });

    if (selectAllCheckbox) {
      selectAllCheckbox.checked = visibleCards.length > 0 && visibleCards.every((card) => card.querySelector(".recipient-checkbox").checked);
      selectAllCheckbox.disabled = globalCheckbox && globalCheckbox.checked;
    }

    if (globalCheckbox && globalCheckbox.checked) {
      recipientCount.textContent = "Global notification enabled";
    } else if (totalChecked > 0 && totalChecked === totalCards) {
      recipientCount.textContent = "All staff selected";
    } else {
      recipientCount.textContent = `${totalChecked} staff selected`;
    }
  }

  function applyFilters() {
    const searchValue = searchInput.value.trim().toLowerCase();
    const departmentValue = departmentFilter.value.toLowerCase();
    const roleValue = roleFilter.value.toLowerCase();

    let visibleCount = 0;
    recipientCards.forEach((card) => {
      const title = card.querySelector(".recipient-info strong").textContent.toLowerCase();
      const email = card.querySelector(".recipient-email").textContent.toLowerCase();
      const department = card.dataset.department.toLowerCase();
      const role = card.dataset.role.toLowerCase();

      const matchesSearch = !searchValue || [title, email, department, role].some((value) => value.includes(searchValue));
      const matchesDepartment = !departmentValue || department === departmentValue;
      const matchesRole = !roleValue || role === roleValue;
      const visible = matchesSearch && matchesDepartment && matchesRole;

      card.style.display = visible ? "grid" : "none";
      visibleCount += visible ? 1 : 0;
    });

    const emptyState = form.querySelector(".recipient-empty-state");
    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? "grid" : "none";
    }

    updateRecipientDisplay();
  }

  function toggleSelectAll(checked) {
    recipientCards.forEach((card) => {
      if (card.offsetParent === null) return;
      const checkbox = card.querySelector(".recipient-checkbox");
      checkbox.checked = checked;
    });
    updateRecipientDisplay();
  }

  function updateGlobalMode() {
    const enabled = globalCheckbox.checked;
    recipientCards.forEach((card) => {
      const checkbox = card.querySelector(".recipient-checkbox");
      checkbox.disabled = enabled;
      card.classList.toggle("disabled", enabled);
    });
    updateRecipientDisplay();
  }

  function getSelectedRecipientsText() {
    const selected = recipientCards.filter((card) => card.querySelector(".recipient-checkbox").checked);
    if (globalCheckbox.checked) {
      return targetRoleInput.value ? `Global notification to all ${targetRoleInput.options[targetRoleInput.selectedIndex].text}` : "Global notification to all staff";
    }
    if (selected.length === 0) {
      return "No recipients selected";
    }
    if (selected.length === recipientCards.length) {
      return "All staff selected";
    }
    return `${selected.length} staff selected`;
  }

  function renderPreview() {
    if (!titleInput.value.trim() || !messageInput.value.trim()) {
      showToast("Validation required", "Please enter a title and message before previewing.", "danger");
      return;
    }

    previewTitle.textContent = titleInput.value.trim();
    previewType.textContent = typeInput.options[typeInput.selectedIndex].text;
    previewTarget.textContent = targetRoleInput.value
      ? `Target role: ${targetRoleInput.options[targetRoleInput.selectedIndex].text}`
      : "Target: All roles";
    previewRecipients.textContent = getSelectedRecipientsText();
    previewMessage.textContent = messageInput.value.trim();

    if (previewModal) {
      previewModal.show();
    }
  }

  function handleFormSubmit() {
    sendButton.disabled = true;
    spinner.classList.remove("d-none");
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (departmentFilter) {
    departmentFilter.addEventListener("change", applyFilters);
  }
  if (roleFilter) {
    roleFilter.addEventListener("change", applyFilters);
  }
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener("change", (event) => toggleSelectAll(event.target.checked));
  }
  if (globalCheckbox) {
    globalCheckbox.addEventListener("change", updateGlobalMode);
    updateGlobalMode();
  }

  recipientCards.forEach((card) => {
    const checkbox = card.querySelector(".recipient-checkbox");
    checkbox.addEventListener("change", updateRecipientDisplay);
  });

  if (previewButton) {
    previewButton.addEventListener("click", renderPreview);
  }

  if (previewConfirmButton) {
    previewConfirmButton.addEventListener("click", () => {
      if (previewModal) previewModal.hide();
      handleFormSubmit();
      form.submit();
    });
  }

  if (cancelButton) {
    cancelButton.addEventListener("click", () => {
      window.location.href = "/notifications/";
    });
  }

  form.addEventListener("submit", handleFormSubmit);
  applyFilters();

  document.querySelectorAll(".toast-stack .alert").forEach((alert) => {
    const text = alert.textContent.trim();
    const variant = alert.classList.contains("alert-danger") ? "danger" : alert.classList.contains("alert-success") ? "success" : "primary";
    const title = variant === "success" ? "Success" : variant === "danger" ? "Error" : "Notice";
    showToast(title, text, variant);
  });
});
