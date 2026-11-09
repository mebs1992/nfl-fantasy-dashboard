"""Extra Almanac features: character, legacy, storytelling, trash talk, and
(from Sleeper seasons) lineups, trades, waivers and draft grades.

Every number comes from completed games. Output goes into almanac.json["x"].
"""
import json
import random
import statistics as stats
from collections import defaultdict

SIMS = 10000


def _decided(g):
    return g["status"] in ("Final", "Result known")


def _scored(g):
    return g["status"] == "Final"


def r2(x):
    return None if x is None else round(x, 2)


def team_rows(games):
    out = []
    for g in games:
        if not _decided(g):
            continue
        for me, my, opp, op, nm in ((g["a"], g["a_pts"], g["b"], g["b_pts"], g["a_name"]),
                                    (g["b"], g["b_pts"], g["a"], g["a_pts"], g["b_name"])):
            res = "T" if g["winner"] is None else ("W" if g["winner"] == me else "L")
            out.append(dict(s=g["season"], w=g["week"], st=g["stage"], fr=me, opp=opp, pts=my, op=op,
                            res=res, sc=_scored(g), name=nm))
    out.sort(key=lambda r: (r["s"], r["w"]))
    return out


def wl(rows):
    w = sum(r["res"] == "W" for r in rows)
    l = sum(r["res"] == "L" for r in rows)
    t = sum(r["res"] == "T" for r in rows)
    return w, l, t


def pct(w, l, t=0):
    g = w + l + t
    return (w + 0.5 * t) / g if g else None


# ====================================================================== character
def character(rows, standings, champions):
    reg = [r for r in rows if r["st"] == "Regular" and r["sc"]]
    by_season = defaultdict(list)
    for r in reg:
        by_season[r["s"]].append(r["pts"])
    league_sd = {s: stats.pstdev(v) for s, v in by_season.items() if len(v) > 4}
    league_mean = {s: stats.mean(v) for s, v in by_season.items() if v}

    # boom or bust: a team's weekly spread relative to the league's that season
    ts = defaultdict(list)
    for r in reg:
        ts[(r["fr"], r["s"])].append(r["pts"])
    vol_season = []
    for (fr, s), v in ts.items():
        if len(v) >= 5 and league_sd.get(s):
            vol_season.append(dict(fr=fr, s=s, vol=stats.pstdev(v) / league_sd[s], sd=stats.pstdev(v),
                                   hi=max(v), lo=min(v), avg=stats.mean(v)))
    place = {(r[2], r[0]): r[15] for r in standings}
    champs = {c[0]: c[1] for c in champions if c[1] and not str(c[1]).startswith("—")}
    by_fr = defaultdict(list)
    for x in vol_season:
        x["place"] = place.get((x["fr"], x["s"]))
        x["champ"] = champs.get(x["s"]) == x["fr"]
        by_fr[x["fr"]].append(x)
    boom = []
    for fr, xs in by_fr.items():
        allpts = [p for x in xs for p in ts[(fr, x["s"])]]
        boom.append(dict(fr=fr, vol=r2(stats.mean(x["vol"] for x in xs)), seasons=len(xs),
                         sd=r2(stats.pstdev(allpts)), best=r2(max(allpts)), worst=r2(min(allpts))))
    boom.sort(key=lambda x: -x["vol"])
    med = stats.median(x["vol"] for x in vol_season)
    champ_v = [x for x in vol_season if x["champ"]]
    wild = [x for x in vol_season if x["vol"] >= med]
    steady = [x for x in vol_season if x["vol"] < med]
    def avg_place(xs):
        p = [x["place"] for x in xs if x["place"]]
        return r2(stats.mean(p)) if p else None
    verdict = dict(
        champs_wild=sum(x["vol"] >= med for x in champ_v), champs_total=len(champ_v),
        wild_avg_finish=avg_place(wild), steady_avg_finish=avg_place(steady),
        wild_titles=sum(x["champ"] for x in wild), steady_titles=sum(x["champ"] for x in steady))
    seasons_wild = sorted(vol_season, key=lambda x: -x["vol"])[:6]
    seasons_steady = sorted(vol_season, key=lambda x: x["vol"])[:6]
    slim = lambda x: dict(fr=x["fr"], s=x["s"], vol=r2(x["vol"]), hi=r2(x["hi"]), lo=r2(x["lo"]), place=x["place"])

    # clutch: close games, playoffs vs regular season
    clutch = []
    frs = sorted({r["fr"] for r in rows})
    for fr in frs:
        mine = [r for r in rows if r["fr"] == fr]
        close = [r for r in mine if r["sc"] and abs(r["pts"] - r["op"]) < 10]
        po = [r for r in mine if r["st"] == "Playoff"]
        rg = [r for r in mine if r["st"] == "Regular"]
        cw, cl, ct = wl(close)
        pw, pl, pt = wl(po)
        rw, rl, rt = wl(rg)
        title_games = [c for c in champions if fr in (c[1], c[3]) and c[1] and not str(c[1]).startswith("—")]
        tw = sum(c[1] == fr for c in title_games)
        clutch.append(dict(fr=fr, close=f"{cw}-{cl}" + (f"-{ct}" if ct else ""), close_pct=r2(pct(cw, cl, ct)), close_n=cw + cl + ct,
                           po=f"{pw}-{pl}", po_pct=r2(pct(pw, pl, pt)), reg_pct=r2(pct(rw, rl, rt)),
                           finals=f"{tw}-{len(title_games) - tw}",
                           swing=r2((pct(pw, pl, pt) or 0) - (pct(rw, rl, rt) or 0)) if pw + pl else None))
    clutch.sort(key=lambda x: (x["close_n"] < 10, -(x["close_pct"] or 0)))

    # hot and cold starts: weeks 1-6 vs weeks 7-14
    hc = []
    hc_seasons = []
    for fr in frs:
        mine = [r for r in rows if r["fr"] == fr and r["st"] == "Regular"]
        early = [r for r in mine if r["w"] <= 6]
        late = [r for r in mine if 7 <= r["w"] <= 14]
        e, l = pct(*wl(early)), pct(*wl(late))
        if e is not None and l is not None:
            hc.append(dict(fr=fr, early=r2(e), late=r2(l), swing=r2(l - e), early_rec="-".join(map(str, wl(early)[:2])),
                           late_rec="-".join(map(str, wl(late)[:2]))))
        for s in sorted({r["s"] for r in mine}):
            es = [r for r in early if r["s"] == s]
            ls = [r for r in late if r["s"] == s]
            if len(es) >= 5 and len(ls) >= 5:
                hc_seasons.append(dict(fr=fr, s=s, early="-".join(map(str, wl(es)[:2])), late="-".join(map(str, wl(ls)[:2])),
                                       swing=r2(pct(*wl(ls)) - pct(*wl(es))), place=place.get((fr, s))))
    hc.sort(key=lambda x: -x["swing"])
    return dict(
        boom=boom, boom_verdict=verdict, boom_wild=[slim(x) for x in seasons_wild], boom_steady=[slim(x) for x in seasons_steady],
        clutch=clutch, hotcold=hc,
        collapses=sorted(hc_seasons, key=lambda x: x["swing"])[:6],
        surges=sorted(hc_seasons, key=lambda x: -x["swing"])[:6],
    ), league_mean


# ====================================================================== legacy
def legacy(rows, standings, champions, res):
    lb = {r[1]: r for r in res["leaderboard"]}
    dyn = []
    for fr, r in lb.items():
        titles, finals, po_seasons, seasons, win_pct = r[2], r[3], r[4], r[5], r[9]
        parts = dict(titles=titles * 30, finals=(finals - titles) * 12, playoffs=po_seasons * 5,
                     winning=round((win_pct - 0.5) * 200, 1), longevity=seasons)
        dyn.append(dict(fr=fr, raw=sum(parts.values()), parts=parts, titles=titles, finals=finals,
                        po_seasons=po_seasons, seasons=seasons, win_pct=win_pct))
    top = max(d["raw"] for d in dyn)
    low = min(d["raw"] for d in dyn)
    for d in dyn:
        d["score"] = round(100 * (d["raw"] - low) / (top - low)) if top > low else 100
    dyn.sort(key=lambda d: -d["raw"])

    # hall of fame / shame seasons (completed seasons only)
    done = [r for r in standings if r[15] is not None]
    by_s = defaultdict(list)
    for r in done:
        by_s[r[0]].append(r)
    graded = []
    for s, rs in by_s.items():
        ppg = [r[13] for r in rs if r[13]]
        m, sd = stats.mean(ppg), stats.pstdev(ppg) or 1
        n = len(rs)
        for r in rs:
            finish = {1: 2.0, 2: 1.0, 3: 0.5}.get(r[15], 0) - (1.0 if r[15] == n else 0)
            score = (r[9] - 0.5) * 6 + (r[13] - m) / sd + finish
            graded.append(dict(fr=r[2], name=r[3], s=s, rec=f"{r[6]}-{r[7]}" + (f"-{r[8]}" if r[8] else ""),
                               ppg=r[13], place=r[15], n=n, score=round(score, 2)))
    graded.sort(key=lambda x: -x["score"])
    return dict(dynasty=dyn, fame=graded[:10], shame=list(reversed(graded[-10:])))


# ====================================================================== storytelling
def ladder_race(rows, standings):
    out = []
    for s in sorted({r["s"] for r in rows}):
        reg = [r for r in rows if r["s"] == s and r["st"] == "Regular"]
        weeks = sorted({r["w"] for r in reg})
        frs = sorted({r["fr"] for r in reg})
        w = defaultdict(float)
        pf = defaultdict(float)
        pos = {fr: [] for fr in frs}
        for wk in weeks:
            for r in reg:
                if r["w"] == wk:
                    w[r["fr"]] += 1 if r["res"] == "W" else 0.5 if r["res"] == "T" else 0
                    pf[r["fr"]] += r["pts"] or 0
            order = sorted(frs, key=lambda f: (-w[f], -pf[f]))
            for i, f in enumerate(order, 1):
                pos[f].append(i)
        out.append(dict(s=s, weeks=weeks, teams=[dict(fr=f, pos=pos[f]) for f in frs]))
    return out


def recaps(rows, standings, champions, fun):
    champs = {c[0]: c for c in champions}
    luck = defaultdict(list)
    for x in fun.get("luckiest", []) + fun.get("unluckiest", []):
        pass
    out = []
    for s in sorted({r[0] for r in standings}, reverse=True):
        st = sorted([r for r in standings if r[0] == s], key=lambda r: r[1])
        if not st:
            continue
        sr = [r for r in rows if r["s"] == s and r["sc"]]
        wins = [r for r in sr if r["res"] == "W"]
        hi = max(sr, key=lambda r: r["pts"]) if sr else None
        blow = max(wins, key=lambda r: r["pts"] - r["op"]) if wins else None
        top_pf = max(st, key=lambda r: r[10])
        c = champs.get(s)
        champ = c[1] if c and c[1] and not str(c[1]).startswith("—") else None
        out.append(dict(
            s=s, champ=champ, runner=c[3] if champ else None, seed=c[6] if champ else None, title_score=c[2] if champ else None,
            first=dict(fr=st[0][2], rec=f"{st[0][6]}-{st[0][7]}"), last=dict(fr=st[-1][2], rec=f"{st[-1][6]}-{st[-1][7]}"),
            top_pf=dict(fr=top_pf[2], pf=top_pf[10]),
            high=dict(fr=hi["fr"], pts=hi["pts"], w=hi["w"], opp=hi["opp"]) if hi else None,
            blowout=dict(fr=blow["fr"], opp=blow["opp"], m=r2(blow["pts"] - blow["op"]), w=blow["w"]) if blow else None,
            complete=bool(champ)))
    return out


def awards(rows):
    weeks = defaultdict(list)
    for r in rows:
        if r["sc"]:
            weeks[(r["s"], r["w"])].append(r)
    per_week = []
    cabinet = defaultdict(lambda: defaultdict(int))
    for (s, w), rs in sorted(weeks.items()):
        if len(rs) < 6:
            continue
        top = max(rs, key=lambda r: r["pts"])
        low = min(rs, key=lambda r: r["pts"])
        losers = [r for r in rs if r["res"] == "L"]
        winners = [r for r in rs if r["res"] == "W"]
        robbed = max(losers, key=lambda r: r["pts"]) if losers else None
        lucky = min(winners, key=lambda r: r["pts"]) if winners else None
        a = dict(s=s, w=w,
                 motw=dict(fr=top["fr"], name=top["name"], pts=top["pts"], opp=top["opp"]),
                 robbed=dict(fr=robbed["fr"], name=robbed["name"], pts=robbed["pts"], opp=robbed["opp"], op=robbed["op"]) if robbed else None,
                 lucky=dict(fr=lucky["fr"], name=lucky["name"], pts=lucky["pts"], opp=lucky["opp"], op=lucky["op"]) if lucky else None,
                 shame=dict(fr=low["fr"], name=low["name"], pts=low["pts"], opp=low["opp"]))
        per_week.append(a)
        cabinet[top["fr"]]["motw"] += 1
        cabinet[low["fr"]]["shame"] += 1
        if robbed:
            cabinet[robbed["fr"]]["robbed"] += 1
        if lucky:
            cabinet[lucky["fr"]]["lucky"] += 1
    cab = [dict(fr=fr, **{k: v.get(k, 0) for k in ("motw", "robbed", "lucky", "shame")}) for fr, v in cabinet.items()]
    cab.sort(key=lambda x: (-x["motw"], x["shame"]))
    return per_week, cab


def sob_story(rows):
    reg = [r for r in rows if r["st"] == "Regular" and r["sc"]]
    season_high = defaultdict(float)
    for r in reg:
        season_high[(r["fr"], r["s"])] = max(season_high[(r["fr"], r["s"])], r["pts"])
    league_avg = defaultdict(list)
    for r in reg:
        league_avg[r["s"]].append(r["pts"])
    league_avg = {s: stats.mean(v) for s, v in league_avg.items()}
    agg = defaultdict(lambda: dict(highs=0, games=0, above=0.0))
    per_season = []
    seasons = defaultdict(lambda: dict(highs=0, games=0, above=0.0, pa=0.0))
    for r in reg:
        hit = abs(r["op"] - season_high[(r["opp"], r["s"])]) < 1e-9
        a = agg[r["fr"]]
        a["games"] += 1
        a["highs"] += hit
        a["above"] += r["op"] - league_avg[r["s"]]
        b = seasons[(r["fr"], r["s"])]
        b["games"] += 1
        b["highs"] += hit
        b["above"] += r["op"] - league_avg[r["s"]]
        b["pa"] += r["op"]
    alltime = sorted((dict(fr=fr, highs=a["highs"], games=a["games"], tough=r2(a["above"] / a["games"])) for fr, a in agg.items()),
                     key=lambda x: -x["highs"])
    for (fr, s), b in seasons.items():
        per_season.append(dict(fr=fr, s=s, highs=b["highs"], tough=r2(b["above"] / b["games"]), pa=r2(b["pa"]), games=b["games"]))
    worst = sorted(per_season, key=lambda x: -x["tough"])[:8]
    return dict(alltime=alltime, seasons=per_season, toughest=worst)


# ====================================================================== this week
def upcoming(rows, games, cur):
    """Next week's matchups with history, bogey and revenge flags."""
    if not cur or cur["complete"]:
        return None
    nxt = cur["done_reg"] + 1
    games_next = [g for g in games if g["season"] == cur["season"] and g["week"] == nxt]
    if not games_next:
        return None
    out = []
    for g in games_next:
        A, B = g["a"], g["b"]
        hist = [r for r in rows if r["fr"] == A and r["opp"] == B]
        w, l, t = wl(hist)
        last = hist[-1] if hist else None
        flags = []
        # bogey: someone dominates the head to head
        if w + l >= 8:
            lead, trail, lw, ll = (A, B, w, l) if w > l else (B, A, l, w)
            if lw / (lw + ll) >= 0.65:
                flags.append(dict(kind="bogey", text=f"{lead} have beaten {trail} {lw} of {w + l + t} times"))
        # revenge: playoff knockouts and 50-point beatings in their last meeting
        po = [r for r in hist if r["st"] == "Playoff"]
        if po:
            lp = po[-1]
            loser = A if lp["res"] == "L" else B
            winner = B if loser == A else A
            flags.append(dict(kind="revenge", text=f"{loser} lost to {winner} in the {lp['s']} playoffs"))
        if last and last["sc"] and abs(last["pts"] - last["op"]) >= 50:
            loser = A if last["res"] == "L" else B
            winner = B if loser == A else A
            flags.append(dict(kind="revenge", text=f"{winner} beat {loser} by {abs(last['pts'] - last['op']):.2f} last time ({last['s']} wk {last['w']})"))
        out.append(dict(a=A, an=g["a_name"], b=B, bn=g["b_name"], aw=w, bw=l, t=t, games=w + l + t,
                        last=dict(s=last["s"], w=last["w"], winner=A if last["res"] == "W" else (B if last["res"] == "L" else None),
                                  score=f"{last['pts']:.2f} – {last['op']:.2f}" if last["sc"] else None) if last else None,
                        flags=flags))
    return dict(week=nxt, games=out)


def odds(cur, games, rows):
    """Monte Carlo of the rest of the regular season and the guillotine."""
    if not cur or cur["complete"]:
        return None
    s, done, pws = cur["season"], cur["done_reg"], cur["pws"]
    rem_weeks = list(range(done + 1, pws))
    sched = defaultdict(list)
    for g in games:
        if g["season"] == s and g["stage"] == "Regular" and g["week"] in rem_weeks:
            sched[g["week"]].append((g["a"], g["b"]))
    reg = [r for r in rows if r["s"] == s and r["st"] == "Regular" and r["sc"]]
    teams = sorted({r["fr"] for r in reg})
    if not teams:
        return None
    scores = defaultdict(list)
    w0 = defaultdict(float)
    pf0 = defaultdict(float)
    for r in reg:
        scores[r["fr"]].append(r["pts"])
        w0[r["fr"]] += 1 if r["res"] == "W" else 0.5 if r["res"] == "T" else 0
        pf0[r["fr"]] += r["pts"]
    allp = [p for v in scores.values() for p in v]
    lm = stats.mean(allp)
    resid = [p - stats.mean(scores[f]) for f in teams for p in scores[f]]
    sd = stats.pstdev(resid) or 25.0
    mean = {f: (len(scores[f]) * stats.mean(scores[f]) + 4 * lm) / (len(scores[f]) + 4) for f in teams}

    alive0 = set(cur["guillotine_alive"])
    rng = random.Random(2026)
    po_ct = defaultdict(int)
    top_ct = defaultdict(int)
    last_ct = defaultdict(int)
    cut_next = defaultdict(int)
    surv_ct = defaultdict(int)
    pts_teams = cur["playoff_teams"]
    guill_weeks = list(range(done + 1, pws + 4))
    for _ in range(SIMS):
        w = dict(w0)
        pf = dict(pf0)
        wk_scores = {}
        for wk in sorted(set(rem_weeks) | set(guill_weeks)):
            sc = {f: rng.gauss(mean[f], sd) for f in teams}
            wk_scores[wk] = sc
            if wk in sched:
                for a, b in sched[wk]:
                    pf[a] += sc[a]
                    pf[b] += sc[b]
                    if sc[a] > sc[b]:
                        w[a] += 1
                    else:
                        w[b] += 1
        order = sorted(teams, key=lambda f: (-w[f], -pf[f]))
        for f in order[:pts_teams]:
            po_ct[f] += 1
        top_ct[order[0]] += 1
        last_ct[order[-1]] += 1
        alive = set(alive0)
        first = True
        for wk in guill_weeks:
            if len(alive) <= 1:
                break
            sc = wk_scores[wk]
            low = min(alive, key=lambda f: sc[f])
            if first:
                cut_next[low] += 1
                first = False
            alive.discard(low)
        if len(alive) == 1:
            surv_ct[next(iter(alive))] += 1
    table = []
    for f in teams:
        table.append(dict(fr=f, w=w0[f], pf=r2(pf0[f]), avg=r2(stats.mean(scores[f])),
                          playoffs=round(100 * po_ct[f] / SIMS, 1), top=round(100 * top_ct[f] / SIMS, 1),
                          last=round(100 * last_ct[f] / SIMS, 1)))
    table.sort(key=lambda x: (-x["playoffs"], -x["w"], -x["pf"]))
    guill = [dict(fr=f, next_cut=round(100 * cut_next[f] / SIMS, 1), survive=round(100 * surv_ct[f] / SIMS, 1)) for f in sorted(alive0)]
    guill.sort(key=lambda x: -x["next_cut"])
    return dict(sims=SIMS, weeks_left=len(rem_weeks), playoff_teams=pts_teams, table=table, guillotine=guill)


# ====================================================================== Sleeper extras
def slot_ok(slot, fpos):
    if slot == "FLEX":
        return any(p in ("RB", "WR", "TE") for p in fpos)
    if slot == "SUPER_FLEX":
        return any(p in ("QB", "RB", "WR", "TE") for p in fpos)
    if slot == "REC_FLEX":
        return any(p in ("WR", "TE") for p in fpos)
    if slot == "WRRB_FLEX":
        return any(p in ("WR", "RB") for p in fpos)
    return slot in fpos


def optimal(points, slots, players):
    """Best lineup score. Fill specific slots first, then flex slots."""
    pool = sorted(points.items(), key=lambda kv: -(kv[1] or 0))
    used = set()
    total = 0.0
    order = sorted(range(len(slots)), key=lambda i: ("FLEX" in slots[i], i))
    for i in order:
        slot = slots[i]
        for pid, p in pool:
            if pid in used:
                continue
            if slot_ok(slot, players.get(pid, {}).get("fpos") or []):
                used.add(pid)
                total += p or 0
                break
    return total


def sleeper_extras(sl):
    d = sl["dir"]
    fr = sl["roster_fr"]
    players = json.loads((d / "players.json").read_text()) if (d / "players.json").exists() else {}
    league = sl["league"]
    slots = [p for p in league.get("roster_positions", []) if p not in ("BN", "IR", "TAXI")]
    pname = lambda pid: players.get(pid, {}).get("name", f"Player {pid}")
    ppos = lambda pid: players.get(pid, {}).get("pos", "")
    done = sl["done_reg"]
    weeks = {}
    for f in sorted(d.glob("matchups_wk*.json")):
        wk = int(f.stem[-2:])
        if wk <= done or (wk >= sl["pws"] and any((m.get("points") or 0) > 0 for m in json.loads(f.read_text()))):
            weeks[wk] = json.loads(f.read_text())
    if not weeks or not slots:
        return None

    # ---------- lineups
    lineup = defaultdict(lambda: dict(actual=0.0, best=0.0, weeks=0, lost=0, lost_list=[]))
    blunders = []
    ppts_all = defaultdict(float)          # player points on any roster, final weeks
    ppts_on = defaultdict(float)           # (roster, player) points while on that roster
    pstart_on = defaultdict(float)
    by_week_roster = {}
    for wk, ms in weeks.items():
        mids = defaultdict(list)
        for m in ms:
            by_week_roster[(wk, m["roster_id"])] = m
            if m.get("matchup_id") is not None:
                mids[m["matchup_id"]].append(m)
            for pid, p in (m.get("players_points") or {}).items():
                ppts_all[pid] += p or 0
                ppts_on[(m["roster_id"], pid)] += p or 0
            for pid, p in zip(m.get("starters") or [], m.get("starters_points") or []):
                if pid and pid != "0":
                    pstart_on[(m["roster_id"], pid)] += p or 0
        if wk > done:
            continue
        for m in ms:
            pts_map = m.get("players_points") or {}
            if not pts_map:
                continue
            actual = m.get("points") or 0
            best = optimal(pts_map, slots, players)
            L = lineup[fr[m["roster_id"]]]
            L["actual"] += actual
            L["best"] += best
            L["weeks"] += 1
            opp = next((o for o in mids.get(m.get("matchup_id"), []) if o is not m), None)
            if opp is not None and actual < (opp.get("points") or 0) < best:
                L["lost"] += 1
                L["lost_list"].append(dict(w=wk, opp=fr[opp["roster_id"]], actual=r2(actual), best=r2(best), op=r2(opp.get("points"))))
            # single worst sit/start call this week
            starters = m.get("starters") or []
            bench = [p for p in pts_map if p not in starters]
            worst = None
            for i, sid in enumerate(starters):
                if i >= len(slots) or not sid or sid == "0":
                    continue
                sp = pts_map.get(sid, 0) or 0
                for bid in bench:
                    bp = pts_map.get(bid, 0) or 0
                    if bp > sp and slot_ok(slots[i], players.get(bid, {}).get("fpos") or []):
                        if worst is None or bp - sp > worst["diff"]:
                            worst = dict(diff=bp - sp, start=sid, sp=sp, bench=bid, bp=bp)
            if worst:
                blunders.append(dict(fr=fr[m["roster_id"]], w=wk, diff=r2(worst["diff"]),
                                     started=pname(worst["start"]), started_pts=r2(worst["sp"]),
                                     benched=pname(worst["bench"]), benched_pts=r2(worst["bp"]),
                                     lost=bool(opp is not None and actual < (opp.get("points") or 0) <= actual + worst["diff"])))
    lineups = []
    for f, L in lineup.items():
        lineups.append(dict(fr=f, actual=r2(L["actual"]), best=r2(L["best"]), left=r2(L["best"] - L["actual"]),
                            eff=round(100 * L["actual"] / L["best"], 1) if L["best"] else None, weeks=L["weeks"],
                            lost=L["lost"], lost_list=L["lost_list"]))
    lineups.sort(key=lambda x: -(x["eff"] or 0))
    blunders.sort(key=lambda x: -x["diff"])

    # ---------- transactions
    txns = json.loads((d / "transactions.json").read_text()) if (d / "transactions.json").exists() else []
    trades = []
    for t in txns:
        if t["type"] != "trade":
            continue
        sides = []
        for rid in t["roster_ids"]:
            got = [pid for pid, to in (t.get("adds") or {}).items() if to == rid]
            pts = sum(ppts_on.get((rid, pid), 0) for pid in got)
            started = sum(pstart_on.get((rid, pid), 0) for pid in got)
            # points only after the trade: subtract weeks before it
            pre = sum((by_week_roster.get((wk, rid), {}).get("players_points") or {}).get(pid, 0) or 0
                      for wk in weeks if wk < (t["leg"] or 0) for pid in got)
            pre_s = 0.0
            for wk in weeks:
                if wk < (t["leg"] or 0):
                    m = by_week_roster.get((wk, rid), {})
                    for pid, p in zip(m.get("starters") or [], m.get("starters_points") or []):
                        if pid in got:
                            pre_s += p or 0
            picks = [p for p in (t.get("draft_picks") or []) if p.get("owner_id") == rid]
            sides.append(dict(fr=fr.get(rid, str(rid)), got=[dict(name=pname(p), pos=ppos(p),
                                                                   pts=r2(ppts_on.get((rid, p), 0) - sum((by_week_roster.get((wk, rid), {}).get("players_points") or {}).get(p, 0) or 0 for wk in weeks if wk < (t["leg"] or 0))))
                                                              for p in got],
                              picks=[f"{p.get('season')} round {p.get('round')}" for p in picks],
                              pts=r2(pts - pre), started=r2(started - pre_s)))
        sides.sort(key=lambda x: -x["started"])
        winner = sides[0]["fr"] if len(sides) > 1 and sides[0]["started"] > sides[1]["started"] else None
        trades.append(dict(w=t["leg"], sides=sides, winner=winner,
                           margin=r2(sides[0]["started"] - sides[1]["started"]) if len(sides) > 1 else None))

    adds = []
    for t in txns:
        if t["type"] not in ("waiver", "free_agent"):
            continue
        for pid, rid in (t.get("adds") or {}).items():
            pts = 0.0
            started = 0.0
            weeks_on = 0
            for wk, ms in weeks.items():
                if wk < (t["leg"] or 0):
                    continue
                m = by_week_roster.get((wk, rid))
                if not m or pid not in (m.get("players_points") or {}):
                    continue
                weeks_on += 1
                pts += m["players_points"].get(pid, 0) or 0
                for sid, sp in zip(m.get("starters") or [], m.get("starters_points") or []):
                    if sid == pid:
                        started += sp or 0
            bid = (t.get("settings") or {}).get("waiver_bid")
            adds.append(dict(fr=fr.get(rid, str(rid)), player=pname(pid), pos=ppos(pid), w=t["leg"], kind=t["type"],
                             pts=r2(pts), started=r2(started), weeks=weeks_on, bid=bid))
    adds.sort(key=lambda x: -x["started"])
    add_by_team = defaultdict(lambda: dict(moves=0, started=0.0))
    for a in adds:
        add_by_team[a["fr"]]["moves"] += 1
        add_by_team[a["fr"]]["started"] += a["started"]
    add_teams = sorted((dict(fr=f, moves=v["moves"], started=r2(v["started"])) for f, v in add_by_team.items()), key=lambda x: -x["started"])

    # ---------- draft
    picks = json.loads((d / "draft_picks.json").read_text()) if (d / "draft_picks.json").exists() else []
    draft = None
    if picks:
        vals = sorted((ppts_all.get(p["player_id"], 0) for p in picks), reverse=True)
        rows = []
        for p in picks:
            got = ppts_all.get(p["player_id"], 0)
            exp = vals[p["pick_no"] - 1] if p["pick_no"] - 1 < len(vals) else 0
            rows.append(dict(fr=fr.get(p["roster_id"], str(p["roster_id"])), rnd=p["round"], pick=p["pick_no"],
                             player=pname(p["player_id"]), pos=ppos(p["player_id"]), pts=r2(got), exp=r2(exp), value=r2(got - exp)))
        teams = defaultdict(list)
        for r in rows:
            teams[r["fr"]].append(r)
        grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
        report = []
        for f, rs in teams.items():
            report.append(dict(fr=f, value=r2(sum(r["value"] for r in rs)), pts=r2(sum(r["pts"] for r in rs)),
                               steal=max(rs, key=lambda r: r["value"]), bust=min(rs, key=lambda r: r["value"]),
                               picks=sorted(rs, key=lambda r: r["pick"])))
        report.sort(key=lambda x: -x["value"])
        n = len(report)
        for i, r in enumerate(report):
            r["grade"] = grades[min(len(grades) - 1, int(i * len(grades) / n))]
        draft = dict(report=report, steals=sorted(rows, key=lambda r: -r["value"])[:8],
                     busts=sorted(rows, key=lambda r: r["value"])[:8], final=sl["complete"])

    return dict(season=sl["season"], through=done, lineups=lineups, blunders=blunders[:10],
                trades=trades, adds=adds[:15], add_teams=add_teams, draft=draft)



# ====================================================================== live week (Monday snapshot)
def live_week(sl, standings):
    """Current scores, projections for players still to play, win chances and a predicted ladder."""
    d = sl["dir"]
    wk = sl["done_reg"] + 1
    pf = d / f"projections_wk{wk:02d}.json"
    mf = d / f"matchups_wk{wk:02d}.json"
    if sl["complete"] or wk >= sl["pws"] or not pf.exists() or not mf.exists():
        return None
    P = json.loads(pf.read_text())
    ms = json.loads(mf.read_text())
    if not any((m.get("points") or 0) > 0 for m in ms):
        return None
    players = json.loads((d / "players.json").read_text()) if (d / "players.json").exists() else {}
    played = set(P.get("played") or [])
    fr = sl["roster_fr"]
    names = sl["names"]
    proj = P.get("proj", {})
    teams = {}
    for m in ms:
        rem = []
        for pid, pts in zip(m.get("starters") or [], m.get("starters_points") or []):
            if not pid or pid == "0":
                continue
            pr = proj.get(pid)
            if pr and pid not in played and not pts:
                info = players.get(pid, {})
                g = (P.get("games") or {}).get(pid, {})
                rem.append(dict(name=info.get("name", pid), pos=info.get("pos"), team=info.get("team") or g.get("team"),
                                opp=g.get("opponent"), proj=pr))
        cur = m.get("points") or 0
        teams[m["roster_id"]] = dict(fr=fr[m["roster_id"]], name=names.get(fr[m["roster_id"]]), cur=round(cur, 2),
                                    rem=rem, proj=round(cur + sum(r["proj"] for r in rem), 2), mid=m.get("matchup_id"))
    rng = random.Random(wk)
    sims = 20000
    def draw(t):
        return t["cur"] + sum(max(0.0, rng.gauss(r["proj"], max(3.0, 0.5 * r["proj"]))) for r in t["rem"])
    pairs = defaultdict(list)
    for rid, t in teams.items():
        if t["mid"] is not None:
            pairs[t["mid"]].append(rid)
    games = []
    win_ct = defaultdict(int)
    low_ct = defaultdict(int)
    alive = set()
    # guillotine survivors this season come from the replay of completed weeks
    weekly = sl["weekly"]
    alive = {t["fr"] for t in teams.values()}
    for w in sorted(weekly):
        sc = {f: p for f, p in weekly[w].items() if f in alive}
        if len(alive) > 1 and sc:
            alive.discard(min(sc, key=sc.get))
    for _ in range(sims):
        sc = {rid: draw(t) for rid, t in teams.items()}
        for mid, (a, b) in ((k, v) for k, v in pairs.items() if len(v) == 2):
            win_ct[a if sc[a] > sc[b] else b] += 1
        al = [rid for rid, t in teams.items() if t["fr"] in alive]
        if len(al) > 1:
            low_ct[min(al, key=lambda r: sc[r])] += 1
    for mid, ids in sorted(pairs.items()):
        if len(ids) != 2:
            continue
        a, b = (teams[i] for i in ids)
        a_id, b_id = ids
        done = not a["rem"] and not b["rem"]
        pa = 100.0 if done and a["cur"] > b["cur"] else 0.0 if done else round(100 * win_ct[a_id] / sims, 1)
        games.append(dict(a=a, b=b, a_win=pa, b_win=round(100 - pa, 1) if done else round(100 * win_ct[b_id] / sims, 1),
                          final=done, to_play=len(a["rem"]) + len(b["rem"])))
    games.sort(key=lambda g: (g["final"], -g["to_play"]))
    # predicted ladder
    cur_rows = {r[2]: r for r in standings if r[0] == sl["season"]}
    pred = []
    for rid, t in teams.items():
        r = cur_rows.get(t["fr"])
        if not r:
            continue
        opp = next((teams[o] for o in pairs.get(t["mid"], []) if o != rid), None)
        win = opp is not None and t["proj"] > opp["proj"]
        pred.append(dict(fr=t["fr"], name=t["name"], seed=r[1], w=r[6] + (1 if win else 0), l=r[7] + (0 if win or opp is None else 1),
                         t=r[8], pf=round(r[10] + t["proj"], 2), pa=round(r[11] + (opp["proj"] if opp else 0), 2),
                         res="W" if win else "L", locked=not t["rem"] and (opp is None or not opp["rem"]),
                         win_pct=round(100 * win_ct[rid] / sims, 1)))
    pred.sort(key=lambda x: (-(x["w"] + 0.5 * x["t"]), -x["pf"]))
    for i, x in enumerate(pred, 1):
        x["pos"] = i
        x["move"] = x["seed"] - i
    danger = sorted(([teams[r]["fr"], round(100 * c / sims, 1)] for r, c in low_ct.items()), key=lambda kv: -kv[1])
    return dict(week=wk, pulled_at=P.get("pulled_at"), games=games, ladder=pred,
                guillotine=[dict(fr=f, name=next((t["name"] for t in teams.values() if t["fr"] == f), f), pct=p,
                                 proj=next((t["proj"] for t in teams.values() if t["fr"] == f), None)) for f, p in danger],
                remaining=sum(len(t["rem"]) for t in teams.values()))

# ====================================================================== entry
def extra_stats(games, standings, champions, res, sleeper):
    rows = team_rows(games)
    char, _ = character(rows, standings, champions)
    leg = legacy(rows, standings, champions, res)
    per_week, cabinet = awards(rows)
    cur = sleeper[-1] if sleeper else None
    cur_info = None
    if cur:
        from almanac_stats import fun_stats  # reuse the guillotine replay
        alive = None
        f = fun_stats(games, standings, champions, res, sleeper)
        g = next((x for x in f["guillotine"] if x["s"] == cur["season"]), None)
        alive = g["alive"] if g else []
        cur_info = dict(season=cur["season"], done_reg=cur["done_reg"], pws=cur["pws"], complete=cur["complete"],
                        playoff_teams=cur["playoff_teams"], guillotine_alive=alive)
        recap_fun = f
    else:
        recap_fun = {}
    return dict(
        character=char,
        legacy=leg,
        race=ladder_race(rows, standings),
        recaps=recaps(rows, standings, champions, recap_fun),
        awards=per_week[-60:], cabinet=cabinet,
        sob=sob_story(rows),
        upcoming=upcoming(rows, games, cur_info),
        odds=odds(cur_info, games, rows),
        sleeper=[x for x in (sleeper_extras(s) for s in sleeper) if x],
        live=live_week(cur, standings) if cur else None,
    )
