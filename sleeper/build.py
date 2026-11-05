"""Rebuild the Sunday Club history workbook and the Almanac data.

Inputs
  sleeper/base/history_2012_2025.xlsx   NFL.com + ESPN archive (frozen)
  sleeper/raw/<season>/                  Sleeper pulls (2026 onward)
  sleeper/franchise_map.csv              Sleeper user -> historical franchise

Outputs
  sleeper/output/Sunday_Club_League_History.xlsx
  sleeper/output/almanac.json

2012-2025 standings and champions are copied from the archive as-is (they
were verified against NFL.com and ESPN). Everything cumulative (all-time
table, head-to-head, records, name history) is recomputed from every game so
new Sleeper weeks flow through.
"""
import csv
import json
import statistics
from collections import defaultdict
from copy import copy
from datetime import datetime, timezone
from itertools import groupby
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
BASE = HERE / "base" / "history_2012_2025.xlsx"
RAW = HERE / "raw"
OUT = HERE / "output"
BASE_LAST = 2025
HEADER_ROW = 5
FIRST = 6


# ---------------------------------------------------------------- helpers
def num(x):
    """148.40 -> '148.4', 93.00 -> '93'."""
    return ("%.2f" % x).rstrip("0").rstrip(".")


def rec(w, l, t):
    return f"{w}-{l}-{t}"


def pct(w, l, t, nd=4):
    g = w + l + t
    return round((w + 0.5 * t) / g, nd) if g else 0


def seasons_str(years):
    years = sorted(set(years))
    out, start, prev = [], None, None
    for y in years:
        if start is None:
            start = prev = y
        elif y == prev + 1:
            prev = y
        else:
            out.append(f"{start}" if start == prev else f"{start}-{prev}")
            start = prev = y
    if start is not None:
        out.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(out)


def table_rows(ws):
    rows = []
    for r in ws.iter_rows(min_row=FIRST, values_only=True):
        if r[0] is None and r[1] is None:
            break
        rows.append(list(r))
    return rows


def decided(g):
    return g["status"] in ("Final", "Result known")


def scored(g):
    return g["status"] == "Final"


# ---------------------------------------------------------------- load
def load_base():
    wb = openpyxl.load_workbook(BASE)
    games = []
    for r in table_rows(wb["All Matchups"]):
        games.append(dict(season=r[0], week=r[1], stage=r[2], status=r[3], a=r[4], a_name=r[5],
                          a_pts=r[6], b=r[7], b_name=r[8], b_pts=r[9], winner=r[10], source="NFL.com"))
    standings = [r[:17] for r in table_rows(wb["Season Standings"])]
    champions = [r[:9] for r in table_rows(wb["Champions"])]
    return wb, games, standings, champions


def load_sleeper(fmap):
    seasons = []
    for d in sorted(p for p in RAW.iterdir() if p.is_dir() and p.name.isdigit()):
        season = int(d.name)
        if season <= BASE_LAST:
            continue
        league = json.loads((d / "league.json").read_text())
        users = {u["user_id"]: u for u in json.loads((d / "users.json").read_text())}
        rosters = json.loads((d / "rosters.json").read_text())
        wb_br = json.loads((d / "winners_bracket.json").read_text()) or []
        st = league["settings"]
        pws = int(st.get("playoff_week_start", 15))
        franchise, name = {}, {}
        for r in rosters:
            u = users.get(r["owner_id"], {})
            tname = (u.get("metadata") or {}).get("team_name") or u.get("display_name") or f"Team {r['roster_id']}"
            fr = fmap.get(r["owner_id"])
            if not fr:
                print(f"WARNING: {u.get('display_name')} ({r['owner_id']}) not in franchise_map.csv; using '{tname}'")
                fr = tname
            franchise[r["roster_id"]] = fr
            name[r["roster_id"]] = tname
        done_reg = max(r["settings"]["wins"] + r["settings"]["losses"] + r["settings"]["ties"] for r in rosters)
        meta = d / "meta.json"
        if meta.exists():
            done_reg = max(done_reg, json.loads(meta.read_text()).get("final_through", 0))
        games, weekly = [], {}
        for f in sorted(d.glob("matchups_wk*.json")):
            wk = int(f.stem[-2:])
            ms = json.loads(f.read_text())
            stage = "Playoff" if wk >= pws else "Regular"
            if stage == "Regular" and wk <= done_reg:
                weekly[wk] = {franchise[m["roster_id"]]: m["points"] for m in ms}
            pairs = defaultdict(list)
            for m in ms:
                if m["matchup_id"] is not None:
                    pairs[m["matchup_id"]].append(m)
            for mid, (x, y) in sorted((k, v) for k, v in pairs.items() if len(v) == 2):
                winner = None
                if stage == "Regular":
                    if wk <= done_reg:
                        status = "Final"
                    elif (x["points"] or 0) + (y["points"] or 0) > 0:
                        status = "In progress"
                    else:
                        status = "Not played"
                else:
                    rnd = wk - pws + 1
                    br = next((b for b in wb_br if b.get("r") == rnd and {b.get("t1"), b.get("t2")} == {x["roster_id"], y["roster_id"]}), None)
                    if br is None:
                        continue  # consolation game, not part of the title race
                    if br.get("w") or (wk <= done_reg and (x["points"] or 0) > 0 and (y["points"] or 0) > 0):
                        status = "Final"
                    else:
                        status = "In progress" if (x["points"] or 0) > 0 else "Not played"
                    if br.get("w"):
                        winner = franchise[br["w"]]
                if status == "Final" and winner is None and x["points"] != y["points"]:
                    winner = franchise[x["roster_id"] if x["points"] > y["points"] else y["roster_id"]]
                if winner and franchise[y["roster_id"]] == winner:
                    x, y = y, x
                games.append(dict(season=season, week=wk, stage=stage, status=status,
                                  a=franchise[x["roster_id"]], a_name=name[x["roster_id"]], a_pts=round(x["points"] or 0, 2),
                                  b=franchise[y["roster_id"]], b_name=name[y["roster_id"]], b_pts=round(y["points"] or 0, 2),
                                  winner=winner if status == "Final" else None, source="Sleeper"))
        # final placings once the bracket is settled
        placing = {}
        for b in wb_br:
            if b.get("p") and b.get("w"):
                placing[franchise[b["w"]]] = b["p"]
                placing[franchise[b["l"]]] = b["p"] + 1
        complete = league.get("status") == "complete" and 1 in placing.values()
        seasons.append(dict(season=season, league=league, games=games, weekly=weekly, done_reg=done_reg,
                            complete=complete, placing=placing, names={franchise[k]: v for k, v in name.items()},
                            teams=len(rosters), pws=pws, dir=d, roster_fr=dict(franchise),
                            playoff_teams=int(st.get("playoff_teams", 4))))
    return seasons


# ---------------------------------------------------------------- compute
def standings_for(season, games, placing, complete):
    t = defaultdict(lambda: dict(gp=0, gs=0, w=0, l=0, ti=0, pf=0.0, pa=0.0, name=None))
    for g in games:
        if g["season"] != season or g["stage"] != "Regular" or not decided(g):
            continue
        for me, my, opp, op_pts in ((g["a"], g["a_pts"], g["b"], g["b_pts"]), (g["b"], g["b_pts"], g["a"], g["a_pts"])):
            s = t[me]
            s["name"] = g["a_name"] if me == g["a"] else g["b_name"]
            s["gp"] += 1
            if g["winner"] is None:
                s["ti"] += 1
            elif g["winner"] == me:
                s["w"] += 1
            else:
                s["l"] += 1
            if scored(g):
                s["gs"] += 1
                s["pf"] += my
                s["pa"] += op_pts
    order = sorted(t.items(), key=lambda kv: (-pct(kv[1]["w"], kv[1]["l"], kv[1]["ti"], 9), -kv[1]["pf"]))
    rows = []
    for seed, (fr, s) in enumerate(order, 1):
        place = placing.get(fr)
        if complete and place is None:
            place = seed  # outside the title bracket: regular-season order
        rows.append([season, seed, fr, s["name"], s["gp"], s["gs"], s["w"], s["l"], s["ti"],
                     pct(s["w"], s["l"], s["ti"]), round(s["pf"], 2), round(s["pa"], 2), round(s["pf"] - s["pa"], 2),
                     round(s["pf"] / s["gs"], 2) if s["gs"] else 0, round(s["pa"] / s["gs"], 2) if s["gs"] else 0,
                     place if complete else None, "Yes" if complete and place == 1 else None])
    if complete:
        # placings 5+ follow seed among non-bracket teams
        bracket = {fr for fr in placing}
        rest = [r for r in rows if r[2] not in bracket]
        nxt = max(placing.values()) + 1 if placing else 1
        for r in rest:
            r[15] = nxt
            nxt += 1
    return rows


def team_games(games):
    """One row per team per game, chronological."""
    out = []
    for g in games:
        for me, my, opp, op in ((g["a"], g["a_pts"], g["b"], g["b_pts"]), (g["b"], g["b_pts"], g["a"], g["a_pts"])):
            res = "T" if g["winner"] is None else ("W" if g["winner"] == me else "L")
            out.append(dict(g=g, fr=me, opp=opp, pts=my, opp_pts=op, res=res,
                            name=g["a_name"] if me == g["a"] else g["b_name"]))
    out.sort(key=lambda r: (r["g"]["season"], r["g"]["week"]))
    return out


def compute(games, standings, champions, current):
    dec = [g for g in games if decided(g)]
    tg = team_games(dec)
    frs = sorted({r["fr"] for r in tg})
    complete_seasons = {r[0] for r in standings if r[15] is not None}

    # ---- all-time leaderboard
    titles = defaultdict(int)
    finals = defaultdict(int)
    for c in champions:
        if c[1] and not str(c[1]).startswith("—"):
            titles[c[1]] += 1
            finals[c[1]] += 1
            if c[3]:
                finals[c[3]] += 1
    lb = []
    for fr in frs:
        mine = [r for r in tg if r["fr"] == fr]
        def wlt(rows):
            return (sum(r["res"] == "W" for r in rows), sum(r["res"] == "L" for r in rows), sum(r["res"] == "T" for r in rows))
        a, reg, po = wlt(mine), wlt([r for r in mine if r["g"]["stage"] == "Regular"]), wlt([r for r in mine if r["g"]["stage"] == "Playoff"])
        sc = [r for r in mine if scored(r["g"])]
        pf, pa = sum(r["pts"] for r in sc), sum(r["opp_pts"] for r in sc)
        srows = [r for r in standings if r[2] == fr]
        yrs = [r[0] for r in srows]
        places = [r[15] for r in srows if r[15] is not None]
        po_seasons = len({r["g"]["season"] for r in mine if r["g"]["stage"] == "Playoff"} |
                         {g["season"] for g in games if g["stage"] == "Playoff" and g["status"] == "Not played" and fr in (g["a"], g["b"])})
        done = [r for r in srows if r[0] in complete_seasons]
        best = max(done, key=lambda r: (r[9], r[10]), default=None)
        worst = min(done, key=lambda r: (r[9], r[10]), default=None)
        lb.append([None, fr, titles[fr], finals[fr], po_seasons, len(yrs), min(yrs), max(yrs),
                   rec(*a), pct(*a), rec(*reg), pct(*reg), rec(*po), pct(*po), sum(a), len(sc),
                   round(pf, 2), round(pa, 2), round(pf - pa, 2), round(pf / len(sc), 2) if sc else 0,
                   round(pa / len(sc), 2) if sc else 0, round(statistics.mean(places), 2) if places else None,
                   f"{best[0]} ({rec(best[6], best[7], best[8])})" if best else None,
                   f"{worst[0]} ({rec(worst[6], worst[7], worst[8])})" if worst else None])
    lb.sort(key=lambda r: (-r[2], -r[9]))
    for i, r in enumerate(lb, 1):
        r[0] = i

    # ---- head to head
    pair = defaultdict(lambda: dict(games=0, aw=0, bw=0, t=0, ap=0.0, bp=0.0, margins=[], po=0, first=None, last=None, meetings=[]))
    for g in dec:
        a, b = sorted((g["a"], g["b"]))
        p = pair[(a, b)]
        p["games"] += 1
        if g["winner"] is None:
            p["t"] += 1
        elif g["winner"] == a:
            p["aw"] += 1
        else:
            p["bw"] += 1
        if scored(g):
            ap, bp = (g["a_pts"], g["b_pts"]) if g["a"] == a else (g["b_pts"], g["a_pts"])
            p["ap"] += ap
            p["bp"] += bp
            p["margins"].append(abs(ap - bp))
        p["po"] += g["stage"] == "Playoff"
        p["first"] = g["season"] if p["first"] is None else min(p["first"], g["season"])
        p["last"] = g["season"] if p["last"] is None else max(p["last"], g["season"])
        p["meetings"].append(g)
    h2h = []
    for (a, b), p in sorted(pair.items(), key=lambda kv: (-kv[1]["games"], kv[0])):
        lead = a if p["aw"] > p["bw"] else b if p["bw"] > p["aw"] else "Even"
        h2h.append([a, b, p["games"], rec(p["aw"], p["bw"], p["t"]), p["aw"], p["bw"], p["t"],
                    round(p["aw"] / p["games"], 4), lead, round(p["ap"], 2), round(p["bp"], 2), round(p["ap"] - p["bp"], 2),
                    round(statistics.mean(p["margins"]), 2) if p["margins"] else None, p["po"], p["first"], p["last"]])
    grid = []
    for x in frs:
        row = [x]
        w = l = 0
        for y in frs:
            if x == y:
                row.append(None)
                continue
            a, b = sorted((x, y))
            p = pair.get((a, b))
            if not p:
                row.append(None)
                continue
            xw = p["aw"] if x == a else p["bw"]
            row.append(xw)
            w += xw
            l += p["bw"] if x == a else p["aw"]
        grid.append(row + [w, l, w / (w + l) if w + l else 0])

    # ---- records book
    sg = [g for g in dec if scored(g)]
    stg = [r for r in tg if scored(r["g"])]
    book = []
    def stage_lbl(g):
        return g["stage"].lower()
    for i, r in enumerate(sorted(stg, key=lambda r: -r["pts"])[:5], 1):
        g = r["g"]
        book.append(["Single week", f"Highest team score #{i}", r["pts"], f"{r['fr']} — {g['season']} week {g['week']} ({stage_lbl(g)}) vs {r['opp']} ({num(r['opp_pts'])})"])
    for i, r in enumerate(sorted(stg, key=lambda r: r["pts"])[:5], 1):
        g = r["g"]
        book.append(["Single week", f"Lowest team score #{i}", r["pts"], f"{r['fr']} — {g['season']} week {g['week']} ({stage_lbl(g)}) vs {r['opp']} ({num(r['opp_pts'])})"])
    def wl(g):
        if g["winner"] == g["a"]:
            return g["a"], g["a_pts"], g["b"], g["b_pts"]
        return g["b"], g["b_pts"], g["a"], g["a_pts"]
    won = [g for g in sg if g["winner"]]
    for i, g in enumerate(sorted(won, key=lambda g: (-round(abs(g["a_pts"] - g["b_pts"]), 2), g["season"], g["week"]))[:5], 1):
        w, wp, l, lp = wl(g)
        book.append(["Margins", f"Biggest blowout #{i}", round(wp - lp, 2), f"{g['season']} wk {g['week']}: {w} {num(wp)} def. {l} {num(lp)}"])
    for i, g in enumerate(sorted(won, key=lambda g: (round(abs(g["a_pts"] - g["b_pts"]), 2), g["season"], g["week"]))[:5], 1):
        w, wp, l, lp = wl(g)
        book.append(["Margins", f"Closest game #{i}", round(wp - lp, 2), f"{g['season']} wk {g['week']}: {w} {num(wp)} def. {l} {num(lp)}"])
    for i, g in enumerate(sorted(sg, key=lambda g: (-round(g["a_pts"] + g["b_pts"], 2), g["season"], g["week"]))[:5], 1):
        book.append(["Shootouts", f"Highest combined score #{i}", round(g["a_pts"] + g["b_pts"], 2), f"{g['season']} wk {g['week']}: {g['a']} {num(g['a_pts'])} vs {g['b']} {num(g['b_pts'])}"])
    for i, g in enumerate(sorted(sg, key=lambda g: (round(g["a_pts"] + g["b_pts"], 2), g["season"], g["week"]))[:3], 1):
        book.append(["Shootouts", f"Lowest combined score #{i}", round(g["a_pts"] + g["b_pts"], 2), f"{g['season']} wk {g['week']}: {g['a']} {num(g['a_pts'])} vs {g['b']} {num(g['b_pts'])}"])
    done_rows = [r for r in standings if r[0] in complete_seasons]
    for i, r in enumerate(sorted(done_rows, key=lambda r: -r[10])[:5], 1):
        book.append(["Season", f"Most points in a season #{i}", r[10], f"{r[2]} — {r[0]} ({rec(r[6], r[7], r[8])})"])
    for i, r in enumerate(sorted(done_rows, key=lambda r: (-r[9], -r[10]))[:5], 1):
        book.append(["Season", f"Best regular season #{i}", rec(r[6], r[7], r[8]), f"{r[2]} — {r[0]} ({num(r[10])} pts)"])
    for i, r in enumerate(sorted(done_rows, key=lambda r: (r[9], r[10]))[:5], 1):
        book.append(["Season", f"Worst regular season #{i}", rec(r[6], r[7], r[8]), f"{r[2]} — {r[0]} ({num(r[10])} pts)"])
    for i, r in enumerate(sorted(done_rows, key=lambda r: -r[13])[:3], 1):
        book.append(["Season", f"Best points per game #{i}", r[13], f"{r[2]} — {r[0]}"])
    streaks = {"W": [], "L": []}
    for fr in frs:
        mine = [r for r in stg if r["fr"] == fr]
        for res, grp in groupby(mine, key=lambda r: r["res"]):
            grp = list(grp)
            if res in streaks:
                streaks[res].append((len(grp), grp[0]["g"]["season"], grp[0]["g"]["week"], fr, grp[0]["g"], grp[-1]["g"]))
    for res, lbl in (("W", "win"), ("L", "loss")):
        for i, s in enumerate(sorted(streaks[res], key=lambda s: (-s[0], s[1], s[2]))[:5], 1):
            book.append(["Streaks", f"Longest {lbl} streak #{i}", s[0], f"{s[3]} — {s[4]['season']} wk {s[4]['week']} to {s[5]['season']} wk {s[5]['week']}"])
    if h2h:
        m = h2h[0]
        book.append(["Rivalries", "Most-played matchup", m[2], f"{m[0]} vs {m[1]} ({m[3]})"])
        ten = [r for r in h2h if r[2] >= 10]
        lop = max(ten, key=lambda r: (abs(r[7] - 0.5), r[2]))
        book.append(["Rivalries", "Most lopsided (10+ games)", lop[3], f"{lop[0]} vs {lop[1]} — {lop[8]} leads"])
        tight = min(ten, key=lambda r: (abs(r[4] - r[5]), r[12] or 0))
        book.append(["Rivalries", "Tightest rivalry (10+ games)", tight[3], f"{tight[0]} vs {tight[1]} — avg margin {num(tight[12])}"])

    # ---- team names
    nm = defaultdict(set)
    latest = {}
    for r in tg:
        nm[(r["fr"], r["name"])].add(r["g"]["season"])
    for (fr, n), ys in nm.items():
        if fr not in latest or max(ys) > latest[fr][1]:
            latest[fr] = (n, max(ys))
    names = []
    for (fr, n), ys in sorted(nm.items(), key=lambda kv: (kv[0][0], min(kv[1]))):
        names.append([fr, n, seasons_str(ys), len(ys), "Yes" if latest[fr][0] == n else None])

    return dict(leaderboard=lb, h2h=h2h, grid=grid, frs=frs, book=book, names=names, pair=pair, tg=tg)


# ---------------------------------------------------------------- write workbook
def write_table(ws, rows, ncols=None, first=FIRST):
    ncols = ncols or max((len(r) for r in rows), default=ws.max_column)
    tmpl = [copy(ws.cell(first, c)._style) for c in range(1, ncols + 1)]
    old_max = ws.max_row
    for r in range(first, max(old_max, first + len(rows)) + 1):
        for c in range(1, max(ncols, ws.max_column) + 1):
            ws.cell(r, c).value = None
    for i, row in enumerate(rows):
        for c, v in enumerate(row, 1):
            cell = ws.cell(first + i, c)
            cell.value = v
            if c <= len(tmpl):
                cell._style = copy(tmpl[c - 1])
    if ws.auto_filter.ref:
        last_col = openpyxl.utils.get_column_letter(ncols)
        ws.auto_filter.ref = f"A{HEADER_ROW}:{last_col}{first + len(rows) - 1}"


def matchup_rows(games):
    rows = []
    for g in sorted(games, key=lambda g: (-g["season"], -g["week"], g["a"])):
        sc = scored(g)
        rows.append([g["season"], g["week"], g["stage"], g["status"], g["a"], g["a_name"],
                     g["a_pts"], g["b"], g["b_name"], g["b_pts"], g["winner"] if decided(g) else None,
                     round(abs(g["a_pts"] - g["b_pts"]), 2) if sc else None,
                     round(g["a_pts"] + g["b_pts"], 2) if sc else None])
    return rows


def write_workbook(wb, games, standings, champions, res, sleeper, generated):
    write_table(wb["All Matchups"], matchup_rows(games), 13)
    write_table(wb["Season Standings"], sorted(standings, key=lambda r: (-r[0], r[1])), 17)
    write_table(wb["Champions"], champions, 9)
    write_table(wb["All-Time Records"], res["leaderboard"], 24)
    write_table(wb["Head-to-Head Records"], res["h2h"], 16)
    write_table(wb["Records Book"], res["book"], 4)
    write_table(wb["Team Name History"], res["names"], 5)

    g = wb["Head-to-Head Grid"]
    hdr = ["Wins →"] + res["frs"] + ["W", "L", "Win %"]
    for c, v in enumerate(hdr, 1):
        g.cell(HEADER_ROW, c).value = v
    write_table(g, res["grid"], len(hdr))

    n_dec = sum(decided(x) for x in games)
    n_ch = sum(1 for c in champions if c[1] and not str(c[1]).startswith("—"))
    last = max(games, key=lambda x: (x["season"], x["week"]) if decided(x) else (0, 0))
    wb["All Matchups"]["A3"] = (f"{len(games):,} rows, one per game. {n_dec:,} have a result. "
                                f"Rows marked \"In progress\" or \"Not played\" are excluded from every total. "
                                f"2026 onward comes from Sleeper and refreshes weekly.")
    wb["Head-to-Head Records"]["A3"] = (f"{len(res['h2h'])} pairings that have met at least once, sorted by games played. "
                                        "Records include every decided game; points and average margin cover scored games only.")
    for s in sleeper:
        if not s["complete"]:
            wb["Season Standings"]["A3"] = (wb["Season Standings"]["A3"].value.split(" Sleeper:")[0] +
                                            f" Sleeper: {s['season']} is in progress, through week {s['done_reg']}; placings fill in when the playoffs finish.")
    # README
    rd = wb["README"]
    first_season = min(x["season"] for x in games)
    rd["B3"] = (f"NFL.com 2012–2025 · ESPN 2025 placings · Sleeper 2026 onward · "
                f"{len({x['season'] for x in games})} seasons · {n_dec:,} games · {n_ch} champions")
    lines = [rd.cell(r, 2).value for r in range(1, rd.max_row + 1)]
    marker = "• Sleeper (2026 onward):"
    if not any(isinstance(v, str) and v.startswith(marker) for v in lines):
        src = next(r for r in range(1, rd.max_row + 1) if rd.cell(r, 2).value == "Source")
        rd.insert_rows(src, 2)
        for k in (0, 1):
            rd.cell(src + k, 2)._style = copy(rd.cell(src - 1, 2)._style)
            rd.row_dimensions[src + k].height = rd.row_dimensions[src - 1].height
        rd.cell(src, 2).value = (marker + " pulled every Tuesday at 4pm Sydney time by a GitHub Action in "
                                 "mebs1992/nfl-fantasy-dashboard. Sleeper teams are matched to franchises by manager "
                                 "account (sleeper/franchise_map.csv), so renames follow the franchise.")
        rd.cell(src + 1, 2).value = ("• Sleeper playoffs: only championship-bracket games count as Playoff games; "
                                     "consolation games are left out, matching the NFL.com era.")
    for r in range(1, rd.max_row + 1):
        v = rd.cell(r, 2).value
        if isinstance(v, str) and ", 1,300 of them." in v:
            rd.cell(r, 2).value = v.replace(", 1,300 of them.", f", {len(games):,} of them.")
        if isinstance(v, str) and v.startswith("• Workbook generated"):
            rd.cell(r, 2).value = f"• Workbook generated {generated} (latest result: {last['season']} week {last['week']})."
    OUT.mkdir(exist_ok=True)
    path = OUT / "Sunday_Club_League_History.xlsx"
    wb.save(path)
    return path


# ---------------------------------------------------------------- almanac data
def almanac(games, standings, champions, res, sleeper, generated):
    from almanac_stats import fun_stats  # noqa: E402  (kept separate for readability)
    from features import extra_stats  # noqa: E402
    return dict(
        generated=generated,
        franchises=res["frs"],
        champions=[dict(season=c[0], champion=c[1], score=c[2], runner_up=c[3], third=c[4], record=c[5], seed=c[6]) for c in champions],
        leaderboard=[dict(zip(["rank", "franchise", "titles", "finals", "playoff_seasons", "seasons", "from", "to", "record", "win_pct",
                               "reg", "reg_pct", "po", "po_pct", "games", "games_scored", "pf", "pa", "diff", "ppg", "opp_ppg",
                               "avg_finish", "best", "worst"], r)) for r in res["leaderboard"]],
        standings=[dict(zip(["season", "seed", "franchise", "name", "gp", "gs", "w", "l", "t", "pct", "pf", "pa", "diff", "ppg", "opp_ppg",
                             "place", "champ"], r)) for r in standings],
        h2h=[dict(zip(["a", "b", "games", "record", "aw", "bw", "t", "a_pct", "leads", "ap", "bp", "diff", "avg_margin", "po", "first", "last"], r))
             for r in res["h2h"]],
        book=[dict(zip(["category", "record", "value", "detail"], r)) for r in res["book"]],
        names=[dict(zip(["franchise", "name", "seasons", "n", "current"], r)) for r in res["names"]],
        games=[dict(s=g["season"], w=g["week"], st=g["stage"][0], a=g["a"], an=g["a_name"], ap=g["a_pts"], b=g["b"], bn=g["b_name"],
                    bp=g["b_pts"], win=g["winner"], sc=scored(g)) for g in games if decided(g)],
        fun=fun_stats(games, standings, champions, res, sleeper),
        x=extra_stats(games, standings, champions, res, sleeper),
    )


def main():
    fmap = {}
    with open(HERE / "franchise_map.csv", newline="") as f:
        for r in csv.DictReader(f):
            fmap[r["sleeper_user_id"]] = r["franchise"]
    wb, games, standings, champions = load_base()
    sleeper = load_sleeper(fmap)
    for s in sleeper:
        games += s["games"]
        standings += standings_for(s["season"], s["games"], s["placing"], s["complete"])
        if s["complete"]:
            title = next((g for g in s["games"] if g["stage"] == "Playoff" and g["winner"] and s["placing"].get(g["winner"]) == 1
                          and s["placing"].get(g["b"] if g["winner"] == g["a"] else g["a"]) == 2), None)
            champ = next(fr for fr, p in s["placing"].items() if p == 1)
            row = next(r for r in standings if r[0] == s["season"] and r[2] == champ)
            champions.append([s["season"], champ, f"{num(title['a_pts'])} - {num(title['b_pts'])}" if title else None,
                              next(fr for fr, p in s["placing"].items() if p == 2),
                              next((fr for fr, p in s["placing"].items() if p == 3), None),
                              rec(row[6], row[7], row[8]), row[1], s["teams"], "Sleeper"])
        else:
            champions.append([s["season"], "— season in progress —", None, None, None, None, None, s["teams"],
                              f"Sleeper. Regular season through week {s['done_reg']}; playoffs start week {s['pws']}."])
    champions = [c for c in champions if c[0] > BASE_LAST or c[0] not in {x[0] for x in champions if x[0] > BASE_LAST}]
    champions.sort(key=lambda c: -c[0])
    current = sleeper[-1] if sleeper else None
    res = compute(games, standings, champions, current)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = write_workbook(wb, games, standings, champions, res, sleeper, generated)
    data = almanac(games, standings, champions, res, sleeper, generated)
    (OUT / "almanac.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {path} and almanac.json ({sum(decided(g) for g in games)} decided games)")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    main()
