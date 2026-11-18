#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAUDI-LABOR-INTEL-001 — أداة التحقق من سلامة سجلات البيانات (14 CSV).
الاستخدام:  python3 tools/validate_csv.py
ما تفعله:
  - تتحقق من وجود ملفات السجلات الـ14 في data/
  - تتحقق من الأعمدة المشتركة الإلزامية في كل سجل
  - تتحقق من مطابقة بادئة المعرف (id) لبادئة السجل
  - تتحقق من انتماء قيم status للقيم المسموحة
  - تطبع ملخصاً لكل سجل (عدد الصفوف، عدد القيم "غير_متحقق")
"""
import csv
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

REQUIRED = ["id", "title", "category", "status", "source_name", "source_url", "access_date", "notes"]
VALID_STATUS = {"ساري", "ملغى", "معدل", "مشروط", "مستقبل_التطبيق", "غير_متحقق"}

PREFIXES = {
    "01-systems-laws.csv": "SYS",
    "02-decisions.csv": "DEC",
    "03-entities-platforms.csv": "ENT",
    "04-services-procedures.csv": "SRV",
    "05-fees-costs.csv": "FEE",
    "06-visas.csv": "VISA",
    "07-iqama-types.csv": "IQM",
    "08-professions.csv": "PROF",
    "09-transfer-conditions.csv": "TRN",
    "10-profession-change.csv": "PRCH",
    "11-employer-obligations.csv": "EMP",
    "12-worker-rights.csv": "WKR",
    "13-violations-penalties.csv": "VIO",
    "14-insurance-health.csv": "HLTH",
}

def main() -> int:
    if not DATA.is_dir():
        print(f"[خطأ] مجلد data غير موجود: {DATA}")
        return 1
    errors = 0
    total_rows = 0
    total_unknown = 0
    for fname, prefix in PREFIXES.items():
        fpath = DATA / fname
        if not fpath.exists():
            print(f"[ناقص] {fname} (سجل {prefix}) — لم يُنشأ بعد")
            errors += 1
            continue
        with fpath.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            cols = reader.fieldnames or []
            missing = [c for c in REQUIRED if c not in cols]
            if missing:
                print(f"[أعمدة ناقصة] {fname}: {missing}")
                errors += 1
            rows = 0
            unknown = 0
            seen_ids = set()
            for row in reader:
                rows += 1
                rid = (row.get("id") or "").strip()
                if not rid.startswith(prefix):
                    print(f"[معرف خاطئ] {fname} سطر {rows}: {rid} (المتوقع بادئة {prefix})")
                    errors += 1
                if rid in seen_ids:
                    print(f"[معرف مكرر] {fname}: {rid}")
                    errors += 1
                seen_ids.add(rid)
                status = (row.get("status") or "").strip()
                if status and status not in VALID_STATUS:
                    print(f"[حالة غير معروفة] {fname} {rid}: {status}")
                    errors += 1
                if status == "غير_متحقق" or "غير متحقق" in (row.get("notes") or ""):
                    unknown += 1
            total_rows += rows
            total_unknown += unknown
            print(f"[سجل] {fname}: {rows} صفوف، {unknown} موسومة غير متحققة")
    print("-" * 60)
    print(f"الإجمالي: {total_rows} صفوف، {total_unknown} غير متحققة، {errors} خطأ")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
