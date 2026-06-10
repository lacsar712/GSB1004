function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) {
    return;
  }

  const toast = document.createElement('div');
  toast.className = `toast align-items-center border-0 ${getToastClass(type)}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');

  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  container.appendChild(toast);

  if (window.bootstrap && window.bootstrap.Toast) {
    const instance = new bootstrap.Toast(toast, { delay: duration });
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
    instance.show();
    return;
  }

  setTimeout(() => toast.remove(), duration);
}

function getToastClass(type) {
  const classes = {
    success: 'text-bg-success',
    error: 'text-bg-danger',
    danger: 'text-bg-danger',
    warning: 'text-bg-warning',
    info: 'text-bg-primary',
  };
  return classes[type] || classes.info;
}

window.showToast = showToast;
