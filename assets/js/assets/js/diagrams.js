// Pinned renderer. The search page remains self-contained and does not load this file.
const blocks = [...document.querySelectorAll('pre > code.language-mermaid, pre > code[data-lang="mermaid"]')];
if (blocks.length) {
  try {
    const { default: mermaid } = await import('https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.esm.min.mjs');
    mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default', flowchart: { htmlLabels: true, useMaxWidth: true } });
    for (const [index, code] of blocks.entries()) {
      const pre = code.parentElement;
      const source = code.textContent;
      const diagram = document.createElement('div');
      diagram.className = 'mermaid-diagram';
      diagram.setAttribute('role', 'img');
      diagram.setAttribute('aria-label', document.querySelector('h1')?.textContent || 'خريطة تدفق');
      // Render each diagram independently; keep the readable source available on failure.
      try {
        const { svg, bindFunctions } = await mermaid.render(`flow-diagram-${index}`, source);
        diagram.innerHTML = svg;
        pre.before(diagram);
        bindFunctions?.(diagram);
        const details = document.createElement('details');
        details.className = 'diagram-source';
        const summary = document.createElement('summary');
        summary.textContent = 'عرض النص الأصلي للخريطة';
        details.append(summary);
        pre.replaceWith(details);
        details.append(pre);
      } catch (error) {
        const note = document.createElement('p');
        note.className = 'diagram-error';
        note.textContent = 'تعذر رسم هذه الخريطة. النص الأصلي متاح أدناه.';
        pre.before(note);
        console.error('Diagram rendering failed', error);
      }
    }
  } catch (error) {
    const note = document.createElement('p');
    note.className = 'diagram-error';
    note.textContent = 'عرض الرسوم يحتاج اتصالًا لتحميل Mermaid. النص الأصلي متاح أدناه.';
    blocks[0].parentElement.before(note);
    console.error('Diagram renderer could not load', error);
  }
}
