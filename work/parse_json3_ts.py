# -*- coding: utf-8 -*-
"""Parse a json3 ASR subtitle track into flowing text with inline timecode
markers, for splitting long multi-speaker videos.

A marker `[[H:MM:SS | t=SEC]]` is inserted at the start and then whenever
>= INTERVAL seconds of speech have elapsed. A splitting agent uses these to
locate speaker-boundary positions and to build deep-links:
    https://www.youtube.com/watch?v=<id>&t=<SEC>
"""
import json, sys, re

INTERVAL = 30  # seconds between inline timecode markers

def fmt_ts(sec):
    sec = int(sec); h = sec // 3600; m = (sec % 3600) // 60; s = sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def parse_ts(path, interval=INTERVAL):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    events = []  # (tsec, text)
    for ev in data.get('events', []):
        segs = ev.get('segs')
        if not segs:
            continue
        text = ''.join(s.get('utf8', '') for s in segs).replace('\n', ' ').strip()
        if not text:
            continue
        tsec = int(ev.get('tStartMs', 0)) // 1000
        events.append((tsec, text))
    # dedup consecutive identical text (rolling-caption artifact)
    dedup = []
    for tsec, text in events:
        if dedup and dedup[-1][1] == text:
            continue
        dedup.append((tsec, text))
    # One line per marker interval so long transcripts stay navigable
    # (grep/Read by line) instead of collapsing into a single 250KB line —
    # a single-line file caused a split agent to misjudge caption coverage.
    lines = []
    cur = []
    last_marker = None
    for tsec, text in dedup:
        if last_marker is None or tsec - last_marker >= interval:
            if cur:
                lines.append(' '.join(cur))
                cur = []
            cur.append(f"[[{fmt_ts(tsec)} | t={tsec}]]")
            last_marker = tsec
        cur.append(text)
    if cur:
        lines.append(' '.join(cur))
    full = '\n'.join(re.sub(r'\s+', ' ', ln).strip() for ln in lines)
    dur = dedup[-1][0] if dedup else 0
    return full, dur

if __name__ == '__main__':
    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    txt, dur = parse_ts(path)
    if out:
        with open(out, 'w', encoding='utf-8') as o:
            o.write(txt + '\n')
        print(f"WROTE {out}  CHARS={len(txt)}  WORDS={len(txt.split())}  DUR={fmt_ts(dur)}")
    else:
        print(f"CHARS={len(txt)} WORDS={len(txt.split())} DUR={fmt_ts(dur)}")
        print("--- first 1200 ---")
        print(txt[:1200])
        print("--- last 600 ---")
        print(txt[-600:])
