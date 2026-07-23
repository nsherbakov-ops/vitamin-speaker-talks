# -*- coding: utf-8 -*-
import os
PYTHONUTF8=1

# DROP: id -> reason group (all are 2024 platform-tactical ad/traffic content that has changed)
drop = {}
g_ctx = "Контекст/Директ/РСЯ 2024 — механика/интерфейс изменились"
g_vk  = "ВК-таргет 2024 — настройки платформы изменились"
g_tgt = "Таргет/медиабаинг 2024 — тактика устарела"
g_sev = "Посевы 2024 — кейсы/цифры устарели"
g_tga = "Telegram Ads/таргет 2024 — инструмент изменился"

for i in "EhF_DIMGi8g 6f_Z-W9RfyA cf7I3AUUYv4 ma0dovnmqo0 3TnVrod9DAI Ky2O5D_iciQ YZz4ZouzdYk QRjE1b7LTsA 2OblHx_i0Mg -BIv1gOBVUM UeRcvlp_pyk qeNmS95ziS0 t0lrSUvJHiU pwFjyAOYwNg bSJyMavS4aM WfDSw8nQ0Ug 2RFgNGX2rvo cngY5yoh7F4 rPiAMqmqSjg aP6ouFKgcac AgmnNH3t3VY _qXDuXcZX2E _U7ZePr1EME oMecBb1xQts wsI-ZQDvKs4 IJMI6SjFgIY".split(): drop[i]=g_ctx
for i in "n3zLehLVJKM NOm0XsXO_Ic 3V10AjEnQ94 V38vXIGlluc bP2mLtFDMLI".split(): drop[i]=g_vk
for i in "kj_nGB_jotI sePoPnrRph0 qumr0SclUNc xqdmeBrjnT4 D1bB38Auzt4 n42vDiM7tEc".split(): drop[i]=g_tgt
for i in "MLZnIIpMeuU 4fcXsf85xN8 q7NOPP39xB0 glqzdrF5NV0 WxAgdbVQAFI".split(): drop[i]=g_sev
for i in "igbxQYLnSHI g4lC-xkYpU4 pzIx5x4p9Mw YNN_qs00GSA".split(): drop[i]=g_tga

# KEEP: id -> category
cat = {}
def add(c, ids):
    for i in ids.split(): cat[i]=c
add("Агентский-бизнес", "KG9uVaLeteY tkC6wOs4Gy8 RLvKEmw7W4Y jzyJXxG4WhE 4eHOTJer388 YU0qEwqQxyw oLgcpVtviio vMydg54nxhQ 6pGQP-8Ks1E ZtPitYZo7z4 ueUn-Drl198 jhoqYjrisE8 PjrJ0yR-HWA B3DAqchkWng CJXL2NRsuXg 3iwJHfWuhWE agX2SaBknMk 9sbwQzdNY0A 9a78LSsp690")
add("Продажи-и-клиенты", "a7kpxcY6Tto EM554kBUVEc Rc5h7g9I_M0 izZkBPaBQws XxVEsa26eXY Rnto-JIx6xQ 9U9nth66is8 pwymamlDXTg bj5IEbwr3r8 cI1XuS5Jq_k x3UmBi6j9rE dr4shc23jSU HHWGI1KkWFA 1SFpbBJ5D-Y MRrplIeMLiQ cB9p3-WVpkk 44nW4TGhv34 01bU4XAXJBM KlXScP6fzUk")
add("Фриланс-и-продуктивность", "WNH6dfx4Pwg FasP03q_6uU S8hRAwONACY TWyk3aRehMA FqYD-RJ1Ix0 Cei8hrv3Y_Y ct1rqfwj4IM CX6s6FG-gso 7iYXIP4uZW4 snJ1ELgJHWM pVNM5Nue8oM MCctW6fCkgQ Vs1wE1QXfSU")
add("Личный-бренд-и-контент", "FpVmbTRitww H8AAoAKTZ0A nYgGw_RDNC4 crHi9ZZA9Sg gPW5mfcs8pU YYXo7uUkiEo oJ_mRuuBvhY")
add("Лендинги-и-конверсия", "ZMJubooJHTA 7vCDb-y3DxA w-oRENC9aqg aFAeCAJ8T-8 OXc01ViSHRQ 71M5QK65m_A lbTVad-4Kwc ns3cq4jaHxg dso5bT_rZ2I LO1CEY5akW0 KXaQ5woJgBQ Ereqn0A5APk JtvKLi5K7QY qrE9ntHkAOQ vTl1NDAo3uE OzuVlUCkL8k TjBhS-75NP8 -UWBlPpXroU ulKgsBBfjc4 nHyTC5f1It0 uqECb6txp7c")
add("Telegram-маркетинг", "zm2lYY22jUM 8WYvpQ1yQqI R7PT0RfMGw0 wpV0IITFb8A lW5V8IwQdU8 9_b-4fGlc2Y GflPuM3Zddk FZXqhrUVHTY hHR-zZnZMqY")
add("Аналитика-и-юнит-экономика", "O5TMzNqM7ts Gqb8EdVlt5A Yu59CENRKd0 ulKgsBBfjc4x")  # placeholder guard
add("SMM-и-соцсети", "RvCvtGM7VWE 32kw2oB5S3k RXP9_F7RJTI")
add("Стратегия-и-тренды", "zd2W3KQzKHs ovR3Xp4wmM4 thmCYeyc1Zc ETW3X7AoduY EFYd2os0w_U r-yOrVGFTsg RC3e2Q0xfvg -X9Kk2iw4d4 C_0UQjbQAV0 IdyeQCmcTBs dWECxXNGODg L-HWfBo33xo")
add("Маркировка-и-право", "JGuBLaMWleo")
add("Ниши-и-маркетплейсы", "pYXY75Bh2HI JX0lOa5DaQI")
cat.pop("ulKgsBBfjc4x", None)  # remove guard

# borderline items to explicitly surface
flags = set("ma0dovnmqo0 QRjE1b7LTsA _U7ZePr1EME IJMI6SjFgIY sePoPnrRph0 qumr0SclUNc MLZnIIpMeuU g4lC-xkYpU4 pzIx5x4p9Mw YNN_qs00GSA wpV0IITFb8A C_0UQjbQAV0 KXaQ5woJgBQ JGuBLaMWleo dWECxXNGODg Vs1wE1QXfSU L-HWfBo33xo Yu59CENRKd0".split())

rows=[]
with open('meta_2024plus.txt') as f:
    for line in f:
        line=line.rstrip('\n')
        if '|' not in line: continue
        vid,date,dur,title=line.split('|',3)
        rows.append((vid,date,dur,title))

# validate coverage
missing=[]; both=[]
for vid,date,dur,title in rows:
    ind = vid in drop; ink = vid in cat
    if ind and ink: both.append(vid)
    if not ind and not ink: missing.append((vid,date,title))
print(f"total={len(rows)} drop={len(drop)} keep={len(cat)}")
print("UNCATEGORIZED (need to assign):")
for m in missing: print("   ", m)
print("IN BOTH (error):", both)

# write outputs sorted newest-first
rows_by_id={r[0]:r for r in rows}
with open('drop.tsv','w') as o:
    for vid,date,dur,title in rows:
        if vid in drop: o.write(f"{date}\t{vid}\t{drop[vid]}\t{'[?]' if vid in flags else ''}\t{title}\n")
with open('keep.tsv','w') as o:
    for vid,date,dur,title in rows:
        if vid in cat: o.write(f"{cat[vid]}\t{date}\t{vid}\t{dur}\t{'[?]' if vid in flags else ''}\t{title}\n")

# counts
from collections import Counter
cc=Counter(cat.values())
print("\n=== KEEP by category ===")
for c,n in sorted(cc.items(), key=lambda x:-x[1]): print(f"  {n:>3}  {c}")
print(f"  TOTAL KEEP = {sum(cc.values())}")
dc=Counter(drop.values())
print("\n=== DROP by reason ===")
for c,n in sorted(dc.items(), key=lambda x:-x[1]): print(f"  {n:>3}  {c}")
print(f"  TOTAL DROP = {sum(dc.values())}")
print(f"\n  borderline [?] flagged = {len(flags)}")
