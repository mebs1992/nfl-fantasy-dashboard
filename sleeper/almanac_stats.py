"""Fun stats for The Almanac. Everything is computed from completed games."""
from collections import defaultdict


def _scored(g):
    return g["status"] == "Final"


def _decided(g):
    return g["status"] in ("Final", "Result known")


def _team_rows(games):
    rows = []
    for g in games:
        if not _decided(g):
            continue
        for me, my, opp, op in ((g["a"], g["a_pts"], g["b"], g["b_pts"]), (g["b"], g["b_pts"], g["a"], g["a_pts"])):
            res = "T" if g["winner"] is None else ("W" if g["winner"] == me else "L")
            rows.append(dict(s=g["season"], w=g["week"], st=g["stage"], fr=me, opp=opp, pts=my, op=op, res=res, sc=_scored(g)))
    rows.sort(key=lambda r: (r["s"], r["w"]))
    return rows


def _game(r):
    return dict(s=r["s"], w=r["w"], st=r["st"], fr=r["fr"], opp=r["opp"], pts=r["pts"], op=r["op"])


def fun_stats(games, standings, champions, res, sleeper):
    rows = _team_rows(games)
    sc = [r for r in rows if r["sc"]]
    active_season = max(r[0] for r in standings)
    active = sorted({r[2] for r in standings if r[0] == active_season})
    out = {}

    # ---------- weekly scoreboard: top dog and wooden spoon
    weeks = defaultdict(list)
    for r in sc:
        if r["st"] == "Regular":
            weeks[(r["s"], r["w"])].append(r)
    top, spoon = defaultdict(int), defaultdict(int)
    for wk, rs in weeks.items():
        if len(rs) < 4:
            continue
        top[max(rs, key=lambda r: r["pts"])["fr"]] += 1
        spoon[min(rs, key=lambda r: r["pts"])["fr"]] += 1
    out["top_dog"] = sorted(([k, v] for k, v in top.items()), key=lambda kv: -kv[1])
    out["wooden_spoon"] = sorted(([k, v] for k, v in spoon.items()), key=lambda kv: -kv[1])
    tot = {wk: sum(r["pts"] for r in rs) / len(rs) for wk, rs in weeks.items() if len(rs) >= 8}
    hi = max(tot, key=tot.get)
    lo = min(tot, key=tot.get)
    out["league_weeks"] = dict(best=dict(s=hi[0], w=hi[1], avg=round(tot[hi], 2)), worst=dict(s=lo[0], w=lo[1], avg=round(tot[lo], 2)))

    # ---------- heartbreak and daylight robbery
    losses = [r for r in sc if r["res"] == "L"]
    wins = [r for r in sc if r["res"] == "W"]
    out["heartbreaks"] = [_game(r) for r in sorted(losses, key=lambda r: -r["pts"])[:8]]
    out["robberies"] = [_game(r) for r in sorted(wins, key=lambda r: r["pts"])[:8]]
    out["blowouts"] = [_game(r) for r in sorted(wins, key=lambda r: -(r["pts"] - r["op"]))[:10]]
    out["nail_biters"] = [_game(r) for r in sorted(wins, key=lambda r: (round(r["pts"] - r["op"], 2), r["s"]))[:10]]
    out["high_scores"] = [_game(r) for r in sorted(sc, key=lambda r: -r["pts"])[:10]]
    out["low_scores"] = [_game(r) for r in sorted(sc, key=lambda r: r["pts"])[:10]]

    # ---------- luck: actual wins vs all-play expected wins (regular season, scored weeks)
    luck = []
    for season in sorted({k[0] for k in weeks}):
        exp, act, gp = defaultdict(float), defaultdict(int), defaultdict(int)
        for (s, w), rs in weeks.items():
            if s != season or len(rs) < 4:
                continue
            for r in rs:
                beat = sum(r["pts"] > o["pts"] for o in rs if o is not r) + 0.5 * sum(r["pts"] == o["pts"] for o in rs if o is not r)
                exp[r["fr"]] += beat / (len(rs) - 1)
                act[r["fr"]] += 1 if r["res"] == "W" else 0.5 if r["res"] == "T" else 0
                gp[r["fr"]] += 1
        for fr in exp:
            luck.append(dict(s=season, fr=fr, actual=act[fr], expected=round(exp[fr], 2), luck=round(act[fr] - exp[fr], 2), gp=gp[fr]))
    out["luckiest"] = sorted(luck, key=lambda x: -x["luck"])[:8]
    out["unluckiest"] = sorted(luck, key=lambda x: x["luck"])[:8]
    career = defaultdict(float)
    for x in luck:
        career[x["fr"]] += x["luck"]
    out["career_luck"] = sorted(([k, round(v, 2)] for k, v in career.items()), key=lambda kv: -kv[1])
    out["luck_current"] = sorted([x for x in luck if x["s"] == active_season], key=lambda x: -x["luck"])

    # ---------- rivalries
    pair = res["pair"]
    rival = []
    for (a, b), p in pair.items():
        if p["games"] < 10:
            continue
        closeness = 1 - abs(p["aw"] - p["bw"]) / p["games"]
        score = p["games"] * closeness + 4 * p["po"]
        rival.append(dict(a=a, b=b, games=p["games"], aw=p["aw"], bw=p["bw"], t=p["t"], po=p["po"],
                          avg_margin=round(sum(p["margins"]) / len(p["margins"]), 2) if p["margins"] else None, score=round(score, 2)))
    out["arch_rivals"] = sorted(rival, key=lambda x: -x["score"])[:6]

    profiles = {}
    for fr in res["frs"]:
        opps = []
        for (a, b), p in pair.items():
            if fr not in (a, b):
                continue
            me_w, op_w = (p["aw"], p["bw"]) if fr == a else (p["bw"], p["aw"])
            opps.append(dict(opp=b if fr == a else a, games=p["games"], w=me_w, l=op_w, t=p["t"], po=p["po"],
                             pct=round((me_w + 0.5 * p["t"]) / p["games"], 3)))
        big = [o for o in opps if o["games"] >= 8] or opps
        nemesis = min(big, key=lambda o: (o["pct"], -o["games"]))
        victim = max(big, key=lambda o: (o["pct"], o["games"]))
        arch = max(opps, key=lambda o: o["games"] * (1 - abs(o["w"] - o["l"]) / o["games"]) + 4 * o["po"])
        mine = [r for r in rows if r["fr"] == fr]
        # current streak
        streak = None
        if mine:
            last = mine[-1]["res"]
            n = 0
            for r in reversed(mine):
                if r["res"] != last:
                    break
                n += 1
            streak = f"{last}{n}"
        titles = [c["season"] if isinstance(c, dict) else c[0] for c in champions if (c[1] if not isinstance(c, dict) else c["champion"]) == fr]
        po = [r for r in mine if r["st"] == "Playoff"]
        profiles[fr] = dict(nemesis=nemesis, victim=victim, arch=arch, streak=streak,
                            titles=sorted(titles), last_title=max(titles) if titles else None,
                            drought=(active_season - max(titles)) if titles else None,
                            playoff_games=len(po), active=fr in active,
                            best_score=_game(max((r for r in mine if r["sc"]), key=lambda r: r["pts"])) if any(r["sc"] for r in mine) else None)
    out["profiles"] = profiles

    # ---------- title droughts (active franchises)
    out["droughts"] = sorted(([fr, profiles[fr]["last_title"]] for fr in active), key=lambda kv: (kv[1] or 0))

    # ---------- top seeds
    seeds = []
    champs = {c[0]: c[1] for c in champions}
    for s in sorted({r[0] for r in standings}):
        if not str(champs.get(s, "—")).startswith("—"):
            top_seed = next(r for r in standings if r[0] == s and r[1] == 1)
            seeds.append(dict(s=s, seed1=top_seed[2], place=top_seed[15], champ=champs[s],
                              champ_seed=next((r[1] for r in standings if r[0] == s and r[2] == champs[s]), None)))
    out["top_seeds"] = seeds

    # ---------- renames
    nm = defaultdict(list)
    for n in res["names"]:
        nm[n[0]].append(n[1])
    out["rename_kings"] = sorted(([k, v] for k, v in nm.items()), key=lambda kv: -len(kv[1]))[:5]

    # ---------- guillotine: hypothetical for every season, real tracker for Sleeper seasons
    guill = []
    for season in sorted({k[0] for k in weeks}):
        wks = sorted(w for (s, w) in weeks if s == season)
        alive = {r["fr"] for w in wks for r in weeks[(season, w)]}
        cuts = []
        for w in wks:
            if len(alive) <= 1:
                break
            rs = [r for r in weeks[(season, w)] if r["fr"] in alive]
            if not rs:
                continue
            low = min(rs, key=lambda r: r["pts"])
            alive.discard(low["fr"])
            cuts.append(dict(w=w, fr=low["fr"], pts=low["pts"]))
        guill.append(dict(s=season, cuts=cuts, alive=sorted(alive), complete=len(alive) == 1))
    out["guillotine"] = guill
    first_cut = defaultdict(int)
    survivor = defaultdict(int)
    for gs in guill:
        if gs["cuts"]:
            first_cut[gs["cuts"][0]["fr"]] += 1
        if gs["complete"]:
            survivor[gs["alive"][0]] += 1
    out["guillotine_first_cut"] = sorted(([k, v] for k, v in first_cut.items()), key=lambda kv: -kv[1])
    out["guillotine_survivors"] = sorted(([k, v] for k, v in survivor.items()), key=lambda kv: -kv[1])

    # ---------- current season
    cur = sleeper[-1] if sleeper else None
    if cur:
        out["current"] = dict(season=cur["season"], through_week=cur["done_reg"], playoff_start=cur["pws"], complete=cur["complete"],
                              names=cur["names"], weekly=cur["weekly"])
    return out
