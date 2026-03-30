export function injectShadowHost(id = 'slc-root') {
  if (document.getElementById(id)) return null;
  const host = document.createElement('div');
  host.id = id;
  host.style.all = 'initial';
  document.documentElement.appendChild(host);
  const shadow = host.attachShadow({ mode: 'open' });
  return shadow;
}

export function getActiveEditable() {
  const el = document.activeElement;
  if (!el) return null;
  const editable = ['INPUT', 'TEXTAREA'];
  if (editable.includes(el.tagName) || el.isContentEditable) return el;
  return null;
}

export function setValue(el, text) {
  if (!el) return false;
  if (el.isContentEditable) {
    el.textContent = text;
  } else {
    el.value = text;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  return true;
}

export function clickSelector(sel) {
  const target = document.querySelector(sel);
  if (target) {
    target.click();
    return true;
  }
  return false;
}
