# سجلات البيانات المرجعية (14 سجلاً)

كل سجل ملف CSV بترميز UTF-8، بفاصلة `,`، والحقول بين علامتي اقتباس عند الحاجة.
**أعمدة مشتركة إلزامية في كل السجلات:**

| العمود | الوصف |
|---|---|
| `id` | المعرف المستقل (بادئة السجل + رقم متسلسل، مثل `FEE-001`) |
| `title` | الاسم/الوصف بالعربية |
| `category` | التصنيف داخل السجل |
| `status` | الحالة النظامية: `ساري` / `ملغى` / `معدل` / `مشروط` / `مستقبل_التطبيق` / `غير_متحقق` |
| `source_name` | اسم المصدر الرسمي |
| `source_url` | رابط المصدر المباشر |
| `access_date` | تاريخ آخر اطلاع/تحقق (YYYY-MM-DD) |
| `notes` | قيود وشروط واستثناءات وإنذارات تحقق |

**قاعدة ذهبية:** أي حقل غير موثق يُترك `غير_متحقق` ولا يُخترع أبداً.
**قاعدة الرسوم:** لا يجوز جمع الرسوم في رقم إجمالي دون بيان شروط انطباق كل رسم — أمثلة الحساب الشرطية في `docs/06-fees.md` فقط وبافتراضات معلنة.

| الملف | السجل | بادئة المعرف |
|---|---|---|
| `01-systems-laws.csv` | الأنظمة واللوائح | `SYS` |
| `02-decisions.csv` | القرارات والتعاميم | `DEC` |
| `03-entities-platforms.csv` | الجهات والمنصات الحكومية | `ENT` |
| `04-services-procedures.csv` | الخدمات والإجراءات | `SRV` |
| `05-fees-costs.csv` | الرسوم والتكاليف | `FEE` |
| `06-visas.csv` | أنواع التأشيرات | `VISA` |
| `07-iqama-types.csv` | أنواع الإقامات | `IQM` |
| `08-professions.csv` | المهن والتصنيفات | `PROF` |
| `09-transfer-conditions.csv` | شروط نقل الخدمات | `TRN` |
| `10-profession-change.csv` | حالات تغيير المهنة | `PRCH` |
| `11-employer-obligations.csv` | التزامات صاحب العمل | `EMP` |
| `12-worker-rights.csv` | حقوق العامل | `WKR` |
| `13-violations-penalties.csv` | المخالفات والغرامات | `VIO` |
| `14-insurance-health.csv` | التأمينات والفحوصات والبطاقات الصحية | `HLTH` |

**أعمدة خاصة موسّعة لكل سجل** موثقة داخل ترويسة الملف نفسه (سطر تعليقي `#` في أول السطر أو في `docs/14-gaps.md`)، وأهمها:
- `05-fees-costs.csv`: `amount`, `currency`, `periodicity` (سنوي/شهري/مرة_واحدة/حسب_الحالة), `varies_by`, `payer` (صاحب_العمل/العامل/الطرفان), `chargeable_to_worker` (نعم/لا/غير_متحقق), `exemptions`, `last_update_date`.
- `02-decisions.csv`: `decision_number`, `issue_date`, `issuer`, `effective_date`, `supersedes`, `worker_impact`, `employer_impact`.
- `09-transfer-conditions.csv`: `scenario`, `from_entity`, `to_entity`, `employer_consent_required`, `worker_consent_required`, `fees`, `new_work_permit`, `iqama_update`, `waiting_period`, `blocking_cases`, `e_procedure`.
