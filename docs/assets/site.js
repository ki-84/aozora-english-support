document.querySelectorAll('[data-translation-toggle]').forEach((button) => {
  const translation = document.getElementById(button.getAttribute('aria-controls'));
  if (!translation) return;
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    translation.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
    button.querySelector('span').textContent = open ? '日本語訳を閉じる' : '日本語訳を見る';
  });
});
