# -*- coding: utf-8 -*-
"""Rebuild INDEX.md by scanning every transcripts/<cat>/*.txt header on disk.

Canonical index builder: works for both short talks (written by build.py) and
long-video per-speaker segments (written directly by split agents). Reads the
fixed header block each .txt carries and regenerates the grouped table.
"""
import os, re, glob

WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, '..', 'transcripts')

CAT_ORDER = ["Лендинги-и-конверсия","Агентский-бизнес","Продажи-и-клиенты","Фриланс-и-продуктивность",
             "Стратегия-и-тренды","Telegram-маркетинг","Личный-бренд-и-контент","Аналитика-и-юнит-экономика",
             "SMM-и-соцсети","Ниши-и-маркетплейсы","Маркировка-и-право"]

FIELD = {
    'title': 'Название:',
    'name':  'Спикер:',
    'role':  'Должность:',
    'date':  'Дата:',
    'cat':   'Категория:',
    'dur':   'Длительность:',
    'url':   'Источник (YouTube):',
}

def parse_header(path):
    h = {}
    with open(path, encoding='utf-8') as f:
        for _ in range(20):
            line = f.readline()
            if not line or line.startswith('='):
                break
            for key, prefix in FIELD.items():
                if line.startswith(prefix):
                    h[key] = line[len(prefix):].strip()
                    break
    return h

items_by_cat = {}
total = 0
for path in glob.glob(os.path.join(OUT, '*', '*.txt')):
    h = parse_header(path)
    if not h.get('title'):
        continue
    cat = h.get('cat') or os.path.basename(os.path.dirname(path))
    rel = os.path.relpath(path, OUT)
    items_by_cat.setdefault(cat, []).append({
        'date': h.get('date', ''),
        'name': h.get('name', '—') or '—',
        'title': h.get('title', ''),
        'url': h.get('url', ''),
        'file': rel,
    })
    total += 1

lines = ["# Индекс расшифровок — выступления спикеров Yagla / Vitamin.tools\n",
         f"Всего расшифровок: **{total}** · выступления 2024+ и посегментные доклады с конференций · "
         f"собрано из субтитров YouTube (без скачивания видео).\n",
         "Каждый файл — расшифровка одного выступления с шапкой (спикер, дата, тема, ссылка).\n"]

seen_cats = [c for c in CAT_ORDER if c in items_by_cat] + \
            [c for c in sorted(items_by_cat) if c not in CAT_ORDER]
for cat in seen_cats:
    items = items_by_cat[cat]
    items.sort(key=lambda x: x['date'], reverse=True)
    lines.append(f"\n## {cat} ({len(items)})\n")
    lines.append("| Дата | Спикер | Тема | Файл | YouTube |")
    lines.append("|------|--------|------|------|---------|")
    for it in items:
        sp = it['name'] or '—'
        yt = f"[▶]({it['url']})" if it['url'] else ''
        lines.append(f"| {it['date']} | {sp} | {it['title']} | [txt]({it['file']}) | {yt} |")
lines.append("")

with open(os.path.join(OUT, '..', 'INDEX.md'), 'w', encoding='utf-8') as o:
    o.write('\n'.join(lines))
print(f"REINDEXED {total} transcripts across {len(seen_cats)} categories")
for cat in seen_cats:
    print(f"  {len(items_by_cat[cat]):>3}  {cat}")
