# -*- coding: utf-8 -*-
import os, re, json, sys

WORK = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(WORK, 'raw')
OUT = os.path.join(WORK, '..', 'transcripts')

def parse_json3(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    lines = []
    for ev in data.get('events', []):
        segs = ev.get('segs')
        if not segs:
            continue
        text = ''.join(s.get('utf8', '') for s in segs).replace('\n', ' ').strip()
        if text:
            lines.append(text)
    out = []
    for ln in lines:
        if out and out[-1] == ln:
            continue
        out.append(ln)
    return re.sub(r'\s+', ' ', ' '.join(out)).strip()

def extract_speaker(desc):
    for pat in (r'Рассказыва(?:ет|ют)\s+(.+)', r'Спикер[:\s—–\-]+(.+)', r'Ведущий[:\s—–\-]+(.+)'):
        m = re.search(pat, desc)
        if m:
            rest = m.group(1).strip()
            parts = re.split(r'\s+[—–]\s+|\s+-\s+|,\s+', rest, maxsplit=1)
            def clean(s):
                return s.replace('«', '').replace('»', '').replace('"', '').strip(' .,')
            name = clean(parts[0])
            role = clean(parts[1]) if len(parts) > 1 else ''
            return name, role
    return '', ''

def slugify(title):
    s = title.strip()
    s = re.sub(r'[\\/:*?"<>|«»"–—]', '', s)
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_.')
    return s[:90]

def fmt_dur(sec):
    sec = int(sec); h = sec // 3600; m = (sec % 3600) // 60; s = sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def fmt_date(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d

rows = []
with open(os.path.join(WORK, 'keep.tsv'), encoding='utf-8') as f:
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < 6:
            continue
        rows.append(dict(cat=p[0], date=p[1], vid=p[2], dur=p[3], flag=p[4], title=p[5]))

no_subs, no_speaker, built = [], [], []
index = {}  # cat -> list of dicts

for r in rows:
    vid = r['vid']
    sub = os.path.join(RAW, f'{vid}.ru-orig.json3')
    if not os.path.exists(sub):
        sub = os.path.join(RAW, f'{vid}.ru.json3')
    if not os.path.exists(sub):
        no_subs.append((vid, r['title']))
        continue
    try:
        text = parse_json3(sub)
    except Exception as e:
        # file may still be mid-write by the fetcher; retry next build pass
        no_subs.append((vid, r['title'] + f' [parse-retry:{type(e).__name__}]'))
        continue
    if len(text) < 200:
        no_subs.append((vid, r['title'] + f' [short:{len(text)}]'))
        continue
    descpath = os.path.join(RAW, f'{vid}.description')
    desc = open(descpath, encoding='utf-8').read() if os.path.exists(descpath) else ''
    name, role = extract_speaker(desc)
    if not name:
        no_speaker.append((vid, r['title']))
    url = f'https://www.youtube.com/watch?v={vid}'
    date = fmt_date(r['date'])
    catdir = os.path.join(OUT, r['cat'])
    os.makedirs(catdir, exist_ok=True)
    fname = f"{date}__{slugify(r['title'])}.txt"
    header = (
        f"Название: {r['title']}\n"
        f"Спикер: {name or '—'}\n"
        f"Должность: {role or '—'}\n"
        f"Дата: {date}\n"
        f"Категория: {r['cat']}\n"
        f"Длительность: {fmt_dur(r['dur'])}\n"
        f"Источник (YouTube): {url}\n"
        f"Канал: Yagla / Vitamin.tools (@YaglaRuOnline)\n"
        f"{'=' * 60}\n\n"
    )
    with open(os.path.join(catdir, fname), 'w', encoding='utf-8') as o:
        o.write(header + text + '\n')
    built.append(vid)
    index.setdefault(r['cat'], []).append(dict(date=date, name=name, role=role, title=r['title'], url=url, file=f"{r['cat']}/{fname}", chars=len(text)))

# INDEX.md
CAT_ORDER = ["Лендинги-и-конверсия","Агентский-бизнес","Продажи-и-клиенты","Фриланс-и-продуктивность",
             "Стратегия-и-тренды","Telegram-маркетинг","Личный-бренд-и-контент","Аналитика-и-юнит-экономика",
             "SMM-и-соцсети","Ниши-и-маркетплейсы","Маркировка-и-право"]
lines = ["# Индекс расшифровок — выступления спикеров Yagla / Vitamin.tools\n",
         f"Всего расшифровок: **{len(built)}** · только выступления 2024+ · собрано из субтитров YouTube (без скачивания видео).\n",
         "Каждый файл — расшифровка одного выступления с шапкой (спикер, дата, тема, ссылка).\n"]
for cat in CAT_ORDER:
    items = index.get(cat)
    if not items:
        continue
    items.sort(key=lambda x: x['date'], reverse=True)
    lines.append(f"\n## {cat} ({len(items)})\n")
    lines.append("| Дата | Спикер | Тема | Файл | YouTube |")
    lines.append("|------|--------|------|------|---------|")
    for it in items:
        sp = it['name'] or '—'
        lines.append(f"| {it['date']} | {sp} | {it['title']} | [txt]({it['file']}) | [▶]({it['url']}) |")
lines.append("")
with open(os.path.join(OUT, '..', 'INDEX.md'), 'w', encoding='utf-8') as o:
    o.write('\n'.join(lines))

print(f"BUILT={len(built)}  NO_SUBS={len(no_subs)}  NO_SPEAKER={len(no_speaker)}")
if no_subs:
    print("\n-- NO SUBS --")
    for v, t in no_subs: print(f"   {v}  {t}")
if no_speaker:
    print("\n-- NO SPEAKER (description had no recognizable pattern) --")
    for v, t in no_speaker: print(f"   {v}  {t}")
