#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAUDI-LABOR-INTEL-001 — مولّد صفحة البحث والتصفية (search.html).
يقرأ ملفات data/*.csv ويدمجها داخل صفحة HTML مستقلة (تعمل من file:// دون خادم)
بحيث تكون البيانات مدمجة كJSON — بلا شبكة، بلا اعتماديات خارجية.
الاستخدام:  python3 tools/build_search_page.py
"""
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "search.html"

REGISTRIES = [
    ("01-systems-laws.csv", "الأنظمة واللوائح"),
    ("02-decisions.csv", "القرارات والتعاميم"),
    ("03-entities-platforms.csv", "الجهات والمنصات"),
    ("04-services-procedures.csv", "الخدمات والإجراءات"),
    ("05-fees-costs.csv", "الرسوم والتكاليف"),
    ("06-visas.csv", "أنواع التأشيرات"),
    ("07-iqama-types.csv", "أنواع الإقامات"),
    ("08-professions.csv", "المهن والتصنيفات"),
    ("09-transfer-conditions.csv", "شروط نقل الخدمات"),
    ("10-profession-change.csv", "تغيير المهنة"),
    ("11-employer-obligations.csv", "التزامات صاحب العمل"),
    ("12-worker-rights.csv", "حقوق العامل"),
    ("13-violations-penalties.csv", "المخالفات والغرامات"),
    ("14-insurance-health.csv", "التأمينات والفحوصات"),
]

def load_csv(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows

def git_commit_date() -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return date.today().isoformat()

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>قاعدة البحث | SAUDI-LABOR-INTEL-001</title>
<style>
  :root {
    --bg: #f7f8fa; --card: #ffffff; --ink: #1c2330; --muted: #5b6675;
    --line: #d9dee6; --accent: #0b5b3f; --accent-ink: #ffffff;
    --warn: #8a5b00; --warn-bg: #fff6e0; --ok: #0b5b3f; --ok-bg: #e6f4ec;
    --bad: #7a1f1f; --bad-bg: #fbeaea; --future-bg: #eef2ff; --future: #2b3a8f;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: "Segoe UI", Tahoma, "Noto Sans Arabic", sans-serif;
    line-height: 1.7;
  }
  .skip-link { position: absolute; inset-inline-start: 8px; top: -48px; background: var(--accent); color: var(--accent-ink); padding: .5rem 1rem; border-radius: 6px; z-index: 10; transition: top .15s ease; }
  .skip-link:focus { top: 8px; }
  .wrap { max-width: 1100px; margin-inline: auto; padding: 1rem; }
  header.site { background: var(--accent); color: var(--accent-ink); padding: 1.25rem 0; }
  header.site h1 { margin: 0; font-size: 1.35rem; }
  header.site p { margin: .25rem 0 0; opacity: .9; font-size: .95rem; }
  .controls {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 1rem; display: grid; gap: .75rem; margin-block: 1rem;
  }
  .controls .row { display: flex; flex-wrap: wrap; gap: .75rem; align-items: end; }
  .field { display: grid; gap: .25rem; flex: 1 1 240px; }
  .field label { font-size: .85rem; color: var(--muted); }
  input[type="search"], select {
    width: 100%; padding: .55rem .75rem; border: 1px solid var(--line);
    border-radius: 8px; font: inherit; background: #fff; color: var(--ink);
  }
  input[type="search"]:focus-visible, select:focus-visible, a:focus-visible, button:focus-visible {
    outline: 3px solid #2b3a8f; outline-offset: 2px;
  }
  .count[aria-live="polite"] { font-size: .9rem; color: var(--muted); }
  .table-wrapper {
    overflow: auto; max-inline-size: 100%; max-block-size: min(560px, 75vh);
    container-type: inline-size; border: 1px solid var(--line); border-radius: 12px;
    background: var(--card);
  }
  table { border-collapse: separate; border-spacing: 0; width: 100%; font-size: .95rem; }
  caption { text-align: start; padding: .75rem 1rem; color: var(--muted); }
  thead { position: sticky; inset-block-start: 0; z-index: 1; }
  thead th { background: #eef1f5; border-block-end: 2px solid var(--line); padding: .6rem .75rem; text-align: start; white-space: nowrap; }
  tbody td, tbody th { padding: .55rem .75rem; border-block-end: 1px solid var(--line); text-align: start; vertical-align: top; }
  tbody th { position: sticky; inset-inline-start: 0; background: #fff; min-width: 9ch; white-space: nowrap; font-weight: 700; }
  tbody tr:hover td, tbody tr:hover th { background: #f3f7f5; }
  td .src a { word-break: break-all; }
  .badge { display: inline-block; padding: .1rem .55rem; border-radius: 999px; font-size: .8rem; border: 1px solid transparent; }
  .badge.ساري { background: var(--ok-bg); color: var(--ok); }
  .badge.ملغى, .badge.معدل { background: var(--bad-bg); color: var(--bad); }
  .badge.مشروط { background: var(--warn-bg); color: var(--warn); }
  .badge.مستقبل_التطبيق { background: var(--future-bg); color: var(--future); }
  .badge.غير_متحقق { background: #f0f0f0; color: var(--muted); }
  .unknown-note { color: var(--warn); }
  footer.site { margin-block: 1.5rem 2.5rem; color: var(--muted); font-size: .85rem; }
  @container (width < 640px) {
    table, caption, tbody, tr, th, td { display: block; width: 100%; }
    thead { display: none; }
    tr { border-block-end: 1px solid var(--line); padding-block: .5rem; }
    tbody th { position: static; background: transparent; }
    td::before {
      content: attr(data-label) ": ";
      font-weight: 700; color: var(--muted);
    }
  }
</style>
</head>
<body>
<a class="skip-link" href="#results">تخطَّ إلى النتائج</a>
<header class="site">
  <div class="wrap">
    <h1>قاعدة البحث والتصفية — منظومة الإقامة والعمل والاستقدام</h1>
    <p>المعرف SAUDI-LABOR-INTEL-001 · تاريخ بناء الصفحة: __BUILD_DATE__</p>
  </div>
</header>
<main id="results" class="wrap">
  <p>صفحة بحث محلية مستقلة تعمل دون إنترنت، تُمكّن من البحث والتصفية في السجلات الأربعة عشر للقاعدة المعرفية. المصادر ودرجة التحقق مذكورة حسب المتاح؛ بعض الإحالات داخلية وليست مصادر رسمية مباشرة.</p>
  <form class="controls" onsubmit="return false;">
    <div class="row">
      <div class="field">
        <label for="dataset">السجل</label>
        <select id="dataset">__DATASET_OPTIONS__</select>
      </div>
      <div class="field" style="flex:2 1 320px;">
        <label for="q">بحث نصي (في كل الحقول)</label>
        <input type="search" id="q" placeholder="مثال: المقابل المالي، نقل الخدمات، FEE-001، 650…">
      </div>
      <div class="field">
        <label for="status">الحالة النظامية</label>
        <select id="status">
          <option value="">الكل</option>
          <option>ساري</option>
          <option>مشروط</option>
          <option>معدل</option>
          <option>ملغى</option>
          <option>مستقبل_التطبيق</option>
          <option>غير_متحقق</option>
        </select>
      </div>
    </div>
    <p class="count" aria-live="polite" id="count">—</p>
  </form>
  <div class="table-wrapper" tabindex="0" role="region" aria-label="جدول نتائج السجلات">
    <table>
      <caption id="tbl-caption">نتائج السجل المختار</caption>
      <thead><tr id="thead-row"></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <footer class="site">
    <p><strong>تنبيه منهجي:</strong> الصفحة تعرض محتوى مدمجًا كما وُلّدت؛ راجع تاريخ الاطلاع لكل صف، وإن كان «غير متحقق» فلا تعتمد الحكم قبل مراجعة المصدر الرسمي. آخر تحديث للملف: __BUILD_DATE__.</p>
  </footer>
</main>
<script id="kb-data" type="application/json">__DATA_JSON__</script>
<script>
(function () {
  "use strict";
  var packed = JSON.parse(document.getElementById("kb-data").textContent);
  var KB = { _titles: packed._titles };
  Object.keys(packed).filter(function (key) { return key !== "_titles"; }).forEach(function (key) {
    var dataset = packed[key];
    KB[key] = dataset.rows.map(function (values) {
      var row = {};
      dataset.columns.forEach(function (column, i) { row[column] = values[i]; });
      return row;
    });
  });
  var ds = document.getElementById("dataset");
  var q = document.getElementById("q");
  var st = document.getElementById("status");
  var theadRow = document.getElementById("thead-row");
  var tbody = document.getElementById("tbody");
  var count = document.getElementById("count");
  var caption = document.getElementById("tbl-caption");
  var timer = null;

  function colsOf(key) {
    var first = KB[key][0] || {};
    return Object.keys(first);
  }

  function normalizeArabic(value) {
    return String(value || "").normalize("NFKC")
      .replace(/[\u064B-\u065F\u0670\u0640]/g, "")
      .replace(/[أإآٱ]/g, "ا").replace(/ى/g, "ي").toLowerCase();
  }

  function sourceLinks(value) {
    // Split explicit source separators, never the spaces inside Arabic URL paths.
    return value.split(/\s+[+·]\s+/).map(function (part) {
      var url = part.trim();
      if (/^https?:\/\//i.test(url) && !/[<>]/.test(url)) return url;
      if (/^(docs|cases|flows)\/[a-zA-Z0-9_-]+\.md$/.test(url)) {
        return url.replace(/\.md$/, ".html");
      }
      return null;
    }).filter(Boolean);
  }

  function render() {
    var key = ds.value;
    var rows = KB[key] || [];
    var needle = normalizeArabic(q.value).trim();
    var statusFilter = st.value;
    var cols = colsOf(key);
    theadRow.innerHTML = "";
    cols.forEach(function (c) {
      var th = document.createElement("th");
      th.scope = "col";
      th.textContent = c;
      theadRow.appendChild(th);
    });
    var shown = 0;
    var frag = document.createDocumentFragment();
    rows.forEach(function (row) {
      var hay = normalizeArabic(cols.map(function (c) { return String(row[c] || ""); }).join(" "));
      if (needle && hay.indexOf(needle) === -1) return;
      if (statusFilter && row["status"] !== statusFilter) return;
      shown++;
      var tr = document.createElement("tr");
      cols.forEach(function (c, i) {
        var cell = (i === 0) ? document.createElement("th") : document.createElement("td");
        if (i === 0) cell.scope = "row";
        var val = String(row[c] || "");
        cell.textContent = val;
        if (c === "status" && val) {
          var b = document.createElement("span");
          b.className = "badge " + val;
          b.textContent = val;
          cell.textContent = "";
          cell.appendChild(b);
        }
        if (c === "source_url" && val) {
          var urls = sourceLinks(val);
          if (urls.length) {
            cell.textContent = "";
            urls.forEach(function (url, index) {
              if (index) cell.appendChild(document.createTextNode(" · "));
              var a = document.createElement("a");
              a.href = url;
              a.textContent = urls.length > 1 ? "المصدر " + (index + 1) : "المصدر";
              a.rel = "noopener noreferrer";
              a.target = "_blank";
              cell.appendChild(a);
            });
          }
        }
        cell.setAttribute("data-label", c);
        tr.appendChild(cell);
      });
      frag.appendChild(tr);
    });
    tbody.innerHTML = "";
    tbody.appendChild(frag);
    caption.textContent = (KB._titles && KB._titles[key] ? KB._titles[key] : key) + " — " + shown + " من " + rows.length + " صف";
    count.textContent = "تُعرض " + shown + " صفًا من أصل " + rows.length + ".";
    if (!rows.length) count.textContent = "هذا السجل فارغ أو لم يُنشأ بعد.";
  }

  function debounced() {
    if (timer) clearTimeout(timer);
    timer = setTimeout(render, 150);
  }

  ds.addEventListener("change", render);
  q.addEventListener("input", debounced);
  st.addEventListener("change", render);
  render();
})();
</script>
</body>
</html>
"""

def main() -> int:
    kb = {}
    titles = {}
    built = []
    skipped = []
    for fname, title in REGISTRIES:
        rows = load_csv(DATA / fname)
        if rows is None:
            skipped.append(fname)
            continue
        key = Path(fname).stem
        kb[key] = {"columns": list(rows[0]) if rows else [], "rows": [list(row.values()) for row in rows]}
        titles[key] = title
        built.append(f"{fname} ({len(rows)} صف)")
    kb["_titles"] = titles
    options = "\n".join(
        f'          <option value="{Path(f).stem}">{t}</option>' for f, t in REGISTRIES
    )
    build_date = date.today().isoformat()
    html = (
        TEMPLATE
        .replace("__DATASET_OPTIONS__", options)
        .replace("__DATA_JSON__", json.dumps(kb, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c"))
        .replace("__BUILD_DATE__", build_date)
    )
    OUT.write_text(html, encoding="utf-8")
    print(f"[تم] {OUT}")
    for b in built:
        print(f"  مدمج: {b}")
    for s in skipped:
        print(f"  متخطى (غير موجود): {s}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
