#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAUDI-LABOR-INTEL-001 — توليد سجلّي data/02-decisions.csv و data/05-fees-costs.csv
من الجداول المنظمة في docs/13-decisions-archive.md و docs/06-fees.md حصراً.
- لا يخترع أي رقم: كل القيم منقول حرفياً من أعمدة الجدول.
- EX-xx تُعاد تسميتها FEE-EX-xx (بادئة السجل إلزامية في المدقق) مع حفظ المعرف الأصلي في notes.
- docs/13 و docs/06 يحويان جداول متعددة بأعمدة مختلفة؛ الترويسة تحدد خريطة الأعمدة لكل جدول.
الاستخدام:  python3 tools/generate_fee_decision_csvs.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"
ACCESS_DATE = "2026-11-17"

DEC_COLS = ["id", "title", "category", "status", "source_name", "source_url", "access_date",
            "notes", "decision_number", "issue_date", "issuer", "effective_date",
            "supersedes", "worker_impact", "employer_impact"]

FEE_COLS = ["id", "title", "category", "status", "source_name", "source_url", "access_date",
            "notes", "amount", "currency", "periodicity", "varies_by", "payer",
            "chargeable_to_worker", "exemptions", "last_update_date"]


def parse_tables(md_path: Path):
    """يفكك الملف إلى جداول: كل جدول = (قائمة الترويسة، صفوف البيانات)."""
    tables = []
    current_header = None
    current_rows = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):  # فاصل الترويسة
            continue
        if cells and cells[0] in ("المعرف",):  # ترويسة جدول جديد
            if current_header:
                tables.append((current_header, current_rows))
            current_header, current_rows = cells, []
            continue
        if current_header is not None:
            current_rows.append(cells)
    if current_header:
        tables.append((current_header, current_rows))
    return tables


def strip_md(text: str) -> str:
    return text.replace("**", "").strip()


def extract_url(text: str) -> str:
    m = re.search(r"https?://[^\s\)\]]+", text)
    return m.group(0) if m else ""


# ---------------------------------------------------------------- 02-decisions
def dec_status(text: str) -> str:
    t = strip_md(text)
    if "ملغى" in t:
        return "ملغى"
    if "معدل" in t or "مستبدل" in t:
        return "معدل"
    if "مستقبل" in t:
        return "مستقبل_التطبيق"
    if "ساري" in t:
        return "ساري"
    if "غير متحقق" in t:
        return "غير_متحقق"
    return "مشروط"


def build_decisions():
    out = []
    for header, rows in parse_tables(DOCS / "13-decisions-archive.md"):
        if "الوثيقة ورقمها" in header:                      # الجداول الرئيسية (9 أعمدة)
            i = {name: n for n, name in enumerate(header)}
            for c in rows:
                if len(c) < len(header) or not c[0].startswith("DEC-"):
                    continue
                doc_ref = strip_md(c[i["الوثيقة ورقمها"]])
                issuer = strip_md(c[i["الجهة"]])
                content = strip_md(c[i["المضمون والحالة"]])
                source = strip_md(c[i["المصدر"]])
                viewed = strip_md(c[i["الاطلاع"]])
                m = re.search(r"(م/\d+|قرار رقم \d+|قرار \d+|رقم \d+)", doc_ref)
                out.append({
                    "id": c[0], "title": doc_ref,
                    "category": ("مرسوم_ملكي" if "مرسوم" in issuer
                                 else "لائحة" if "لائحة" in issuer or "لائحة" in content
                                 else "قرار_وزاري" if "وزارة" in issuer or "وزاري" in issuer
                                 else "قرار_مجلس_وزراء"),
                    "status": dec_status(content),
                    "source_name": source or "docs/13-decisions-archive.md",
                    "source_url": extract_url(source) or "docs/13-decisions-archive.md",
                    "access_date": (viewed if re.match(r"\d{4}-\d{2}-\d{2}", viewed) else ACCESS_DATE),
                    "notes": content,
                    "decision_number": m.group(0) if m else "",
                    "issue_date": strip_md(c[i["تاريخ الصدور"]]),
                    "issuer": issuer,
                    "effective_date": strip_md(c[i["بدء التطبيق"]]),
                    "supersedes": "",
                    "worker_impact": strip_md(c[i["الأثر على العامل / صاحب العمل"]]),
                    "employer_impact": "",
                })
        elif "الموضوع والفرضية" in header:                   # جدول الفرضيات غير المتحققة (4 أعمدة)
            for c in rows:
                if len(c) < 4 or not c[0].startswith("DEC-"):
                    continue
                out.append({
                    "id": c[0],
                    "title": strip_md(c[1]),
                    "category": "فرضية_غير_متحققة",
                    "status": "غير_متحقق",
                    "source_name": "docs/13-decisions-archive.md — جدول الفرضيات غير المتحققة",
                    "source_url": "docs/13-decisions-archive.md",
                    "access_date": ACCESS_DATE,
                    "notes": "نتيجة التحقق: " + strip_md(c[2]) + " — الخطوة المطلوبة: " + strip_md(c[3]),
                    "decision_number": "", "issue_date": "", "issuer": "",
                    "effective_date": "", "supersedes": "",
                    "worker_impact": "", "employer_impact": "",
                })
    with (DATA / "02-decisions.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=DEC_COLS)
        w.writeheader()
        w.writerows(out)
    return len(out)


# -------------------------------------------------------------- 05-fees-costs
def fee_status(text: str) -> str:
    t = strip_md(text)
    official = ("رسمي متحقق" in t) or ("نقل موثوق" in t)
    unverified = ("غير متحقق" in t) or ("فرضية" in t) or ("معلق" in t)
    if official and unverified:
        return "مشروط"
    if unverified:
        return "غير_متحقق"
    if official:
        return "ساري"
    return "مشروط"  # ثانوي/ناقل وغير ذلك


def fee_category(title: str, amount: str, is_ex: bool) -> str:
    t = title + " " + amount
    if is_ex:
        return "إعفاء"
    if any(k in t for k in ("غرامة", "مخالفة", "عقوبة", "جزاء")):
        return "غرامة"
    if any(k in t for k in ("المقابل المالي", "اشتراك", "تأمين", "الأخطار", "قسط")):
        return "تكلفة_إلزامية"
    return "رسم_حكومي"


def fee_row(rid, title, amount, basis, periodic, payer, state, extra_note=""):
    is_ex = rid.startswith("EX-")
    # FEE-EX-xx حتى لا تتصادم مع FEE-01..06 الأصلية في إزالة التكرار
    out_id = ("FEE-EX-" + rid.split("-", 1)[1]) if is_ex else rid
    worker_pays = ("خارج م40" in payer) or payer.strip().startswith("العامل")
    employer_pays = ("صاحب العمل" in payer) or ("المنشأة" in payer) or ("المستقبل" in payer)
    notes = strip_md(state)
    if is_ex:
        notes = f"المعرف الأصلي في الدليل: {rid}. " + notes
    if extra_note:
        notes = (notes + " — " + extra_note).strip(" —")
    return {
        "id": out_id,
        "title": strip_md(title),
        "category": fee_category(strip_md(title), strip_md(amount), is_ex),
        "status": fee_status(state),
        "source_name": strip_md(basis) or "docs/06-fees.md",
        "source_url": "docs/06-fees.md",
        "access_date": ACCESS_DATE,
        "notes": notes,
        "amount": strip_md(amount),
        "currency": "ريال سعودي" if "ريال" in amount else "",
        "periodicity": strip_md(periodic),
        "varies_by": ("حسب النطاق/الشريحة" if ("نطاق" in amount or "شريحة" in amount) else ""),
        "payer": strip_md(payer),
        "chargeable_to_worker": ("نعم" if worker_pays else "لا" if employer_pays else "غير_متحقق"),
        "exemptions": (strip_md(amount) if is_ex else ""),
        "last_update_date": "",
    }


def build_fees():
    out = []
    for header, rows in parse_tables(DOCS / "06-fees.md"):
        h = {name: n for n, name in enumerate(header)}
        n = len(header)
        for c in rows:
            if len(c) < n or not (c[0].startswith("FEE-") or c[0].startswith("EX-")):
                continue
            if "الدورية" in h and "من يتحمل" in "|".join(header):
                r = fee_row(c[0], c[h["البند"]], c[h.get("القيمة الحالية", 2) if "القيمة الحالية" in h else h["القيمة/النطاق"]],
                            c[h["الأساس/السند"] if "الأساس/السند" in h else h["الأساس"]],
                            c[h["الدورية"]], c[h["من يتحمل نظاماً"] if "من يتحمل نظاماً" in h else h["من يتحمل"]],
                            c[h["الحالة"]])
            elif "الأساس/السند" in h:                        # جدول الغرامات (5 أعمدة)
                r = fee_row(c[0], c[h["البند"]], c[h["القيمة"]], c[h["الأساس/السند"]], "", "", c[h["الحالة"]])
            elif "الفئة" in h:                               # جدول الإعفاءات EX (5 أعمدة)
                r = fee_row(c[0], c[h["الفئة"]], c[h["الحكم"]], c[h["السند"]], "", "", c[h["الحالة"]])
            else:                                            # جدول مختصر (4 أعمدة)
                r = fee_row(c[0], c[h["البند"]], c[h["القيمة/النطاق"]], "", "", "", c[h["الحالة"]])
            out.append(r)
    # إزالة التكرارات المحتملة مع الحفاظ على الترتيب
    seen, uniq = set(), []
    for r in out:
        if r["id"] not in seen:
            seen.add(r["id"])
            uniq.append(r)
    with (DATA / "05-fees-costs.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FEE_COLS)
        w.writeheader()
        w.writerows(uniq)
    return len(uniq)


if __name__ == "__main__":
    print(f"02-decisions.csv: {build_decisions()} صف")
    print(f"05-fees-costs.csv: {build_fees()} صف")
