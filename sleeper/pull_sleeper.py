"""Pull the current Sleeper season for The Greatest League (Sunday Club).

Writes raw API responses to sleeper/raw/<season>/ so the build step (and
anyone else) can work offline from what Sleeper returned.

Stdlib only, so the GitHub Action needs no installs for this step.

Season rollover: Sleeper gives each new season a new league ID. If
config.json has no league for the current NFL season, this script looks
through the commissioner's leagues for that season and picks the one whose
previous_league_id points at the last league we know about.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.sleeper.app/v1"
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"


def get(path, retries=3):
    url = f"{API}{path}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "sunday-club-almanac"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise RuntimeError(f"GET {url} failed: {e}") from e
            time.sleep(2 * (attempt + 1))


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def resolve_league(cfg, season):
    leagues = cfg.setdefault("leagues", {})
    if str(season) in leagues:
        return leagues[str(season)]
    known = sorted(leagues.items())
    if not known:
        sys.exit("config.json has no league IDs")
    last_season, last_id = known[-1]
    commish = cfg.get("lookup_user_id")
    if not commish:
        last_users = get(f"/league/{last_id}/users")
        owners = [u["user_id"] for u in last_users if u.get("is_owner")] or [last_users[0]["user_id"]]
        commish = owners[0]
    for lg in get(f"/user/{commish}/leagues/nfl/{season}") or []:
        if str(lg.get("previous_league_id")) == str(last_id):
            leagues[str(season)] = lg["league_id"]
            save(CONFIG, cfg)
            print(f"Found {season} league {lg['league_id']} (renewed from {last_id})")
            return lg["league_id"]
    print(f"No {season} league renewed from {last_id} yet; staying on {last_season}")
    return None


def main():
    cfg = json.loads(CONFIG.read_text())
    state = get("/state/nfl")
    season = int(state.get("league_season") or state["season"])
    league_id = resolve_league(cfg, season)
    if league_id is None:
        return

    out = HERE / "raw" / str(season)
    league = get(f"/league/{league_id}")
    save(out / "state.json", state)
    save(out / "league.json", league)
    save(out / "users.json", get(f"/league/{league_id}/users"))
    save(out / "rosters.json", get(f"/league/{league_id}/rosters"))
    save(out / "winners_bracket.json", get(f"/league/{league_id}/winners_bracket") or [])
    save(out / "losers_bracket.json", get(f"/league/{league_id}/losers_bracket") or [])

    settings = league.get("settings", {})
    last_week = int(settings.get("last_scored_leg") or 0)
    current = int(state.get("week") or 0) if int(state.get("season", 0)) == season else 18
    upto = max(last_week, current)
    upto = min(upto, int(settings.get("playoff_week_start", 15)) + 3, 18)
    for wk in range(1, upto + 1):
        data = get(f"/league/{league_id}/matchups/{wk}")
        if data:
            # Keep the file small: drop per-player points, keep team totals.
            slim = [
                {k: m.get(k) for k in ("roster_id", "matchup_id", "points", "custom_points")}
                for m in data
            ]
            save(out / f"matchups_wk{wk:02d}.json", slim)
    # Which weeks are finished? Sleeper only updates win/loss records a day or so
    # after Monday night. The Action runs Tuesday 4pm Sydney (all games done), so
    # on a Tuesday/Wednesday (UTC) run the current week counts as final once every
    # team has a score. Never go backwards from an earlier run.
    rosters = json.loads((out / "rosters.json").read_text())
    done = max(r["settings"]["wins"] + r["settings"]["losses"] + r["settings"]["ties"] for r in rosters)
    meta_path = out / "meta.json"
    prev = json.loads(meta_path.read_text()).get("final_through", 0) if meta_path.exists() else 0
    final = max(done, prev)
    wk_file = out / f"matchups_wk{current:02d}.json"
    now = datetime.now(timezone.utc)
    if current and wk_file.exists() and now.weekday() in (1, 2):
        pts = [m["points"] or 0 for m in json.loads(wk_file.read_text())]
        if pts and all(p > 0 for p in pts):
            final = max(final, current)
    save(meta_path, {"final_through": final})
    print(f"Pulled {league.get('name')} {season}: weeks 1-{upto}, final through week {final}, status {league.get('status')}")


if __name__ == "__main__":
    main()
