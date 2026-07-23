# -*- coding: utf-8 -*-
"""Build per-speaker transcript files from long-video split maps.

Deterministic slicer. Inputs:
  work/ts/<id>.txt        — timestamped transcript ([[H:MM:SS | t=SEC]] markers)
  work/splits/<id>.json   — boundary map produced by a split agent:
      {"video_id","date","conf_title","segments":[
          {"start_t":int,"end_t":int|null,"speaker":str,"role":str,
           "topic":str,"category":str,"stale":str|null}, ...]}
  work/long_meta.txt      — id|upload_date|duration|title (for fallback title/date)

Output: transcripts/<Категория>/<YYYY-MM-DD>__<slug>.txt with a header carrying
the segment timecode range + a &t=<sec> deep-link + parent conference + any
staleness flag. Run reindex.py afterwards to refresh INDEX.md.
"""
import os, re, json, glob, sys

WORK = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(WORK, 'ts')
SPLITS = os.path.join(WORK, 'splits')
OUT = os.path.join(WORK, '..', 'transcripts')
MARKER = re.compile(r'\[\[\s*[0-9:]+\s*\|\s*t=(\d+)\s*\]\]')

def fmt_ts(sec):
    sec = int(sec); h = sec // 3600; m = (sec % 3600) // 60; s = sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def slugify(title):
    s = re.sub(r'[\\/:*?"<>|«»""–—]', '', title.strip())
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_.')
    return s[:80] or 'segment'

def load_meta():
    meta = {}
    p = os.path.join(WORK, 'long_meta.txt')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            parts = line.rstrip('\n').split('|', 3)
            if len(parts) == 4:
                meta[parts[0]] = dict(date=parts[1], dur=int(parts[2]), title=parts[3])
    return meta

def fmt_date(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 and d.isdigit() else d

def chunks_with_time(ts_text):
    """Return list of (t_sec, text) chunks split on inline markers."""
    out = []
    pos = 0
    cur_t = 0
    for m in MARKER.finditer(ts_text):
        seg = ts_text[pos:m.start()].strip()
        if seg:
            out.append((cur_t, seg))
        cur_t = int(m.group(1))
        pos = m.end()
    tail = ts_text[pos:].strip()
    if tail:
        out.append((cur_t, tail))
    return out

def slice_text(chunks, start_t, end_t):
    end_t = end_t if end_t is not None else 10**9
    picked = [txt for (t, txt) in chunks if start_t <= t < end_t]
    return re.sub(r'\s+', ' ', ' '.join(picked)).strip()

def is_long_segment(path):
    """A file written by this script carries a 'Конференция:' header line;
    short talks (build.py) never do. Used to safely clear prior output so
    re-runs stay idempotent instead of piling up _2/_3 duplicates."""
    try:
        with open(path, encoding='utf-8') as f:
            for _ in range(20):
                line = f.readline()
                if not line or line.startswith('='):
                    return False
                if line.startswith('Конференция:'):
                    return True
    except OSError:
        return False
    return False

def clear_prior_output():
    n = 0
    for path in glob.glob(os.path.join(OUT, '*', '*.txt')):
        if is_long_segment(path):
            os.remove(path); n += 1
    if n:
        print(f"cleared {n} prior long-segment files")

def main():
    meta = load_meta()
    clear_prior_output()
    written, used_names = [], set()
    for jpath in sorted(glob.glob(os.path.join(SPLITS, '*.json'))):
        data = json.load(open(jpath, encoding='utf-8'))
        vid = data.get('video_id') or os.path.splitext(os.path.basename(jpath))[0]
        m = meta.get(vid, {})
        date = fmt_date(data.get('date') or m.get('date', ''))
        conf = data.get('conf_title') or m.get('title', '')
        tspath = os.path.join(TS, f'{vid}.txt')
        if not os.path.exists(tspath):
            print(f"SKIP {vid}: no ts transcript"); continue
        chunks = chunks_with_time(open(tspath, encoding='utf-8').read())
        for seg in data.get('segments', []):
            if seg.get('drop'):
                continue  # segment dropped by user review (stale ad-cabinet walkthrough)
            start_t = int(seg.get('start_t', 0))
            end_t = seg.get('end_t')
            text = slice_text(chunks, start_t, end_t)
            if len(text) < 150:
                print(f"  short segment {vid} @{start_t}: {len(text)} chars — skipped"); continue
            cat = seg.get('category') or 'Стратегия-и-тренды'
            topic = (seg.get('topic') or 'Без названия').strip()
            speaker = (seg.get('speaker') or '—').strip() or '—'
            role = (seg.get('role') or '—').strip() or '—'
            stale = seg.get('stale')
            url = f"https://www.youtube.com/watch?v={vid}&t={start_t}"
            tc = fmt_ts(start_t) + (f"–{fmt_ts(end_t)}" if end_t else "")
            dur_txt = f"~{max(1, round(((end_t or start_t) - start_t)/60))} мин" if end_t else "—"
            catdir = os.path.join(OUT, cat)
            os.makedirs(catdir, exist_ok=True)
            base = f"{date}__{slugify(topic)}"
            fname = base + ".txt"
            i = 2
            while (cat, fname) in used_names or os.path.exists(os.path.join(catdir, fname)):
                fname = f"{base}_{i}.txt"; i += 1
            used_names.add((cat, fname))
            header = (
                f"Название: {topic}\n"
                f"Спикер: {speaker}\n"
                f"Должность: {role}\n"
                f"Дата: {date}\n"
                f"Категория: {cat}\n"
                f"Длительность: {dur_txt}\n"
                f"Тайм-код: {tc}\n"
                f"Источник (YouTube): {url}\n"
                f"Конференция: {conf}\n"
                f"Устаревание: {stale if stale else '—'}\n"
                f"Канал: Yagla / Vitamin.tools (@YaglaRuOnline)\n"
                f"{'=' * 60}\n\n"
            )
            with open(os.path.join(catdir, fname), 'w', encoding='utf-8') as o:
                o.write(header + text + '\n')
            written.append((cat, fname, speaker, stale))
    print(f"\nWROTE {len(written)} segment files")
    stale_n = sum(1 for w in written if w[3])
    print(f"  flagged stale: {stale_n}")

if __name__ == '__main__':
    main()
