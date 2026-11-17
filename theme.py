"""Aurora theme (text contrast >= 4.5:1 checked over the brightest aurora behind the panels)
 for the app: palette sampled from the user's photograph IMG_0263.CR2
(aurora over snow-covered mountains and spruce at night) and the page CSS.

Palette roles (hex sampled from the photo unless noted):
  night      #1c1b21  page base (darkened night sky)
  panel      #26252c  panels and cards (darkened night sky)
  sky        #3b3a3e  night sky, upper left of the photo
  spruce     #1b1612  treeline
  aurora     #bde188  aurora, brightest 10 % of pixels   -> primary accent
  glow       #e7fd9b  aurora, brightest 1 %              -> headings
  aurora_mid #a0b180  body of the aurora
  aurora_muted #879574 aurora edges                   -> borders, rules
  snow       #c7b9ba  snow on the peaks (95th percentile)
  snow_text  #ece3e6  snow, lifted for body text (derived)
  mist       #cfc8bd  moonlit snow in shadow (#aca69a), lifted for 4.5:1 contrast -> secondary text
  alpenglow  #e0b4c6  pink cast of the snow, saturated (derived) -> off-zodiac flag
"""
import base64, os

PALETTE = {'night': '#1c1b21', 'panel': '#26252c', 'sky': '#3b3a3e', 'spruce': '#1b1612', 'aurora': '#bde188', 'glow': '#e7fd9b', 'aurora_mid': '#a0b180', 'aurora_muted': '#879574', 'snow': '#c7b9ba', 'mist': '#cfc8bd', 'lavender': '#c9b3e0', 'snow_text': '#ece3e6', 'alpenglow': '#e0b4c6'}

WHEEL_THEME = dict(
    fig_bg='none', face=PALETTE['night'], face_alpha=0.82, band_a=PALETTE['sky'], band_b='#4a4850', band_edge=PALETTE['night'],
    band_text=PALETTE['snow_text'], ring=PALETTE['aurora_muted'], ink=PALETTE['snow_text'], grey=PALETTE['mist'],
    up=PALETTE['aurora'], down_face=PALETTE['night'], accent=PALETTE['alpenglow'], label_bg=PALETTE['night'])


def css(bg_path='assets/background.jpg'):
    p = PALETTE
    bg = ''
    if os.path.exists(bg_path):
        b64 = base64.b64encode(open(bg_path, 'rb').read()).decode()
        bg = (f"background-image: linear-gradient(180deg, rgba(20,19,25,0.25) 0%, rgba(20,19,25,0.55) 55%, "
              f"rgba(20,19,25,0.90) 100%), url('data:image/jpeg;base64,{b64}');"
              "background-size: cover; background-position: center top; background-attachment: fixed;")
    return f"""<style>
    .stApp {{ {bg} }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] > div:first-child {{ background: rgba(28,27,33,0.80); backdrop-filter: blur(6px);
        border-right: 1px solid {p['aurora_muted']}55; }}
    .block-container {{ background: rgba(28,27,33,0.50); border-radius: 16px; padding: 2rem 2.2rem 2.5rem;
        margin-top: 1.2rem; backdrop-filter: blur(5px); border: 1px solid {p['aurora_muted']}40; }}
    h1, h2, h3 {{ font-family: Georgia, 'Palatino Linotype', 'Book Antiqua', serif !important;
        color: {p['glow']} !important; letter-spacing: 0.01em; }}
    h1 {{ text-shadow: 0 0 18px {p['aurora']}55; }}
    [data-testid="stMetricValue"] {{ color: {p['aurora']}; font-family: Georgia, serif; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {p['mist']} !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {p['aurora_muted']} !important;
        background: rgba(38,37,44,0.55); }}
    code {{ color: {p['glow']}; background: rgba(189,225,136,0.10); }}
    a {{ color: {p['aurora']}; }}
    </style>"""
