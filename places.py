"""Offline place-name search and historical UTC offsets.

Gazetteer: GeoNames cities with population >= 1000 (geonamescache package, ~170k places),
with coordinates and IANA time zone. Offsets come from the IANA tz database (zoneinfo +
tzdata), which records historical changes (e.g. summer time; London plain GMT in 1850).
Before standard time zones (mostly before ~1880-1900) the database gives Local Mean Time
or an early standard; the app shows the offset it used so the user can override it.
Elevation is not in the gazetteer and defaults to 0 m (editable).
"""
import math
import unicodedata
import datetime as dt
from zoneinfo import ZoneInfo
import geonamescache

_gc = geonamescache.GeonamesCache(min_city_population=1000)
_COUNTRY = {k: v['name'] for k, v in _gc.get_countries().items()}


def _norm(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).casefold().strip()


def _build():
    recs = []
    for c in _gc.get_cities().values():
        alts = [a for a in c.get('alternatenames', []) if a and a.isascii()][:15]
        recs.append(dict(name=c['name'], country=_COUNTRY.get(c['countrycode'], c['countrycode']),
                         lat=float(c['latitude']), lon=float(c['longitude']), tz=c['timezone'],
                         pop=int(c['population']), key=_norm(c['name']),
                         alts=tuple({_norm(a) for a in alts})))
    return recs


PLACES = _build()


def search(query, n=12):
    """Rank: exact name > exact alternate name > name prefix > alternate prefix > substring;
    ties broken by population."""
    q = _norm(query)
    if len(q) < 2:
        return []
    scored = []
    for r in PLACES:
        k = r['key']
        if k == q:
            s = 0
        elif q in r['alts']:
            s = 1
        elif k.startswith(q):
            s = 2
        elif any(a.startswith(q) for a in r['alts']):
            s = 3
        elif len(q) >= 4 and q in k:
            s = 4
        else:
            continue
        scored.append((s, -r['pop'], r))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [r for _, _, r in scored[:n]]


def label(r):
    return f"{r['name']}, {r['country']}  ({r['lat']:.3f}°, {r['lon']:.3f}°; pop. {r['pop']:,})"


def utc_offset_hours(tzname, local_naive):
    """Historical UTC offset (hours) for a local clock time in an IANA zone.
    Returns (offset, note). Ambiguous times (clocks going back) use the first occurrence."""
    z = ZoneInfo(tzname)
    aware = local_naive.replace(tzinfo=z, fold=0)
    off = aware.utcoffset().total_seconds() / 3600
    # detect nonexistent local times (clocks going forward): round-trip check
    back = aware.astimezone(dt.timezone.utc).astimezone(z).replace(tzinfo=None)
    if back != local_naive:
        note = 'this clock time did not exist locally (clocks went forward); pre-change offset used'
    elif aware.replace(fold=1).utcoffset() != aware.utcoffset():
        note = 'ambiguous clock time (clocks went back); first occurrence used'
    else:
        note = ''
    return off, note


_GRID = None


def nearest(lat, lon):
    """(gazetteer place nearest to a position, distance in km). Names the town and time zone of the position
    a device reports ("Use my location" in the profile)."""
    global _GRID
    import numpy as np
    if _GRID is None:
        _GRID = (np.radians([r['lat'] for r in PLACES]), np.radians([r['lon'] for r in PLACES]))
    la, lo = _GRID
    p, l = math.radians(float(lat)), math.radians(float(lon))
    a = np.sin((la - p) / 2) ** 2 + math.cos(p) * np.cos(la) * np.sin((lo - l) / 2) ** 2
    i = int(np.argmin(a))
    return PLACES[i], float(2 * 6371.0088 * math.asin(min(1.0, math.sqrt(float(a[i])))))
