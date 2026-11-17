# Sidereal Chart · Enochian Reading

A Streamlit app that draws an accurate **sidereal chart** and reads it through
John Dee's **Heptarchic (Enochian) system**.

## What it does
- **Astronomy:** topocentric apparent positions of the Sun, Moon and planets from
  NASA JPL **DE440s** (via Skyfield), with the Ascendant and Midheaven.
- **Zodiac:** the real **IAU constellation boundaries** (Delporte 1930) along the
  ecliptic: 13 unequal signs including Ophiuchus. No equal 30° signs or ayanamsa.
- **Enochian layer:** the Heptarchic King and Prince of the day (the day starts at
  sunrise by default; local midnight is an option), the 42 ministers in Dee's and
  James's naming, the Liber Scientiae zodiac Kings, and the Part of the Earth
  governing the chart's location.
- **Forecast:** a summary with strengths and cautions, plus a plain-English
  "What does this mean?" explanation (the app's own paraphrase, not Dee's words).
- Place search over about 170,000 GeoNames places, with automatic historical time zones.
- Optional user profile (name, picture, birth details, home). On the web it is
  kept for the browser session only and is not stored on the server.

Dates run from **1850 to 2149**, the range of DE440s.

## Running it
- **Online:** deployed on Streamlit Community Cloud from this repository, with main file `app.py`.
  On first start the app downloads `de440s.bsp` (about 32 MB) from NASA JPL, which
  takes about 45 seconds; later starts are quick.
- **Locally:** `pip install -r requirements.txt`, then `streamlit run app.py`
  from this folder. The working directory must be the app folder.

## Files
| File | Purpose |
|---|---|
| `app.py` | page layout |
| `sidereal_engine.py` | positions, angles, IAU constellation bands |
| `enochian_layer.py` | Heptarchic interpretation rules |
| `chart_wheel.py` | chart wheel drawing |
| `places.py` | place search and time zones |
| `forecast.py`, `plain_forecast.py` | Forecast box and plain-English window |
| `user_profile.py` | user profile |
| `theme.py`, `assets/`, `.streamlit/config.toml` | colours, background and icon |
| `*.csv` | correspondence tables and forecast wording; `uncertainty_log.csv` lists open source questions |

## Sources and credits
Correspondence tables are transcribed from J. Peterson (ed.), *John Dee's Five Books
of Mystery* (2003) and G. James, *The Enochian Evocation of Dr John Dee*. Both are
in copyright, so **please keep this repository private**. The deployed app can still
be shared publicly from Streamlit's sharing settings.

Planetary data: NASA JPL DE440s via Skyfield. Place data: GeoNames (CC BY 4.0).
Time zones: IANA tz database.
