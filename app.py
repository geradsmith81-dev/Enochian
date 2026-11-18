"""Sidereal chart with Enochian (Dee) interpretation, and a ritual calendar of the Heptarchic workings
(pages Today, Month, Year, Watches, Workings, Occasions, How it works, About; modelled on Sky Gahshomar).

Run:  streamlit run app.py      (conda env 'astro'; needs ephem/de440s.bsp and the CSV tables)
"""
import calendar
import datetime as dt
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')

import sidereal_engine as se
import enochian_layer as el
import chart_wheel as cw
import places
import forecast
import theme
import user_profile
import plain_forecast
import os
from zoneinfo import ZoneInfo
from PIL import Image
import enochian_script
import ritual_calendar as rc
import calendar_pages as cp

_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sidereal_enochian_icon.ico')
st.set_page_config(page_title='Sidereal chart · Enochian reading', layout='wide',
                   page_icon=Image.open(_ICON) if os.path.exists(_ICON) else None)
st.markdown(theme.css(), unsafe_allow_html=True)
st.markdown(cp.css(), unsafe_allow_html=True)
# 'Enochian script' (sidebar): the screen spelled in John Dee's Enochian letters; the switch itself stays in English
enochian_script.install_pyplot()           # the chart wheel is re-lettered too
if enochian_script.on():
    st.markdown(enochian_script.css(), unsafe_allow_html=True)



def footer():
    """Credit line at the bottom of every page (user request, Nov 2026)."""
    st.divider()
    st.markdown("<p style='text-align:center; opacity:0.85; font-size:0.9rem; margin:0.2rem 0 0;'>"
                "Developed by Gerad Smith and Kenton Copper</p>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def find_places(q):
    return places.search(q, n=12)


@st.cache_data(show_spinner=False)
def run(utc, lat, lon, elev, convention):
    t, summary, tab = el.interpret(utc, lat, lon, elev, convention)
    _, rows = se.chart(utc, lat, lon, elev)
    asc, mc = se.angles(t, lat, lon)
    bands = se.ecliptic_constellation_bands(t, step=0.05)
    if bands[0][1] == bands[-1][1]:
        bands = bands[1:]
    return summary, tab, rows, bands, asc, mc


# ---------------- inputs ----------------
enochian_script.switch()       # first in the sidebar, always in English, so it is easy to find and switch back
user_profile.sidebar_card()
prof = user_profile.get()
home, birth = prof.get('home'), prof.get('birth')
MODE_NOW, MODE_BIRTH, MODE_PICK = 'Now, where I live', 'My birth chart', 'A date and place I choose'

with st.sidebar:
    st.header('Chart input')
    modes = ([MODE_NOW] if home else []) + [MODE_PICK] + ([MODE_BIRTH] if birth else [])
    mode = st.radio('Chart for', modes, key='chart_mode') if len(modes) > 1 else MODE_PICK
    if len(modes) == 1:
        st.caption('Tip: create your profile (top of this sidebar) to open the chart at your home place and '
                   'to see your birth chart.')

    if mode == MODE_NOW:
        tzname = home['tz']
        now = dt.datetime.now(ZoneInfo(tzname)) if tzname else dt.datetime.now(dt.timezone.utc)
        local_naive = now.replace(tzinfo=None, second=0, microsecond=0)
        d, tm = local_naive.date(), local_naive.time()
        place, lat, lon, elev = f"{home['name']}, {home['country']}", home['lat'], home['lon'], float(home['elev'])
        tz = now.utcoffset().total_seconds() / 3600
        tz_iana = tzname
        st.caption(f"{place} · {local_naive:%d %b %Y, %H:%M} local time (UTC{tz:+.2f}) · "
                   f"{'your device position' if home['src'] == 'gps' else 'from your profile'}")
        st.button('Update to this minute', icon=':material/refresh:', width='stretch')
    elif mode == MODE_BIRTH:
        local_naive = user_profile.birth_local(birth)
        d, tm = local_naive.date(), local_naive.time()
        place, lat, lon, tz = birth['place'], birth['lat'], birth['lon'], float(birth['utc_offset'])
        near_home = home and abs(home['lat'] - lat) < 0.02 and abs(home['lon'] - lon) < 0.02
        elev = float(home['elev']) if near_home else 0.0
        tz_iana = birth.get('tz')
        st.caption(f"{user_profile.birth_text(birth)} · UTC{tz:+.2f}. Change it with Edit profile.")
    else:
        today = dt.date.today()
        st.markdown('**Date**')
        yc, mc_, dc = st.columns([1.3, 1.4, 1])
        year = yc.number_input('Year', min_value=1850, max_value=2149, value=today.year, step=1,
                               help='Type any year from 1850 to 2149 (range of the NASA JPL DE440s data).')
        month = mc_.selectbox('Month', range(1, 13), index=today.month - 1, format_func=lambda m: calendar.month_abbr[m])
        ndays = calendar.monthrange(int(year), int(month))[1]
        if st.session_state.get('day_value', today.day) > ndays:          # e.g. 31 Jan -> Feb keeps the last day
            st.session_state['day_value'] = ndays
        day = dc.number_input('Day', min_value=1, max_value=ndays, step=1, key='day_value',
                              value=None if 'day_value' in st.session_state else today.day)
        d = dt.date(int(year), int(month), int(day))
        tm = st.time_input('Local clock time', dt.time(12, 0), step=60)
        st.subheader('Place')
        manual = st.checkbox('Enter coordinates manually', value=False)
        if not manual:
            q = st.text_input('Search place name', home['name'] if home else 'London', key='chart_search',
                              placeholder='e.g. Mortlake, Kraków, Praha, Třeboň')
            hits = find_places(q)
            if not hits:
                st.warning('No match in the gazetteer (places with population ≥ 1000). Try another spelling '
                           'or enter coordinates manually.')
                st.stop()
            pick = st.selectbox('Matches', range(len(hits)), format_func=lambda i: places.label(hits[i]))
            hit = hits[pick]
            place, lat, lon, tzname = f"{hit['name']}, {hit['country']}", hit['lat'], hit['lon'], hit['tz']
            st.caption(f'{lat:.4f}°, {lon:.4f}° · time zone {tzname}')
        else:
            place = st.text_input('Place label', 'Custom location')
            lat = st.number_input('Latitude (°N)', -90.0, 90.0, 51.5, 0.0001, format='%.4f')
            lon = st.number_input('Longitude (°E)', -180.0, 180.0, 0.0, 0.0001, format='%.4f')
            tzname = None
        is_home = bool(home) and abs(home['lat'] - lat) < 0.02 and abs(home['lon'] - lon) < 0.02
        elev = st.number_input('Elevation (m)', 0.0, 9000.0, float(home['elev']) if is_home else 0.0, 10.0,
                               help='Not in the gazetteer; affects sunrise slightly.')
        local_naive = dt.datetime.combine(d, tm)
        if tzname:
            auto_off, tz_note = places.utc_offset_hours(tzname, local_naive)
            override = st.checkbox(f'Override UTC offset (automatic: {auto_off:+.2f} h)', value=False)
            tz = st.number_input('UTC offset (hours)', -12.0, 14.0, float(auto_off), 0.25) if override else auto_off
            tz_iana = None if override else tzname
            if tz_note:
                st.info(tz_note)
        else:
            tz = st.number_input('UTC offset of that clock (hours)', -12.0, 14.0, 0.0, 0.25)
            tz_iana = None
    st.subheader('Options')
    convention = st.radio('Heptarchic day begins at', ['sunrise', 'midnight'], index=0,
                          help='Dee was never told (Peterson p160, p260). Sunrise is the project default.')
    st.caption('Valid dates 1850–2149 (JPL DE440s). Place data: GeoNames (CC BY 4.0); '
               'time zones: IANA tz database.')

local = dt.datetime.combine(d, tm)
utc_dt = local - dt.timedelta(hours=tz)
utc = (utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, 0)

# ---------------- pages (the ritual calendar is modelled on Sky Gahshomar) ----------------
PAGES = {'Chart': 'Chart', 'Today': 'Today', 'Month': 'Month', 'Year': 'Year', 'Watches': 'Watches',
         'Workings': 'Workings', 'Occasions': 'Occasions', 'How': 'How it works', 'About': 'About'}
RENDER = {'Today': cp.render_today, 'Month': cp.render_month, 'Year': cp.render_year, 'Watches': cp.render_watches,
          'Workings': cp.render_workings, 'Occasions': cp.render_occasions, 'How': cp.render_how,
          'About': cp.render_about}
page = st.radio('Page', list(PAGES), key='page', horizontal=True, format_func=PAGES.get,
                label_visibility='collapsed')
if page != 'Chart':
    _tzi = rc.tzinfo(tz_iana, tz)
    moment = local.replace(tzinfo=dt.timezone(dt.timedelta(hours=tz))).astimezone(_tzi)
    st.title('Ritual calendar · ' + PAGES[page])
    st.caption(f'{place} · the chosen moment {local:%d %b %Y %H:%M} local (UTC{tz:+.2f}) · '
               'times from NASA JPL DE440s via Skyfield, IAU constellation boundaries · change the date, time and '
               'place in the sidebar')
    RENDER[page](dict(lat=float(lat), lon=float(lon), elev=float(elev), tzname=tz_iana, off=float(tz), tz=_tzi,
                      place=place, conv=convention, moment=moment, mode=mode))
    footer()
    st.stop()

summary, tab, rows, bands, asc, mc = run(utc, lat, lon, elev, convention)

# ---------------- header ----------------
who = user_profile.get()['name']
if mode == MODE_BIRTH:
    title = (who + "'s" if who and not who.endswith('s') else (who + "'" if who else 'My')) + ' birth chart'
elif mode == MODE_NOW:
    title = 'The sky now, where ' + (who.split()[0] + ' lives' if who else 'I live')
else:
    title = 'Sidereal chart · Enochian reading'
av = user_profile.avatar_html(64)
if av:
    _a, _b = st.columns([0.07, 0.93], vertical_alignment='center')
    _a.markdown(av, unsafe_allow_html=True)
    _b.title(title)
else:
    st.title(title)
st.caption(f'{place} · {local:%d %b %Y %H:%M} local (UTC{tz:+.2f}) = {utc_dt:%Y-%m-%d %H:%M} UTC · '
           'positions: NASA JPL DE440s via Skyfield (IAU standards), checked against JPL Horizons to <0.12″')

left, right = st.columns([1.15, 1])
with left:
    fig = cw.draw_wheel(rows, bands, f'{place}, {local:%d %b %Y %H:%M}', asc, mc, theme=theme.WHEEL_THEME)
    st.pyplot(fig, width='stretch')

with right:
    m = summary['ministers']
    st.subheader(f"Heptarchic day: {summary['weekday']}")
    c1, c2 = st.columns(2)
    c1.metric('King', summary['day_king'])
    c2.metric('Prince', summary['day_prince'])
    st.write(f"**Realm:** {summary['day_realm']}")
    if summary.get('day_start_utc'):
        st.caption(f"Day began at local sunrise {summary['day_start_utc']} UTC; next sunrise "
                   f"{summary['next_day_start_utc']} UTC · {summary['convention']}")
    else:
        st.caption(summary['convention'])
    st.markdown(f"**Part {summary['part_of_day']} of 6 of the day — ministers**")
    if m['part'] and m['part']['names_dee_letters']:
        st.markdown(f"Dee's letters: `{m['part']['names_dee_letters']}`")
        st.markdown(f"James's names: {m['part']['names_james_rotation']}")
    if m['whole_day']:
        st.markdown(f"Whole-day six (Peterson): `{m['whole_day']['names_dee_letters']}`")

    st.subheader('Part of the Earth (this location)')
    pe = summary['part_of_the_earth']
    if pe['parts']:
        for p in pe['parts']:
            st.markdown(f"**{p['angel']}** — {p['country']} ({p['modern_identification']}) · Aethyr **{p['aire']}** · "
                        f"{p['ministers']} ministers · King {p['zodiac_king']} ({p['sign']}) · tribe {p['tribe']} · face {p['quarter']}")
    st.caption(pe['status'])

fc = forecast.build(summary, tab)


@st.dialog('What does this mean?', width='large')
def plain_dialog(sections, header):
    plain_forecast.show(sections)
    st.download_button('Download this explanation (.txt)', header + '\n\n' + plain_forecast.as_text(sections),
                       file_name=f"forecast_explained_{local:%Y%m%d_%H%M}.txt", mime='text/plain', on_click='ignore')


st.subheader('Forecast')
with st.container(border=True):
    st.markdown(fc['summary'])
    st.markdown('**Strengths**')
    st.markdown('\n'.join(f'- {x}' for x in fc['strengths']) if fc['strengths'] else '_None under the current rules._')
    st.caption(fc['note'])
    b1, b2 = st.columns(2)
    if b1.button('What does this mean?', icon=':material/lightbulb:', type='primary', width='stretch',
                 key='plain_btn'):
        plain_dialog(plain_forecast.build(summary, fc, utc_dt, lon, tz),
                     f"{place} · {local:%d %b %Y %H:%M} local (UTC{tz:+.2f})")
    b2.download_button('Download forecast (.txt)',
                       forecast.as_text(fc, header=f"{place} · {local:%d %b %Y %H:%M} local (UTC{tz:+.2f})"),
                       file_name=f"forecast_{local:%Y%m%d_%H%M}.txt", mime='text/plain', width='stretch')

st.subheader('Bodies')
show = tab.rename(columns={'body': 'Body', 'ecl_lon': 'Ecl. long. (°)', 'iau_constellation': 'IAU constellation',
                           'above_horizon': 'Above horizon', 'heptarchic_king': 'Heptarchic King',
                           'heptarchic_prince': 'Prince', 'king_planet': 'Planet (Dee table)',
                           'zodiac_king': 'Zodiac King', 'tribe': 'Tribe', 'quarter': 'Face'})
cols = [c for c in ['Body', 'Ecl. long. (°)', 'IAU constellation', 'Above horizon', 'Heptarchic King', 'Prince',
                    'Planet (Dee table)', 'Zodiac King', 'Tribe', 'Face'] if c in show]
enochian_script.table(show[cols])

with st.expander('Sources and certainty'):
    st.markdown('Each statement is tagged **sourced**, **inferred**, or **app design rule**. '
                'Sources: Peterson, *John Dee\'s Five Books of Mystery*; James, *The Enochian Evocation of Dr John Dee*; '
                'Skinner, introduction to *Dr John Dee\'s Spiritual Diary*.')
    enochian_script.table(pd.read_csv('uncertainty_log.csv', encoding='utf-8'))

footer()
