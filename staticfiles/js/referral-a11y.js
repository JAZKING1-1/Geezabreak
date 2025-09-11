document.addEventListener('DOMContentLoaded', () => {
  const es = document.querySelector('.error-summary');
  if (es) {
    es.focus();
  }
  document.querySelectorAll('.error-summary a').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) {
        el.focus({preventScroll:true});
        el.scrollIntoView({behavior:'smooth',block:'center'});
      }
    });
  });

  // --- conditional reveals ---
  const toggle = (cb, selectors) => {
    const nodes = Array.from(document.querySelectorAll(selectors));
    if (!cb || !nodes.length) return;
    const apply = () => nodes.forEach(n => n.style.display = cb.checked ? '' : 'none');
    cb.addEventListener('change', apply); apply();
  };
  toggle(document.getElementById('id_interpreter_required'), 'label[for="id_preferred_language"], #id_preferred_language');
  toggle(document.getElementById('id_is_rereferral'), 'label[for="id_last_support_when"], #id_last_support_when');

  // --- children formset add (progressive enhancement) ---
  const wrap = document.getElementById('children-forms');
  if (!wrap) return; // nothing else if not on referral page
  const chip = document.getElementById('children-chip');
  const prefix = wrap.dataset.prefix; // expected 'children'
  const mgmtTotal = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const empty = document.getElementById('child-empty-form');

  const updateChip = () => {
    const cards = wrap.querySelectorAll('.child-card');
    chip.textContent = cards.length ? `${cards.length} child${cards.length>1?'ren':''}` : 'Not added';
  };
  updateChip();

  const addBtn = document.getElementById('add-child');
  if (addBtn) {
    addBtn.addEventListener('click', () => {
      const idx = parseInt(mgmtTotal.value, 10);
      const mk = (name) => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = `${prefix}-${idx}-${name}`;
        input.id = `id_${prefix}-${idx}-${name}`;
        input.placeholder = name === 'dob' ? 'DD/MM/YYYY' : '';
        return input.outerHTML;
      };
      const mkCheckbox = (name) => `<input type="checkbox" name="${prefix}-${idx}-${name}" id="id_${prefix}-${idx}-${name}">`;
      const mkSelect = (name, optionsHtml) => {
        const sel = document.createElement('select');
        sel.name = `${prefix}-${idx}-${name}`;
        sel.id = `id_${prefix}-${idx}-${name}`;
        sel.innerHTML = optionsHtml;
        return sel.outerHTML;
      };
      const relOptions = `\n        <option value="son">Son</option>\n        <option value="daughter">Daughter</option>\n        <option value="stepchild">Step-child</option>\n        <option value="foster">Foster child</option>\n        <option value="other">Other</option>`;

      const tpl = empty.content.cloneNode(true).firstElementChild;
      tpl.innerHTML = tpl.innerHTML
        .replace('__FULL_NAME__', mk('full_name'))
        .replace('__DOB__', mk('dob'))
        .replace('__REL__', mkSelect('relationship', relOptions))
        .replace('__ASN__', mkCheckbox('has_asn'))
        .replace('__SCH__', mk('school_nursery'));
      wrap.appendChild(tpl);
      mgmtTotal.value = idx + 1;
      updateChip();
    });
  }
});
