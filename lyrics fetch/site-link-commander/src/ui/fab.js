export function createFab(shadowRoot, onClick) {
  const btn = document.createElement('div');
  btn.id = 'slc-button';
  btn.textContent = '⇆';
  btn.title = 'Open SiteLink Commander';
  btn.addEventListener('click', onClick);
  shadowRoot.appendChild(btn);
  return btn;
}
