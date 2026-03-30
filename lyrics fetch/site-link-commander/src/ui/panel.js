import { MSG } from '../common/messaging.js';

export function createPanel(shadowRoot, handlers) {
  const panel = document.createElement('div');
  panel.id = 'slc-panel';
  panel.hidden = true;
  panel.innerHTML = `
    <h3>SiteLink Commander</h3>
    <section>
      <label>Pair with tab</label>
      <div class="row">
        <select id="slc-pair-list"></select>
        <button id="slc-pair-btn" class="primary">Pair</button>
      </div>
      <button id="slc-unpair">Unpair</button>
      <div id="slc-pair-status" class="pill">Not paired</div>
    </section>

    <section>
      <label>Quick actions</label>
      <div class="row">
        <button data-action="send-selection" class="primary">Send Selection</button>
        <button data-action="sync-form">Sync Form</button>
      </div>
      <div class="row">
        <input id="slc-selector" placeholder="CSS selector to click/fill" />
      </div>
      <div class="row">
        <button data-action="click-selector">Trigger Click</button>
        <button data-action="scrape-selector">Scrape & Send</button>
      </div>
      <textarea id="slc-fill-data" rows="3" placeholder='{"name":"Ada","email":"ada@example.com"}'></textarea>
      <button data-action="fill-form">Fill Form</button>
    </section>

    <section>
      <label>Automations</label>
      <input id="slc-auto-name" placeholder="Name" />
      <textarea id="slc-auto-steps" rows="3" placeholder='[{"type":"sendSelection"},{"type":"click","selector":"button.submit"}]'></textarea>
      <div class="row">
        <button id="slc-save-auto" class="primary">Save</button>
        <button id="slc-run-auto">Run</button>
      </div>
      <select id="slc-auto-list"></select>
      <button id="slc-del-auto">Delete</button>
    </section>

    <section>
      <label>Domain controls</label>
      <div class="row">
        <button id="slc-allow-domain" class="primary">Allow</button>
        <button id="slc-block-domain">Block</button>
      </div>
      <div id="slc-domain-status" class="pill"></div>
    </section>

    <section>
      <label>Recent logs</label>
      <div id="slc-logs" class="log"></div>
    </section>
  `;
  shadowRoot.appendChild(panel);

  const $ = (id) => panel.querySelector(id);

  $('#slc-pair-btn').onclick = () => handlers.pair($('#slc-pair-list').value);
  $('#slc-unpair').onclick = handlers.unpair;
  panel.querySelectorAll('[data-action]').forEach(btn =>
    btn.onclick = () => handlers.action(btn.dataset.action)
  );
  $('#slc-save-auto').onclick = () => handlers.saveAutomation($('#slc-auto-name').value, $('#slc-auto-steps').value);
  $('#slc-run-auto').onclick = () => handlers.runAutomation($('#slc-auto-list').value);
  $('#slc-del-auto').onclick = () => handlers.deleteAutomation($('#slc-auto-list').value);
  $('#slc-allow-domain').onclick = () => handlers.updateDomain('allow');
  $('#slc-block-domain').onclick = () => handlers.updateDomain('block');

  return {
    panel,
    setVisible(v) { panel.hidden = !v; },
    setPairStatus(text) { $('#slc-pair-status').textContent = text; },
    setDomainStatus(text) { $('#slc-domain-status').textContent = text; },
    setPairs(list) {
      const sel = $('#slc-pair-list');
      sel.innerHTML = '';
      list.forEach(({ id, title }) => {
        const o = document.createElement('option');
        o.value = id; o.textContent = `#${id} — ${title}`;
        sel.appendChild(o);
      });
    },
    setAutomations(list) {
      const sel = $('#slc-auto-list');
      sel.innerHTML = '';
      list.forEach(a => {
        const o = document.createElement('option');
        o.value = a.id; o.textContent = a.name;
        sel.appendChild(o);
      });
    },
    logs(html) { $('#slc-logs').innerHTML = html; },
    getSelector() { return $('#slc-selector').value; },
    getFillData() { return $('#slc-fill-data').value; }
  };
}
