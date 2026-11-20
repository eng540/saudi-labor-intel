#!/usr/bin/env python3
"""Regression checks for the findings corrected on 2026-11-20.
These checks detect known regressions, not the legal validity of all content.
"""
import argparse
import csv
import json
import re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent

def rows(name):
    with (ROOT / 'data' / name).open(encoding='utf-8-sig', newline='') as f:
        return {row['id']: row for row in csv.DictReader(f)}

def check(condition, message):
    if not condition:
        raise AssertionError(message)

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts = {}
        self.html = {}
    def handle_starttag(self, tag, attrs):
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if tag == 'html':
            self.html = dict(attrs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path)
    args = parser.parse_args()
    operations = (ROOT / 'docs/12-operations.md').read_text()
    check('يفقد العامل أجره في 7' not in operations, 'Article 81 reversal returned')
    check('100 ريال/شهر' not in operations, 'Permit annual fee became monthly')
    check('م61/5-6' in operations and 'م64' in operations and 'م65' in operations, 'Article references missing')
    check('1.5×' not in rows('12-worker-rights.csv')['WKR-03']['title'], 'Overtime multiplier oversimplified')
    tech = rows('08-professions.csv')['PROF-004']
    decision = rows('02-decisions.csv')['DEC-029']
    check(tech['status'] == decision['status'] == 'مستقبل_التطبيق', 'Future localization is marked current')
    check(tech['effective_date'] == decision['effective_date'] == '2027-05-09', 'Technical-engineering date disagrees')
    check('400' in rows('05-fees-costs.csv')['FEE-04']['amount'], 'Dependent amount missing')
    check('سداد' in rows('05-fees-costs.csv')['FEE-04']['title'], 'Dependent collection channel missing')
    check(16100 == 2000 + 100 + 9600 + 650 + 3000 + 150 + 600, 'First minimum arithmetic')
    check(19250 == 2000 + 100 + 9600 + 650 + 6000 + 300 + 600, 'First maximum arithmetic')
    check(17250 == 100 + 9600 + 650 + 6000 + 300 + 600, 'Second maximum arithmetic')
    fees = (ROOT / 'docs/06-fees.md').read_text()
    check('16,100–19,250' in fees and '14,100–17,250' in fees, 'Published totals disagree with their assumptions')
    for name in ['docs/06-fees.md', 'docs/16-domestic-workers.md']:
        ids = re.findall(r'^\| ((?:DOM|EX)-\d+) \|', (ROOT / name).read_text().split('## 8) جدول المصادر')[0], re.M)
        check(len(ids) == len(set(ids)), f'Duplicate primary row IDs in {name}')
    prof = (ROOT / 'docs/09-professions.md').read_text()
    headings = re.findall(r'^### \[(PROF-\d+)\]', prof, re.M)
    check(len(headings) == len(set(headings)), 'Duplicate profession heading IDs')
    check('/.../' not in prof, 'Truncated source URL returned')
    for folder in ['docs', 'cases']:
        for path in (ROOT / folder).glob('*.md'):
            text = path.read_text().splitlines()
            for i, line in enumerate(text):
                if line.startswith('|') and i and not text[i-1].startswith('|'):
                    check(not text[i-1].strip(), f'Missing table boundary: {path.name}:{i+1}')
    html = (ROOT / 'search.html').read_text()
    kb = json.loads(re.search(r'<script id="kb-data" type="application/json">(.*?)</script>', html, re.S).group(1))
    for path in (ROOT / 'data').glob('*.csv'):
        with path.open(encoding='utf-8-sig', newline='') as f:
            dataset = kb[path.stem]
            unpacked = [dict(zip(dataset['columns'], values)) for values in dataset['rows']]
            check(unpacked == list(csv.DictReader(f)), f'Stale search data: {path.name}')
    if args.site:
        for name in ['docs/12-operations.html', 'docs/05-iqama-lifecycle.html', 'docs/10-renewal-exit.html']:
            text = (args.site / name).read_text()
            tags = Tags(); tags.feed(text)
            check(tags.counts.get('table', 0) > 0, f'Jekyll did not render tables: {name}')
            check(tags.html.get('dir') == 'rtl', f'Missing RTL: {name}')
        for source in (ROOT / 'flows').glob('0*.md'):
            built = (args.site / source.with_suffix('.html').relative_to(ROOT)).read_text()
            check('diagrams.js' in built and 'language-mermaid' in built, f'Missing diagram setup: {source.name}')
    print('PASS: audited regressions, table boundaries, unique IDs, and search-data parity')

if __name__ == '__main__':
    main()
