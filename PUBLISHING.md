# دليل نشر المستودع على GitHub

المستودع جاهز محلياً على: `/root/DSH_Projects/saudi-labor-intel` (فرع `main`، محفوظات git كاملة).
هناك طريقتان للنشر — اختر ما يناسبك:

## الطريقة 1 — الرفع اليدوي من المتصفح (بدون أدوات، 5 دقائق)

1. سجّل الدخول إلى github.com ← زر **New repository**.
2. الاسم المقترح: `saudi-labor-intel` · الوصف: «قاعدة معرفية موثقة لمنظومة الإقامة والعمل والاستقدام في السعودية (SAUDI-LABOR-INTEL-001)» · Public أو Private حسب رغبتك · **دون** تهيئة README (لأنه موجود لدينا).
3. في صفحة المستودع الفارغ: **uploading an existing file** (رابط الرفع اليدوي).
4. اسحب محتويات المجلد المحلي (كافة الملفات والمجلدات، **دون** مجلد `.git`).
5. Commit message: `SAUDI-LABOR-INTEL-001 — الإصدار الأول للقاعدة المعرفية` ثم **Commit changes**.
6. لتشغيل صفحة البحث: Settings ← Pages ← Source: Deploy from a branch ← Branch: main / (root) ← Save — ستُتاح `search.html` على رابط GitHub Pages خلال دقائق.

> ملاحظة: سطر الأوامر أدق لرفع مجلدات متعددة؛ إن كنت مرتاحاً للطرفية استخدم الطريقة 2.

## الطريقة 2 — من سطر الأوامر (git + رمز وصول PAT)

1. أنشئ رمز وصول: github.com ← Settings ← Developer settings ← **Personal access tokens (classic)** ← Generate new token ← علّم `repo` فقط.
2. ثم نفّذ من جهازك:

```bash
cd /path/to/saudi-labor-intel            # مجلد المستودع المحلي
git remote add origin https://github.com/<اسم-حسابك>/saudi-labor-intel.git
git push -u origin main
```

3. عند طلب كلمة المرور، الصق الرمز (PAT) بدلها.

## بعد النشر (اختياري لكن مُستحسن)

- **Topics** للمستودع: `saudi-arabia` `labor-law` `iqama` `work-visa` `hrsd` `qiwa` `expat-workers` `saudization`
- **GitHub Pages** لتفعيل صفحة البحث (كما في الطريقة 1، خطوة 6).
- **التحديث المستقبلي:** حدّث السجلات في `data/*.csv` ثم نفّذ `python3 tools/build_search_page.py` لتحديث `search.html`، و`python3 tools/validate_csv.py` قبل كل commit، ثم push.
- **قاعدة التحديث المنهجية:** أي قرار جديد يُضاف إلى `docs/13-decisions-archive.md` بسجل DEC جديد بحقوله الثمانية كاملة + صف مطابق في `data/02-decisions.csv`.

## ملاحظات أمان

- لا ترفع أبداً رموز وصول أو بيانات دخول داخل المستودع (موجود `.gitignore` للمخرجات المؤقتة).
- المحتوى مرجعي بحثي مفتوح؛ النصوص النظامية والقرارات ملك جهاتها وذُكرت بروابطها الأصلية.
