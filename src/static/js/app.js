// Placeholder for future enhancements (toasts, progress, etc.)
document.addEventListener('DOMContentLoaded', () => {
  // Simple ripple on buttons
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.classList.add('clicked');
      setTimeout(() => btn.classList.remove('clicked'), 160);
    });
  });
});



