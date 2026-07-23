# -*- coding: utf-8 -*-
"""Robust, resumable subtitle+description fetcher (no video download).
Per-video timeout so one hanging video can't stall the batch.
Re-run safely: already-fetched videos are skipped."""
import os, subprocess, sys, glob

WORK = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(WORK, 'raw')
os.makedirs(RAW, exist_ok=True)

ids = []
with open(os.path.join(WORK, 'keep.tsv'), encoding='utf-8') as f:
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3:
            ids.append(p[2])

PER_VIDEO_TIMEOUT = 90
done, skipped, failed = [], [], []

for i, vid in enumerate(ids, 1):
    have_sub = glob.glob(os.path.join(RAW, f'{vid}.ru*.json3'))
    have_desc = os.path.exists(os.path.join(RAW, f'{vid}.description'))
    if have_sub and have_desc:
        skipped.append(vid)
        print(f"[{i}/{len(ids)}] SKIP {vid}", flush=True)
        continue
    cmd = [
        'yt-dlp', '--skip-download', '--write-auto-subs',
        '--sub-langs', 'ru-orig,ru', '--sub-format', 'json3',
        '--write-description', '--no-warnings', '--no-progress',
        '--socket-timeout', '20', '--retries', '2',
        '-o', os.path.join(RAW, '%(id)s.%(ext)s'),
        f'https://www.youtube.com/watch?v={vid}',
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_VIDEO_TIMEOUT)
        ok = bool(glob.glob(os.path.join(RAW, f'{vid}.ru*.json3')))
        if ok:
            done.append(vid)
            print(f"[{i}/{len(ids)}] OK   {vid}", flush=True)
        else:
            failed.append((vid, (r.stderr or r.stdout or '').strip()[-160:]))
            print(f"[{i}/{len(ids)}] FAIL {vid} (no subs written)", flush=True)
    except subprocess.TimeoutExpired:
        failed.append((vid, 'TIMEOUT'))
        print(f"[{i}/{len(ids)}] TIMEOUT {vid}", flush=True)
    except Exception as e:
        failed.append((vid, repr(e)[:160]))
        print(f"[{i}/{len(ids)}] ERROR {vid}: {e}", flush=True)

print(f"\nSUMMARY done={len(done)} skipped={len(skipped)} failed={len(failed)} total={len(ids)}")
if failed:
    print("FAILED:")
    for v, why in failed:
        print(f"   {v}  {why}")
