"""art/build.py: draws every picture of James and John's Coworking Space from one set of parts, so the room, the people
and the ink are the same hand in every scene. Run it from the space's folder (python art/build.py); it writes:

  art.svg                the dashboard's still (the idle scene)
  art/<scene>.svg        one scene per stage of a run, which the dashboard swaps in as the run moves:
                         idle, tim (a direction arrives: Tim walks in with the memo), reading, flowchart (RUN.md: James
                         at the run board), consulting (John makes his one call), spec (the prompts: John at the terminal,
                         the spec coming off the printer), done (a toast), failed
  art/door.svg           the two of them for the office door: the CTO and the Chief Engineer, side by side
  mark.svg               the pair, two colleagues each in their own half (the office floor shows it as their avatar)
  art/james.svg, art/john.svg   one avatar each

Owner 2026-10-07 ~22:40 CDT, a ground-up redesign that scraps the lounge look: "recreate them like a 1980s Software
Startup setting, working in an executive office, both in dress shirt, tie, rolled up sleeves, a couple glasses with brown
liquid in them, a couple cigars on the table, and still some boxes of chinese takeout food. Think Mad Men meets Scooby Doo
cartoon art style. And redesign James and John to resemble like a CTO and Chief Engineer, not like 2 partners living
together in an apartment. Really need to land the coworking and leadership elements more."

Style: Saturday-morning cel on a painted background. The room is flat painted shapes with a thin brown line and no black
ink (walnut panelling, the city at night through the blinds, the run board, the org chart with the CTO and the Chief
Engineer at the top, the partners' desk with both their nameplates). The people and everything they touch are cels:
heavy warm-black ink, flat colour, eyes as white ovals with dot pupils. Arms are outlined tubes (one ink stroke under one
colour stroke), so every pose is drawn by the same hand. Colour by fill and stroke attributes only. Classes (tim, walk,
bubble, draw, scribble, tap, smoke, ember, type, cursor, feed, head, blink, twinkle, minute, flash) are hooks the
dashboard's CSS animates; with no CSS every scene is a complete still. Two colleagues at work, never a likeness of anyone
real.
"""
import math
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(HERE)

INK = '#17110D'      # the cel ink
LINE = '#2B1B10'     # the background painter's line
TYPE = "'Courier Prime', 'Courier New', Courier, monospace"

# the people
SKIN_JAMES, SKIN_JAMES_DK = '#D6A07C', '#B98461'
SKIN_JOHN, SKIN_JOHN_DK = '#9C6B4E', '#7E5338'
SKIN_TIM = '#EBC4A0'
SHIRT_JAMES, SHIRT_JAMES_DK = '#F7F3EA', '#DCD6C8'
SHIRT_JOHN, SHIRT_JOHN_DK = '#BFD3E6', '#9FB7CE'
TIE_JAMES, TIE_JOHN = '#A8322B', '#C8962E'
BRACES = '#2B3A63'
TROUSERS_JAMES = '#3A3E48'
HAIR_JAMES, HAIR_JOHN, BEARD_JOHN, HAIR_TIM = '#2A211C', '#1C1612', '#231C18', '#6B3E26'
WHISKY, WHISKY_DK, GLASS = '#A9651F', '#7E4716', '#E4EEEC'
MANILA, MANILA_DK = '#E6C47C', '#C9A55C'


def f(n):
    """A number for a path: one decimal, no trailing zero."""
    s = f'{n:.1f}'
    return s[:-2] if s.endswith('.0') else s


def pts(*ps):
    return ' L'.join(f'{f(x)},{f(y)}' for x, y in ps)


def tube(points, w, fill, ow=2.4, ink=INK):
    """An outlined tube along a polyline: (the ink stroke, the colour stroke). Draw every ink before every colour."""
    d = 'M' + pts(*points)
    return (f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{f(w + 2 * ow)}" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def arm(S, E, H, shirt, skin, hand=True, ow=2.4, cls=None, hold=''):
    """A shirt-sleeved arm, sleeve rolled to the elbow: shoulder S, elbow E, hand H. `hold` is drawn in the hand."""
    sleeve = tube([S, E], 14, shirt, ow)
    fore_start = lerp(E, H, 0.12)
    fore = tube([fore_start, H], 9.5, skin, ow)
    cuff_end = lerp(E, H, 0.30)
    cuff = tube([lerp(E, H, 0.04), cuff_end], 15.5, shirt, ow)
    # the fold of the rolled cuff
    ux, uy = H[0] - E[0], H[1] - E[1]
    L = math.hypot(ux, uy) or 1
    nx, ny = -uy / L * 7, ux / L * 7
    m = lerp(E, H, 0.17)
    fold = f'<path d="M{f(m[0] + nx)},{f(m[1] + ny)} L{f(m[0] - nx)},{f(m[1] - ny)}" fill="none" stroke="{INK}" stroke-width="1.3"/>'
    s = f'<g class="{cls}">' if cls else '<g>'
    s += sleeve[0] + fore[0] + sleeve[1] + fore[1] + cuff[0] + cuff[1] + fold
    s += hold
    if hand:
        s += f'<circle cx="{f(H[0])}" cy="{f(H[1])}" r="6.2" fill="{skin}" stroke="{INK}" stroke-width="{ow}"/>'
    return s + '</g>\n'


# ======================================================================================== the room (painted, no ink)
def lcg(seed):
    while True:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        yield seed / 0x7FFFFFFF


def wall():
    r = lcg(7)
    s = '  <g class="room">\n'
    s += '    <rect width="640" height="272" fill="#6B472C"/>\n'
    # the walnut boards: a seam every 46px, two strokes of grain on each, a lighter board now and then
    for i, x in enumerate(range(0, 640, 46)):
        if i % 3 == 1:
            s += f'    <rect x="{x}" y="8" width="46" height="252" fill="#704B2F"/>\n'
        for _ in range(2):
            gx = x + 8 + next(r) * 30
            y0 = 14 + next(r) * 60
            y1 = y0 + 90 + next(r) * 120
            bend = (next(r) - 0.5) * 10
            s += f'    <path d="M{f(gx)},{f(y0)} C{f(gx + bend)},{f(y0 + 40)} {f(gx - bend)},{f(y1 - 40)} {f(gx + bend / 2)},{f(y1)}" fill="none" stroke="#7A5536" stroke-width="1.6" stroke-linecap="round"/>\n'
        s += f'    <rect x="{x - 1}" y="8" width="2" height="252" fill="#4B301C"/>\n'
    s += '    <rect width="640" height="9" fill="#4A2F1C"/><rect y="9" width="640" height="2" fill="#86613F"/>\n'
    s += '    <rect y="256" width="640" height="16" fill="#3F2717"/><rect y="256" width="640" height="2" fill="#5E3E25"/>\n'
    # the carpet: deep teal, a darker band at the wall, a few painted dabs
    s += '    <rect y="272" width="640" height="128" fill="#2C5A5D"/>\n'
    s += '    <rect y="272" width="640" height="10" fill="#244B4E"/>\n'
    for _ in range(26):
        x = next(r) * 620
        y = 290 + next(r) * 104
        w = 10 + next(r) * 26
        s += f'    <path d="M{f(x)},{f(y)} l{f(w)},0" stroke="#2F6366" stroke-width="2.2" stroke-linecap="round"/>\n'
    return s + '  </g>\n'


def window():
    r = lcg(31)
    s = f'  <g class="window" stroke="{LINE}" stroke-width="1.3">\n'
    s += '    <rect x="398" y="24" width="224" height="190" fill="#4E321D"/>\n'
    # the night in flat bands
    for y, h, c in ((32, 50, '#221C42'), (82, 40, '#2E2554'), (122, 36, '#463163'), (158, 48, '#6A3F62')):
        s += f'    <rect x="406" y="{y}" width="208" height="{h}" fill="{c}" stroke="none"/>\n'
    s += '    <circle cx="590" cy="104" r="10" fill="#F2E6C4" stroke="none"/><circle cx="595" cy="100" r="8.5" fill="#2E2554" stroke="none"/>\n'
    for x, y in ((430, 96), (466, 112), (540, 92), (612 - 30, 128), (452, 140), (520, 124)):
        s += f'    <circle cx="{x}" cy="{y}" r="1.1" fill="#F3E9C6" stroke="none"/>\n'
    # the skyline: back row, front row, a water tower, lit windows (some twinkle)
    back = [(406, 150), (424, 132), (446, 158), (470, 120), (494, 146), (518, 128), (548, 152), (572, 136), (596, 156)]
    for i, (x, top) in enumerate(back):
        w = (back[i + 1][0] if i + 1 < len(back) else 614) - x
        s += f'    <rect x="{x}" y="{top}" width="{w}" height="{206 - top}" fill="#1E2040" stroke="none"/>\n'
    front = [(406, 172, 22), (432, 160, 26), (466, 176, 20), (492, 154, 30), (530, 170, 24), (560, 162, 28), (594, 178, 20)]
    for x, top, w in front:
        s += f'    <rect x="{x}" y="{top}" width="{w}" height="{206 - top}" fill="#15172E" stroke="none"/>\n'
        for wy in range(top + 6, 202, 8):
            for wx in range(x + 4, x + w - 4, 7):
                v = next(r)
                if v < 0.42:
                    cls = ' class="twinkle"' if v < 0.05 else ''
                    s += f'    <rect{cls} x="{wx}" y="{wy}" width="3" height="4" fill="{"#F2C14E" if v > 0.12 else "#E89B3A"}" stroke="none"/>\n'
    s += '    <path d="M500,154 L500,144 L506,140 L512,144 L512,154 Z M502,154 L501,160 M510,154 L511,160" fill="#15172E" stroke="#15172E" stroke-width="1.4"/>\n'
    s += '    <rect x="507" y="32" width="6" height="174" fill="#4E321D"/>\n'
    # the venetian blinds, raised a third of the way, and the cord
    s += '    <rect x="406" y="32" width="208" height="52" fill="#D7C49B" stroke="none"/>\n'
    for y in range(37, 84, 5):
        s += f'    <path d="M406,{y} L614,{y}" stroke="#9C875E" stroke-width="1.2"/>\n'
    s += '    <rect x="404" y="82" width="212" height="6" fill="#C2AE84"/>\n'
    s += '    <path d="M604,88 L604,150" stroke="#E8DCC0" stroke-width="1.2"/><rect x="601.5" y="150" width="5" height="9" rx="2" fill="#C2AE84"/>\n'
    s += '    <rect x="392" y="206" width="236" height="9" fill="#8A5E38"/><rect x="392" y="206" width="236" height="2" fill="#A97A4C" stroke="none"/>\n'
    return s + '  </g>\n'


# The run board on the left wall: a whiteboard in an aluminium frame. Its content changes with the run.
def board(stage):
    s = f'  <g class="board" stroke="{LINE}" stroke-width="1.3">\n'
    s += '    <rect x="22" y="38" width="200" height="162" rx="2" fill="#B5BAC0"/>\n'
    s += '    <rect x="28" y="44" width="188" height="150" fill="#F4F1E7"/>\n'
    s += '    <rect x="36" y="198" width="172" height="6" fill="#9EA4AA"/>\n'
    for x, c in ((60, '#1F4E8C'), (76, '#B23A2E'), (92, '#2E7D4F')):
        s += f'    <rect x="{x}" y="194" width="13" height="4" rx="1.5" fill="{c}" stroke-width="0.8"/>\n'
    s += f'    <text x="36" y="58" font-family="{TYPE}" font-size="10" font-weight="700" letter-spacing="1" fill="#1F4E8C" stroke="none">RUN BOARD</text>\n'
    s += '    <path d="M36,62 L102,62" stroke="#1F4E8C" stroke-width="1.4"/>\n'
    if stage in ('idle', 'tim', 'reading'):
        s += roadmap()
    elif stage == 'flowchart':
        s += flowchart(True)
    elif stage == 'done':
        s += flowchart(False) + pinned()
    else:
        s += flowchart(False)
    return s + '  </g>\n'


def roadmap():
    """Before a run: last quarter's roadmap, a Gantt in three markers."""
    s = f'    <g stroke="none" font-family="{TYPE}" font-size="7" font-weight="700" fill="#4A4A4A">\n'
    for i, (lbl, x, w, c) in enumerate((('Q1', 60, 70, '#1F4E8C'), ('Q2', 92, 64, '#B23A2E'), ('Q3', 120, 76, '#2E7D4F'), ('Q4', 150, 52, '#1F4E8C'))):
        y = 76 + i * 26
        s += f'      <text x="36" y="{y + 6}">{lbl}</text><rect x="{x}" y="{y}" width="{w}" height="8" rx="2" fill="{c}"/>\n'
    s += '    </g>\n'
    s += '    <path d="M58,176 L208,176 M58,70 L58,180" stroke="#7C7C7C" stroke-width="1"/>\n'
    return s


def flowchart(draw):
    """The run, drawn as it is composed: three lanes into the gate, the gate into main. `draw`: it draws itself."""
    k = (lambda i: f' class="draw d{i}"') if draw else (lambda i: '')
    blue, red, green = '#1F4E8C', '#B23A2E', '#2E7D4F'
    s = '    <g fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n'
    for i, y in enumerate((74, 104, 134)):
        s += f'      <rect{k(1 + i)} x="38" y="{y}" width="38" height="20" rx="3" stroke="{blue}"/>\n'
        s += f'      <path{k(4 + i)} d="M76,{y + 10} C96,{y + 10} 100,{116 if y != 104 else 114} 116,114" stroke="{blue}"/>\n'
    s += f'      <path{k(7)} d="M116,114 L136,98 L156,114 L136,130 Z" stroke="{red}"/>\n'
    s += f'      <path{k(8)} d="M156,114 L170,114 M166,110 L170,114 L166,118" stroke="{red}"/>\n'
    s += f'      <rect{k(9)} x="172" y="102" width="38" height="24" rx="3" stroke="{green}"/>\n'
    s += f'      <path{k(10)} d="M42,80 L66,80 M42,86 L58,86 M42,110 L68,110 M42,116 L56,116 M42,140 L64,140 M42,146 L60,146 M178,110 L202,110 M178,117 L196,117" stroke="#5A6A80" stroke-width="1.3"/>\n'
    s += '    </g>\n'
    s += f'    <g stroke="none" font-family="{TYPE}" font-size="7" font-weight="700">\n'
    s += f'      <text x="128" y="117" fill="{red}">G</text><text x="176" y="138" fill="{green}">MAIN</text>\n'
    s += '    </g>\n'
    return s


def pinned():
    """Done: the composed run pinned to the board, ticked off, with the rubber stamp."""
    return (f'    <g stroke="{INK}" stroke-width="1">\n'
            '      <path d="M150,140 L210,136 L212,188 L152,192 Z" fill="#FFFFFF"/>\n'
            '      <circle cx="180" cy="139" r="2.6" fill="#B23A2E"/>\n'
            '      <path d="M158,152 L161,155 L166,149 M158,163 L161,166 L166,160 M158,174 L161,177 L166,171" fill="none" stroke="#2E7D4F" stroke-width="1.6"/>\n'
            '      <path d="M170,152 L204,150 M170,163 L200,161 M170,174 L204,172" fill="none" stroke="#9A9A9A" stroke-width="1.2"/>\n'
            '      <g transform="rotate(-12 182 182)"><rect x="160" y="175" width="44" height="13" rx="2" fill="none" stroke="#B23A2E" stroke-width="1.6"/>\n'
            f'      <text x="182" y="185" text-anchor="middle" font-family="{TYPE}" font-size="8" font-weight="700" fill="#B23A2E" stroke="none">COMPOSED</text></g>\n'
            '    </g>\n')


def org_chart():
    """The leadership: the CTO at the top, his Chief Engineer under him, Tim beside, five department heads below."""
    s = f'  <g class="org" stroke="{LINE}" stroke-width="1.2">\n'
    s += '    <rect x="240" y="42" width="154" height="112" fill="#B8893A"/>\n'
    s += '    <rect x="245" y="47" width="144" height="102" fill="#EFE6CE"/>\n'
    t = f'font-family="{TYPE}" font-weight="700" text-anchor="middle" fill="#3A2A18" stroke="none"'
    s += f'    <text x="317" y="57" font-size="6" letter-spacing="1.2" {t}>ORGANIZATION</text>\n'
    s += '    <path d="M317,76 L317,84 M317,98 L317,106 M262,106 L372,106 M262,106 L262,112 M289.5,106 L289.5,112 M317,106 L317,112 M344.5,106 L344.5,112 M372,106 L372,112 M292,69 L282,69" fill="none" stroke="#3A2A18" stroke-width="1"/>\n'
    s += '    <rect x="292" y="62" width="50" height="14" fill="#D9A441"/>\n'
    s += f'    <text x="317" y="72" font-size="8" {t}>CTO</text>\n'
    s += '    <rect x="280" y="84" width="74" height="14" fill="#D9A441"/>\n'
    s += f'    <text x="317" y="93.5" font-size="6" {t}>CHIEF ENGINEER</text>\n'
    s += '    <rect x="252" y="63" width="30" height="12" fill="#FFF8E6"/>\n'
    s += f'    <text x="267" y="71.5" font-size="5.5" {t}>EA</text>\n'
    for x, lbl in ((262, 'BE'), (289.5, 'FE'), (317, 'DB'), (344.5, 'QA'), (372, 'API')):
        s += f'    <rect x="{x - 11}" y="112" width="22" height="12" fill="#FFF8E6"/>\n'
        s += f'    <text x="{x}" y="120.5" font-size="5.5" {t}>{lbl}</text>\n'
    s += '    <path d="M254,134 L380,134 M254,140 L346,140" fill="none" stroke="#C7B994" stroke-width="1.4"/>\n'
    return s + '  </g>\n'


def clock():
    """Ten to eleven at night. The minute hand moves when the page animates it."""
    cx, cy = 317, 23
    s = f'  <g class="clock" stroke="{LINE}" stroke-width="1.2">\n'
    s += f'    <circle cx="{cx}" cy="{cy}" r="13" fill="#C9A24A"/><circle cx="{cx}" cy="{cy}" r="10.5" fill="#F3EBD6"/>\n'
    for i in range(12):
        a = math.radians(i * 30)
        s += f'    <path d="M{f(cx + 8.6 * math.sin(a))},{f(cy - 8.6 * math.cos(a))} L{f(cx + 10 * math.sin(a))},{f(cy - 10 * math.cos(a))}" stroke="#3A2A18" stroke-width="1"/>\n'
    h, m = math.radians(325), math.radians(300)
    s += f'    <path d="M{cx},{cy} L{f(cx + 5.5 * math.sin(h))},{f(cy - 5.5 * math.cos(h))}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>\n'
    s += f'    <path class="minute" d="M{cx},{cy} L{f(cx + 8.4 * math.sin(m))},{f(cy - 8.4 * math.cos(m))}" stroke="{INK}" stroke-width="1.4" stroke-linecap="round"/>\n'
    s += f'    <circle cx="{cx}" cy="{cy}" r="1.4" fill="{INK}" stroke="none"/>\n'
    return s + '  </g>\n'


def credenza():
    """Against the wall under the org chart: the walnut credenza, the banker's lamp, the spec binders, the decanter."""
    s = '  <ellipse cx="256" cy="204" rx="46" ry="34" fill="#F2D49A" fill-opacity="0.16"/>\n'
    s += f'  <g class="credenza" stroke="{LINE}" stroke-width="1.3">\n'
    s += '    <rect x="234" y="223" width="166" height="44" fill="#5B3A22"/>\n'
    for x in range(240, 398, 6):
        s += f'    <path d="M{x},226 L{x},264" stroke="#664429" stroke-width="2"/>\n'
    s += '    <path d="M289,223 L289,267 M345,223 L345,267" stroke-width="1.6"/>\n'
    for x in (284, 294, 340, 350):
        s += f'    <rect x="{x - 1.5}" y="238" width="3" height="12" rx="1.5" fill="#C9A24A" stroke-width="0.8"/>\n'
    s += '    <path d="M240,267 L243,276 L246,267 Z M388,267 L391,276 L394,267 Z" fill="#3F2717"/>\n'
    s += '    <rect x="228" y="216" width="178" height="7" fill="#7E5634"/>\n'
    # the lamp
    s += '    <ellipse cx="252" cy="215" rx="10" ry="2.8" fill="#C9A24A"/><rect x="250.6" y="196" width="2.8" height="18" fill="#C9A24A" stroke-width="0.8"/>\n'
    s += '    <path d="M236,201 Q252,186 268,201 L266,205 L238,205 Z" fill="#2E6A49"/>\n'
    s += '    <path d="M241,198 Q252,190 263,198" fill="none" stroke="#4E9A70" stroke-width="1.4"/>\n'
    s += '    <path d="M262,205 L262,211" stroke="#C9A24A" stroke-width="1"/>\n'
    # the spec binders
    for i, c in enumerate(('#B23A2E', '#D9A441', '#2F6F73', '#3A3E48')):
        x = 274 + i * 8
        s += f'    <rect x="{x}" y="{193 + (i % 2) * 2}" width="7.5" height="{23 - (i % 2) * 2}" fill="{c}"/><rect x="{x + 1.5}" y="{198 + (i % 2) * 2}" width="4.5" height="5" fill="#EFE6CE" stroke-width="0.6"/>\n'
    # the decanter and a spare glass
    s += f'    <path d="M368,216 C366,207 368,199 374,195 L374,189 L382,189 L382,195 C388,199 390,207 388,216 Z" fill="{GLASS}" fill-opacity="0.55"/>\n'
    s += f'    <path d="M367.6,216 C366.8,211 367.2,207 368.4,204 L387.6,204 C388.8,207 389.2,211 388.4,216 Z" fill="{WHISKY}" stroke="none"/>\n'
    s += f'    <path d="M368,216 C366,207 368,199 374,195 L374,189 L382,189 L382,195 C388,199 390,207 388,216 Z" fill="none"/>\n'
    s += f'    <circle cx="378" cy="186" r="3.6" fill="{GLASS}"/><path d="M372,200 L373,212" stroke="#FFFFFF" stroke-width="1.4" stroke-opacity="0.7"/>\n'
    s += '  </g>\n'
    return s


# ======================================================================================== the desk and what is on it
def glass(x, y, s=1.0, cls=None):
    """A rocks glass, two fingers of whisky and an ice cube; its base centred at (x, y)."""
    c = f' class="{cls}"' if cls else ''
    return (f'<g{c} transform="translate({f(x)} {f(y)}) scale({s})" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">'
            f'<path d="M-7.5,-15 L7.5,-15 L6.5,0 L-6.5,0 Z" fill="{GLASS}" fill-opacity="0.7"/>'
            f'<path d="M-7,-8.5 L7,-8.5 L6.5,-2 L-6.5,-2 Z" fill="{WHISKY}" stroke="none"/>'
            f'<path d="M-6.6,-8.5 L6.6,-8.5" stroke="{WHISKY_DK}" stroke-width="1.4"/>'
            '<rect x="-3.5" y="-12" width="5" height="5" rx="1" fill="#F4FAF9" stroke-width="1" transform="rotate(12 -1 -9.5)"/>'
            '<path d="M-6.5,-2 L6.5,-2" stroke-width="1.2"/>'
            f'<path d="M-7.5,-15 L7.5,-15 L6.5,0 L-6.5,0 Z" fill="none"/>'
            '<path d="M-4.5,-13 L-4,-4" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.8"/></g>')


def pail(x, y, s=1.0, open_=False, sticks=False):
    """A takeout pail, its base centred at (x, y): white folded box, red pagoda, wire handle."""
    g = f'<g transform="translate({f(x)} {f(y)}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
    g += '<path d="M-10,-19 L10,-19 L7,0 L-7,0 Z" fill="#FBF8F0"/>'
    g += '<path d="M3,-19 L10,-19 L7,0 L2,0 Z" fill="#E6E0D2" stroke="none"/>'
    g += '<path d="M-10,-19 L10,-19 L7,0 L-7,0 Z" fill="none"/>'
    if open_:
        g += '<path d="M-10,-19 L-13,-26 L-2,-22 Z M10,-19 L13,-26 L2,-22 Z" fill="#FBF8F0" stroke-width="1.5"/>'
        g += '<path d="M-9,-19 Q0,-24 9,-19" fill="#D9A85E" stroke-width="1.3"/>'
    else:
        g += '<path d="M-10,-19 L0,-27 L10,-19 Z" fill="#FBF8F0" stroke-width="1.5"/>'
        g += '<path d="M-8,-22 Q0,-35 8,-22" fill="none" stroke="#6E737B" stroke-width="1.3"/>'
    g += '<path d="M-4,-8 L4,-8 M-3,-8 L-3,-12 L3,-12 L3,-8 M-5,-12 L0,-16 L5,-12" fill="none" stroke="#B23A2E" stroke-width="1.3"/>'
    if sticks:
        g += '<path d="M1,-20 L10,-40 M4,-20 L15,-38" fill="none" stroke="#C49A62" stroke-width="2"/>'
    return g + '</g>'


def cigar(a, b, cls):
    """A cigar resting on the ashtray: mouth end a, lit end b; ash, ember, and a ribbon of smoke rising off it."""
    s = ''.join(tube([a, b], 4.6, '#6E4024', ow=1.6))
    band = lerp(a, b, 0.32)
    s += f'<circle cx="{f(band[0])}" cy="{f(band[1])}" r="2.7" fill="#D9A441" stroke="{INK}" stroke-width="1"/>'
    ash = lerp(a, b, 0.88)
    s += ''.join(tube([ash, b], 4.6, '#8E8A84', ow=1.2))
    s += f'<circle class="ember" cx="{f(b[0])}" cy="{f(b[1])}" r="2.1" fill="#E86A2E" stroke="none"/>'
    x, y = b
    s += (f'<path class="smoke {cls}" d="M{f(x)},{f(y - 3)} C{f(x - 8)},{f(y - 14)} {f(x + 8)},{f(y - 22)} {f(x)},{f(y - 34)} '
          f'C{f(x - 7)},{f(y - 44)} {f(x + 6)},{f(y - 52)} {f(x + 2)},{f(y - 62)}" fill="none" stroke="#E9E2D6" stroke-width="3.2" '
          'stroke-linecap="round" stroke-opacity="0.6"/>')
    return s


def terminal(stage):
    """The PC on the desk: a beige system unit with two floppy drives, the green screen on top of it."""
    s = f'  <g class="pc" stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <rect x="172" y="291" width="76" height="21" rx="2" fill="#D8CCB0"/>\n'
    s += '    <rect x="204" y="295" width="38" height="13" rx="1" fill="#C4B796" stroke-width="1.3"/>\n'
    s += '    <path d="M207,299 L239,299 M207,305 L239,305" stroke="#2A2620" stroke-width="2"/>\n'
    s += '    <circle cx="181" cy="305" r="1.8" fill="#D9452E" stroke="none"/><path d="M178,297 L196,297 M178,300 L196,300" stroke="#B4A788" stroke-width="1"/>\n'
    s += '    <rect x="178" y="234" width="64" height="57" rx="7" fill="#DCD1B6"/>\n'
    s += '    <path d="M228,236 C238,238 240,244 240,256 L240,286 C240,289 238,290 236,290 L230,290 Z" fill="#C9BD9F" stroke="none"/>\n'
    s += '    <rect x="184" y="240" width="52" height="45" rx="5" fill="#2B2A26"/>\n'
    s += '    <rect x="188" y="244" width="44" height="37" rx="4" fill="#0E1A12" stroke="none"/>\n'
    s += '    <rect x="178" y="234" width="64" height="57" rx="7" fill="none"/>\n'
    s += '    <circle cx="232" cy="288" r="1.4" fill="#4DFF88" stroke="none"/>\n'
    # the phosphor: a few lines of green, the cursor. Reading and spec type their lines in; failed flashes an error.
    g = '#4DFF88'
    lines = [(192, 249, 26), (192, 255, 34), (192, 261, 18), (192, 267, 30)]
    typing = stage in ('reading', 'spec')
    s += '    <g stroke="none">\n'
    for i, (x, y, w) in enumerate(lines):
        cls = f' class="type t{i + 1}"' if typing else ''
        s += f'      <rect{cls} x="{x}" y="{y}" width="{w}" height="2.6" fill="{g}" fill-opacity="0.9"/>\n'
    if stage == 'failed':
        s += f'      <text class="flash" x="192" y="278.5" font-family="{TYPE}" font-size="7" font-weight="700" fill="{g}">?ERROR</text>\n'
    elif stage == 'done':
        s += f'      <text x="192" y="278.5" font-family="{TYPE}" font-size="7" font-weight="700" fill="{g}">OK.</text>\n'
        s += f'      <rect class="cursor" x="208" y="273" width="4" height="6" fill="{g}"/>\n'
    else:
        s += f'      <rect class="cursor" x="192" y="273" width="4" height="6" fill="{g}"/>\n'
    s += '    </g>\n'
    s += '    <path d="M192,246 C200,244 210,244 216,245" fill="none" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="2"/>\n'
    return s + '  </g>\n'


def printer(stage):
    """The dot-matrix printer: green-bar paper standing up behind it, the print head that runs while it prints."""
    s = f'  <g class="printer" stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <path d="M258,296 L258,276 L292,276 L292,296 Z" fill="#FFFFFF" stroke-width="1.4"/>\n'
    s += '    <path d="M260,281 L290,281 M260,287 L290,287" stroke="#BFE3BC" stroke-width="3"/>\n'
    s += '    <path d="M255,312 L252,296 L298,296 L295,312 Z" fill="#D8CCB0"/>\n'
    s += '    <rect x="258" y="298" width="34" height="4" fill="#3A372F" stroke-width="1"/>\n'
    cls = ' class="printhead"' if stage == 'spec' else ''
    s += f'    <rect{cls} x="262" y="297" width="6" height="6" fill="#8A8170" stroke-width="1"/>\n'
    s += '    <path d="M258,307 L268,307" stroke="#B4A788" stroke-width="1"/>\n'
    return s + '  </g>\n'


def printout():
    """Spec: the printout feeding off the front of the desk and folding onto the carpet."""
    s = f'  <g stroke="{INK}" stroke-width="1.4" stroke-linejoin="round">\n'
    s += '    <g class="feed">\n'
    s += '      <path d="M258,318 L292,318 L292,378 L258,378 Z" fill="#FFFFFF"/>\n'
    for y in range(324, 376, 10):
        s += f'      <rect x="262" y="{y}" width="26" height="4" fill="#BFE3BC" stroke="none"/>\n'
    for y in range(322, 378, 6):
        s += f'      <circle cx="260.5" cy="{y}" r="0.9" fill="#9A9A9A" stroke="none"/><circle cx="289.5" cy="{y}" r="0.9" fill="#9A9A9A" stroke="none"/>\n'
    s += '    </g>\n'
    s += '    <path d="M252,394 L298,394 L300,386 L254,386 Z" fill="#FFFFFF"/><path d="M254,386 L300,386 L296,380 L256,380 Z" fill="#F2F2EC"/>\n'
    s += '    <path d="M258,378 L256,380 M292,378 L296,380" fill="none"/>\n'
    s += '    <path d="M262,389 L292,389" stroke="#BFE3BC" stroke-width="2.4"/>\n'
    return s + '  </g>\n'


def keyboard():
    s = f'  <g stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">\n'
    s += '    <path d="M296,305 L364,305 L369,316 L291,316 Z" fill="#D8CCB0"/>\n'
    for i, y in enumerate((308.5, 311, 313.5)):
        x0 = 297 - i * 1.3
        s += f'    <path d="M{f(x0)},{y} L{f(x0 + 68 + i * 2.6)},{y}" stroke="#7E7461" stroke-width="1.5" stroke-dasharray="3.2 1.6"/>\n'
    return s + '  </g>\n'


def desk_top():
    return (f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
            '    <path d="M172,304 L488,304 L498,318 L162,318 Z" fill="#8E5D36"/>\n'
            '    <path d="M190,309 L300,309 M380,313 L470,313" stroke="#9E6B41" stroke-width="1.4"/>\n'
            '  </g>\n')


def desk_front():
    s = f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <path d="M150,393 L510,393 L522,399 L138,399 Z" fill="#1F4245" stroke="none"/>\n'
    s += '    <rect x="164" y="324" width="332" height="69" fill="#6C4327"/>\n'
    s += '    <rect x="160" y="318" width="340" height="7" fill="#A36D42"/>\n'
    for x0 in (170, 398):
        s += f'    <rect x="{x0}" y="329" width="92" height="60" fill="#76492A" stroke-width="1.6"/>\n'
        for y in (349, 369):
            s += f'    <path d="M{x0},{y} L{x0 + 92},{y}" stroke-width="1.6"/>\n'
        for y in (339, 359, 379):
            s += f'    <rect x="{x0 + 38}" y="{y - 2}" width="16" height="4" rx="2" fill="#D2A64A" stroke-width="1.2"/>\n'
    s += '    <rect x="268" y="329" width="124" height="60" fill="#5A371F" stroke-width="1.6"/>\n'
    # the two nameplates, side by side on the one desk
    for y, name in ((336, 'JAMES · CTO'), (355, 'JOHN · CHIEF ENGINEER')):
        s += f'    <rect x="295" y="{y}" width="96" height="14" rx="1.5" fill="#D1A447" stroke-width="1.3"/>\n'
        s += f'    <text x="343" y="{y + 9.6}" text-anchor="middle" font-family="{TYPE}" font-size="6.6" font-weight="700" fill="#3A2A10" stroke="none">{escape(name)}</text>\n'
    return s + '  </g>\n'


def desk_items(stage, james_glass_on_desk):
    s = '  <g>\n'
    s += '    ' + glass(378, 313) + '\n' if stage not in ('done',) else ''
    # the ashtray and the two cigars
    s += (f'    <g stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">'
          '<path d="M392,313 L420,313 L417,306 L395,306 Z" fill="#C68A3A" fill-opacity="0.9"/>'
          '<path d="M395,306 Q406,303 417,306" fill="none" stroke-width="1.2"/>'
          '<path d="M398,311 L414,311" stroke="#E7B66A" stroke-width="1.4"/></g>\n')
    s += '    ' + cigar((402, 305), (384, 298), 's1') + '\n'
    s += '    ' + cigar((410, 305), (429, 297), 's2') + '\n'
    if james_glass_on_desk:
        s += '    ' + glass(442, 313) + '\n'
    # dinner
    if stage != 'flowchart':
        s += '    ' + pail(458, 312, 0.95, open_=stage not in ('idle', 'tim'), sticks=stage not in ('idle', 'tim')) + '\n'
    s += '    ' + pail(478, 313, 1.0) + '\n'
    s += '    ' + pail(466, 316, 0.9, open_=True) + '\n'
    return s + '  </g>\n'


# ======================================================================================== John, Chief Engineer (seated)
# Local (0, 0) is where the desk top's back edge crosses his middle; he sits at (330, 304).
JOHN_AT = (330, 304)


def john_chair():
    return (f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
            '    <path d="M286,304 L286,236 C286,206 374,206 374,236 L374,304 Z" fill="#6E2A22"/>\n'
            '    <path d="M292,300 L292,238 C292,214 368,214 368,238 L368,300" fill="none" stroke="#8A3A30" stroke-width="2"/>\n'
            + ''.join(f'    <circle cx="{x}" cy="{y}" r="1.5" fill="#4A1A14" stroke="none"/>\n' for y in (226, 244, 262) for x in (300, 316, 344, 360) if not (300 < x < 362 and y > 236))
            + '  </g>\n')


def john_head(look='front', expr='smile', cls=''):
    dx, dy = {'front': (0, 0), 'left': (-1.8, 0.3), 'right': (1.8, 0.3), 'down': (0, 1.4), 'up': (0.6, -1.3)}[look]
    s = f'    <g class="head{(" " + cls) if cls else ""}">\n'
    s += f'    <ellipse cx="-18.5" cy="-86" rx="3.4" ry="5.4" fill="{SKIN_JOHN}"/><ellipse cx="18.5" cy="-86" rx="3.4" ry="5.4" fill="{SKIN_JOHN}"/>\n'
    s += f'    <path d="M-18,-90 C-18,-106 -10,-112 0,-112 C10,-112 18,-106 18,-90 C18,-74 12,-62 0,-62 C-12,-62 -18,-74 -18,-90 Z" fill="{SKIN_JOHN}"/>\n'
    # close-cropped hair
    s += f'    <path d="M-18.5,-91 C-20,-108 -10,-115 0,-115 C10,-115 20,-108 18.5,-91 C16,-99 10,-103 0,-103 C-10,-103 -16,-99 -18.5,-91 Z" fill="{HAIR_JOHN}"/>\n'
    # the full beard and the moustache
    s += f'    <path d="M-18,-88 C-18.5,-70 -10,-59 0,-59 C10,-59 18.5,-70 18,-88 C16,-80 12,-76 8,-75.5 C4,-78 -4,-78 -8,-75.5 C-12,-76 -16,-80 -18,-88 Z" fill="{BEARD_JOHN}"/>\n'
    s += f'    <path d="M-8,-76 Q0,-81 8,-76 Q4,-74.5 0,-75.5 Q-4,-74.5 -8,-76 Z" fill="{BEARD_JOHN}" stroke-width="1.2"/>\n'
    if expr == 'talk':
        s += '    <path d="M-5,-72.5 Q0,-71 5,-72.5 Q3,-66.5 0,-66.5 Q-3,-66.5 -5,-72.5 Z" fill="#5A2320" stroke="#E2C9B8" stroke-width="1.2"/>\n'
    elif expr == 'frown':
        s += '    <path d="M-4.5,-69.5 Q0,-72.5 4.5,-69.5" fill="none" stroke="#E2C9B8" stroke-width="1.5"/>\n'
    else:
        s += '    <path d="M-5,-71.5 Q0,-68.5 5,-71.5" fill="none" stroke="#E2C9B8" stroke-width="1.5"/>\n'
    s += f'    <path d="M-1.5,-88 Q-4.5,-80 -1,-79 Q2,-78.5 3.5,-80.5" fill="{SKIN_JOHN_DK}" stroke-width="1.5"/>\n'
    # horn-rimmed glasses, the lenses read as the whites of his eyes
    s += '    <path d="M-2.5,-92 Q0,-94 2.5,-92" fill="none" stroke="#2B1A10" stroke-width="2.2"/>\n'
    s += '    <path d="M-14.5,-93 L-18.5,-90 M14.5,-93 L18.5,-90" fill="none" stroke="#2B1A10" stroke-width="2"/>\n'
    for x in (-8.5, 8.5):
        s += f'    <rect x="{x - 6}" y="-98" width="12" height="11" rx="3.5" fill="#FFFFFF" stroke="#2B1A10" stroke-width="2.6"/>\n'
        s += f'    <circle cx="{f(x + dx)}" cy="{f(-92.3 + dy)}" r="1.9" fill="{INK}" stroke="none"/>\n'
    s += f'    <g class="blink" opacity="0"><rect x="-13.2" y="-96.7" width="9.4" height="8.4" rx="2.4" fill="{SKIN_JOHN}" stroke="none"/><rect x="3.8" y="-96.7" width="9.4" height="8.4" rx="2.4" fill="{SKIN_JOHN}" stroke="none"/>'
    s += '<path d="M-13,-91.5 L-4,-91.5 M4,-91.5 L13,-91.5" stroke-width="1.4"/></g>\n'
    brow = {'frown': ('M-14,-101 L-4,-99', 'M4,-99 L14,-101'), 'talk': ('M-14,-102.5 L-4,-103.5', 'M4,-103.5 L14,-102.5')}.get(
        expr, ('M-14,-101.5 L-4,-102.5', 'M4,-102.5 L14,-101.5'))
    s += f'    <path d="{brow[0]} {brow[1]}" fill="none" stroke-width="2.6"/>\n'
    # the pencil behind his ear
    s += f'    <g>{"".join(tube([(10, -103), (30, -90)], 3.2, "#E8C34A", ow=1.3))}<path d="M28.5,-91 L33,-88 L30.5,-92.5 Z" fill="#3A2A18" stroke-width="0.8"/><path d="M10,-103 L13,-101" stroke="#E98A8A" stroke-width="3.2"/></g>\n'
    return s + '    </g>\n'


def john_torso():
    s = f'    <path d="M-7,-64 L-7,-52 L7,-52 L7,-64 Z" fill="{SKIN_JOHN}"/>\n'
    s += f'    <path d="M-10,-57 C-24,-56 -33,-52 -36,-45 C-38,-30 -37,-12 -35,6 L35,6 C37,-12 38,-30 36,-45 C33,-52 24,-56 10,-57 Z" fill="{SHIRT_JOHN}"/>\n'
    s += f'    <path d="M-6,-57 L0,-47 L6,-57 Z" fill="{SKIN_JOHN}" stroke-width="1.4"/>\n'
    # the loosened knit tie
    s += f'    <path d="M-3.4,-49 L3.4,-49 L2.6,-42.5 L-2.6,-42.5 Z" fill="{TIE_JOHN}"/>\n'
    s += f'    <path d="M-2.6,-42.5 L2.6,-42.5 L5.5,4 L-5.5,4 Z" fill="{TIE_JOHN}"/>\n'
    s += '    <path d="M-3,-36 L3,-36 M-3.6,-28 L3.6,-28 M-4.2,-20 L4.2,-20 M-4.8,-12 L4.8,-12" stroke="#A97A22" stroke-width="1.2"/>\n'
    s += f'    <path d="M-10,-57 L-1,-48 L-11,-45 L-14,-53 Z M10,-57 L1,-48 L11,-45 L14,-53 Z" fill="{SHIRT_JOHN}" stroke-width="1.6"/>\n'
    # the pocket and its pocket protector: three pens
    s += f'    <path d="M12,-34 L27,-34 L27,-20 L12,-20 Z" fill="{SHIRT_JOHN_DK}" stroke-width="1.4"/>\n'
    for x, c in ((15, '#B23A2E'), (19, '#1F4E8C'), (23, INK)):
        s += f'    <rect x="{x - 1.3}" y="-40" width="2.6" height="9" rx="1" fill="{c}" stroke-width="0.9"/>\n'
    s += '    <path d="M12.5,-33 L26.5,-33 L26.5,-27 L12.5,-27 Z" fill="#F4F1EA" stroke-width="1.2"/>\n'
    s += f'    <path d="M-30,-20 Q-26,-17 -22,-20 M20,-4 Q24,-1 28,-4" fill="none" stroke="{SHIRT_JOHN_DK}" stroke-width="1.4"/>\n'
    return s


def john_body(look, expr, cls=''):
    x, y = JOHN_AT
    s = f'  <g class="john" transform="translate({x} {y})" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    s += john_torso() + john_head(look, expr, cls)
    return s + '  </g>\n'


SJL, SJR = (-32, -45), (32, -45)


def john_arms(stage):
    """What his hands are doing, drawn over the desk top."""
    x, y = JOHN_AT
    s = f'  <g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    key_l, key_r = (-16, 6), (16, 7)
    on_desk_l = arm(SJL, (-42, -6), key_l, SHIRT_JOHN, SKIN_JOHN)
    on_desk_r = arm(SJR, (42, -6), key_r, SHIRT_JOHN, SKIN_JOHN)
    if stage in ('idle', 'spec'):
        s += arm(SJL, (-42, -6), key_l, SHIRT_JOHN, SKIN_JOHN, cls='tap tap-l')
        s += arm(SJR, (42, -6), key_r, SHIRT_JOHN, SKIN_JOHN, cls='tap tap-r')
    elif stage == 'tim':
        s += on_desk_l + on_desk_r
    elif stage == 'reading':
        s += on_desk_l
        s += arm(SJR, (38, -6), (9, -60), SHIRT_JOHN, SKIN_JOHN)
    elif stage == 'flowchart':
        s += arm(SJL, (-40, -8), (-15, -22), SHIRT_JOHN, SKIN_JOHN, hand=False,
                 hold=pail(-15, -10, 0.9, open_=True) + f'<circle cx="-15" cy="-20" r="6.2" fill="{SKIN_JOHN}" stroke="{INK}" stroke-width="2.4"/>')
        s += arm(SJR, (42, -8), (17, -54), SHIRT_JOHN, SKIN_JOHN,
                 hold='<path d="M14,-52 L2,-70 M18,-52 L8,-72" fill="none" stroke="#C49A62" stroke-width="2"/>')
    elif stage == 'consulting':
        s += on_desk_l
        hold = ''.join(tube([(56, -96), (64, -122)], 3.2, '#E8C34A', ow=1.3)) + '<path d="M62.6,-121 L66,-128 L66.2,-120 Z" fill="#3A2A18" stroke-width="0.8"/>'
        s += arm(SJR, (56, -58), (57, -96), SHIRT_JOHN, SKIN_JOHN, cls='nod', hold=hold)
    elif stage == 'done':
        s += on_desk_l
        s += arm(SJR, (54, -56), (51, -94), SHIRT_JOHN, SKIN_JOHN, cls='toast', hold=glass(51, -94, 1.05))
    elif stage == 'failed':
        s += on_desk_r
        s += arm(SJL, (-52, -44), (-13, -96), SHIRT_JOHN, SKIN_JOHN)
    return s + '  </g>\n'


# ======================================================================================== James, CTO (standing)
# Local (0, 0) is between his feet.
def james_head(look='front', expr='smile'):
    dx, dy = {'front': (0, 0), 'left': (-1.7, 0.2), 'right': (1.7, 0.2), 'down': (-0.6, 1.5), 'up': (0.6, -1.3)}[look]
    s = '    <g class="head">\n'
    s += f'    <path d="M-7,-200 L-7.5,-184 L7.5,-184 L7,-200 Z" fill="{SKIN_JAMES}"/>\n'
    s += f'    <path d="M-7,-196 L7,-196 L7,-191 Q0,-188 -7,-191 Z" fill="{SKIN_JAMES_DK}" stroke="none"/>\n'
    s += f'    <ellipse cx="-16.5" cy="-219" rx="3.4" ry="5.6" fill="{SKIN_JAMES}"/><ellipse cx="16.5" cy="-219" rx="3.4" ry="5.6" fill="{SKIN_JAMES}"/>\n'
    # the square jaw
    s += f'    <path d="M-15.5,-236 L-15.8,-212 C-15.8,-203 -11,-196 -4,-195 L4,-195 C11,-196 15.8,-203 15.8,-212 L15.5,-236 Z" fill="{SKIN_JAMES}"/>\n'
    # slicked back, silver at the temples
    s += f'    <path d="M-16.5,-222 C-19.5,-238 -12,-250 2,-250 C15,-250 20.5,-240 16.5,-222 C15.5,-230 12,-235 7,-236 C2,-240 -6,-240 -10,-236 C-13,-233 -15,-228 -16.5,-222 Z" fill="{HAIR_JAMES}"/>\n'
    s += '    <path d="M-10,-238 C-5,-247 7,-248 13,-240" fill="none" stroke="#4A3B30" stroke-width="1.6"/>\n'
    s += '    <path d="M-16.5,-223 C-17,-227 -16.5,-230 -15.5,-232 L-14,-226 Z M16.5,-223 C17,-227 16.5,-230 15.5,-232 L14,-226 Z" fill="#B3ADA5" stroke-width="1.2"/>\n'
    # eyes: two white ovals that touch, dot pupils
    for ex in (-4.6, 4.6):
        s += f'    <ellipse cx="{ex}" cy="-221" rx="4.4" ry="5.6" fill="#FFFFFF" stroke-width="1.8"/>\n'
        s += f'    <circle cx="{f(ex + dx)}" cy="{f(-219 + dy)}" r="1.7" fill="{INK}" stroke="none"/>\n'
        # the heavy upper lid: the calm of a man who has signed off on worse
        s += f'    <path d="M{f(ex - 4.4)},-222.6 C{f(ex - 4.4)},-229.4 {f(ex + 4.4)},-229.4 {f(ex + 4.4)},-222.6 Q{f(ex)},-221.4 {f(ex - 4.4)},-222.6 Z" fill="{SKIN_JAMES}" stroke-width="1.8"/>\n'
    s += f'    <g class="blink" opacity="0"><ellipse cx="-4.6" cy="-221" rx="4.4" ry="5.6" fill="{SKIN_JAMES}" stroke-width="1.8"/><ellipse cx="4.6" cy="-221" rx="4.4" ry="5.6" fill="{SKIN_JAMES}" stroke-width="1.8"/></g>\n'
    brow = {'stern': 'M-10,-230 L-2,-228 M2,-228 L10,-230', 'talk': 'M-10,-231 L-2,-232 M2,-232 L10,-231'}.get(expr, 'M-10,-230.5 L-2,-231.5 M2,-231.5 L10,-229.5')
    s += f'    <path d="{brow}" fill="none" stroke-width="2.8"/>\n'
    s += f'    <path d="M{f(0.5 + dx * 0.6)},-215 Q{f(5 + dx * 0.6)},-207 {f(1 + dx * 0.6)},-206 Q{f(-1.5 + dx * 0.6)},-205.6 {f(-3 + dx * 0.6)},-207" fill="none" stroke-width="1.6"/>\n'
    mx = dx * 0.5
    if expr == 'talk':
        s += f'    <path d="M{f(-6 + mx)},-202.5 Q{f(mx)},-200.5 {f(6 + mx)},-203 Q{f(3 + mx)},-196 {f(mx)},-196.5 Q{f(-4 + mx)},-197.5 {f(-6 + mx)},-202.5 Z" fill="#5A2320" stroke-width="1.6"/>\n'
        s += f'    <path d="M{f(-3.5 + mx)},-201.8 L{f(3.5 + mx)},-202" stroke="#FFFFFF" stroke-width="1.4"/>\n'
    elif expr == 'stern':
        s += f'    <path d="M{f(-5 + mx)},-201 L{f(5 + mx)},-201.5" fill="none" stroke-width="1.8"/>\n'
    else:
        s += f'    <path d="M{f(-6 + mx)},-201.5 Q{f(mx)},-199 {f(6.5 + mx)},-203.5" fill="none" stroke-width="1.8"/><path d="M{f(6.5 + mx)},-203.5 L{f(7.5 + mx)},-205" stroke-width="1.4"/>\n'
    s += '    <path d="M-2.5,-196.6 Q0,-195.6 2.5,-196.6" fill="none" stroke="#9A6A4C" stroke-width="1.2"/>\n'
    return s + '    </g>\n'


def james_torso():
    s = f'    <path d="M-9,-190 C-19,-189 -29,-186 -32,-180 C-34,-160 -31,-135 -25,-112 L25,-112 C31,-135 34,-160 32,-180 C29,-186 19,-189 9,-190 Z" fill="{SHIRT_JAMES}"/>\n'
    s += f'    <path d="M-20,-140 Q-14,-136 -10,-140 M12,-160 Q16,-157 20,-160 M-18,-118 Q-14,-114 -10,-118 M12,-118 Q16,-114 20,-118" fill="none" stroke="{SHIRT_JAMES_DK}" stroke-width="1.5"/>\n'
    s += f'    <path d="M-5.5,-190 L0,-180 L5.5,-190 Z" fill="{SKIN_JAMES}" stroke-width="1.4"/>\n'
    # the braces, over the shoulders
    for side in (-1, 1):
        a, b = (side * 14, -112), (side * 19, -186)
        s += ''.join(tube([a, b], 4.4, BRACES, ow=1.5))
        s += f'<rect x="{side * 14 - 3}" y="-121" width="6" height="5" fill="#C9A24A" stroke-width="1"/>\n'
    # the tie, knot pulled down a notch
    s += f'    <path d="M-3.8,-183 L3.8,-183 L2.8,-176 L-2.8,-176 Z" fill="{TIE_JAMES}"/>\n'
    s += f'    <path d="M-2.8,-176 L2.8,-176 L6.5,-128 L0,-121 L-6.5,-128 Z" fill="{TIE_JAMES}"/>\n'
    s += '    <path d="M-3.4,-166 L3.6,-171 M-4.4,-154 L4.4,-160 M-5.2,-142 L5.2,-148 M-5.6,-131 L5.8,-137" stroke="#D9A84A" stroke-width="1.3"/>\n'
    s += f'    <path d="M-9,-190 L-1,-181 L-11,-178 L-14,-186 Z M9,-190 L1,-181 L11,-178 L14,-186 Z" fill="{SHIRT_JAMES}" stroke-width="1.6"/>\n'
    return s


def james_legs():
    s = f'    <path d="M-25,-112 L25,-112 L23,-62 L19,-8 L3,-8 L1,-92 L-1,-92 L-3,-8 L-19,-8 L-23,-62 Z" fill="{TROUSERS_JAMES}"/>\n'
    s += '    <path d="M-11,-104 L-11,-12 M11,-104 L11,-12" stroke="#50555F" stroke-width="1.4"/>\n'
    s += '    <rect x="-25" y="-115" width="50" height="7" fill="#3E2618" stroke-width="2"/><rect x="-3.5" y="-115" width="7" height="7" fill="#C9A24A" stroke-width="1.4"/>\n'
    s += '    <path d="M-20,-9 L-3,-9 L-2,0 L-25,0 C-27,-3 -25,-8 -20,-9 Z M3,-9 L20,-9 C25,-8 27,-3 25,0 L2,0 Z" fill="#1E1B1B"/>\n'
    s += '    <path d="M-20,-6 L-12,-6 M13,-6 L21,-6" stroke="#57504C" stroke-width="1.4"/>\n'
    return s


SL, SR = (-28, -181), (28, -181)


def pocket_hand(side):
    """The hand that goes in his trouser pocket: a forearm into the pocket, the pocket's edge drawn over it."""
    x = side
    s = arm(SL if side < 0 else SR, (x * 36, -142), (x * 21, -108), SHIRT_JAMES, SKIN_JAMES, hand=False)
    s += f'<path d="M{x * 28},-110 L{x * 13},-110 L{x * 12},-96 L{x * 25},-100 Z" fill="{TROUSERS_JAMES}" stroke="none"/>'
    s += f'<path d="M{x * 24},-109 L{x * 14},-98" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    return s


def watch(H, E):
    """His wristwatch, on the left wrist, just short of the hand."""
    p = lerp(H, E, 0.22)
    return f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="3.4" fill="#D9A441" stroke="{INK}" stroke-width="1.4"/>'


def james(stage, x=548, y=390, s=1.0, look=None, expr=None):
    pose = {
        'idle': ('left', 'smile'), 'tim': ('left', 'smile'), 'reading': ('down', 'stern'), 'flowchart': ('right', 'smile'),
        'consulting': ('left', 'stern'), 'spec': ('down', 'smile'), 'done': ('left', 'talk'), 'failed': ('left', 'stern'),
        'door': ('front', 'smile'),
    }[stage]
    look = look or pose[0]
    expr = expr or pose[1]
    out = f'  <ellipse cx="{x}" cy="{f(y + 1)}" rx="{f(34 * s)}" ry="{f(6 * s)}" fill="#1F4245"/>\n'
    out += f'  <g class="james" transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    out += james_legs() + james_torso()
    left, right = '', ''
    if stage == 'door':
        # in the doorway his inside hand is in his pocket, so nobody's arm crosses anybody
        left = arm(SL, (-40, -144), (-25, -150), SHIRT_JAMES, SKIN_JAMES, hold=glass(-22, -142, 1.15))
        right = pocket_hand(1)
    elif stage in ('idle', 'tim'):
        left = pocket_hand(-1)
        H = (25, -150)
        right = arm(SR, (40, -144), H, SHIRT_JAMES, SKIN_JAMES, hold=glass(22, -142, 1.15)) + watch(H, (40, -144))
    elif stage == 'reading':
        HL, HR = (-14, -150), (14, -150)
        folder = (f'<g stroke="{INK}" stroke-width="2"><path d="M-26,-172 L0,-168 L0,-138 L-24,-142 Z" fill="{MANILA}"/>'
                  f'<path d="M0,-168 L26,-172 L24,-142 L0,-138 Z" fill="#FBF8F0"/>'
                  '<path d="M5,-162 L20,-164 M5,-156 L20,-158 M5,-150 L16,-151.5" stroke="#8A8A8A" stroke-width="1.2"/>'
                  '<path d="M-20,-161 L-6,-159" stroke="#B23A2E" stroke-width="1.4"/></g>')
        left = arm(SL, (-38, -140), HL, SHIRT_JAMES, SKIN_JAMES, hand=False)
        right = arm(SR, (38, -140), HR, SHIRT_JAMES, SKIN_JAMES, hand=False) + folder
        right += f'<circle cx="{HL[0]}" cy="{HL[1]}" r="6.2" fill="{SKIN_JAMES}" stroke="{INK}"/><circle cx="{HR[0]}" cy="{HR[1]}" r="6.2" fill="{SKIN_JAMES}" stroke="{INK}"/>' + watch(HR, (38, -140))
    elif stage == 'flowchart':
        left = pocket_hand(-1)
        H = (88, -214)
        marker = f'<g transform="rotate(-50 {H[0]} {H[1]})"><rect x="{H[0] - 2.5}" y="{H[1] - 15}" width="5" height="14" rx="1.5" fill="#1F4E8C" stroke="{INK}" stroke-width="1.4"/></g>'
        right = arm(SR, (58, -190), H, SHIRT_JAMES, SKIN_JAMES, cls='scribble', hold=marker) + watch(H, (58, -190))
    elif stage == 'consulting':
        HL = (-6, -197)
        left = arm(SL, (-36, -146), HL, SHIRT_JAMES, SKIN_JAMES)
        right = arm(SR, (46, -148), (25, -118), SHIRT_JAMES, SKIN_JAMES)
    elif stage == 'spec':
        left = pocket_hand(-1)
        H = (20, -152)
        sheet = (f'<g transform="rotate(-8 18 -150)" stroke="{INK}" stroke-width="1.4"><path d="M2,-178 L34,-178 L34,-128 L2,-128 Z" fill="#FFFFFF"/>'
                 '<path d="M6,-172 L30,-172 M6,-164 L30,-164 M6,-156 L30,-156 M6,-148 L30,-148 M6,-140 L30,-140" stroke="#BFE3BC" stroke-width="3.5"/>'
                 '<path d="M8,-170 L26,-170 M8,-162 L22,-162 M8,-154 L28,-154" stroke="#5A5A5A" stroke-width="1"/></g>')
        right = arm(SR, (40, -140), H, SHIRT_JAMES, SKIN_JAMES, hold=sheet) + watch(H, (40, -140))
    elif stage == 'done':
        left = arm(SL, (-48, -160), (-64, -178), SHIRT_JAMES, SKIN_JAMES)
        H = (46, -236)
        right = arm(SR, (50, -196), H, SHIRT_JAMES, SKIN_JAMES, cls='toast', hold=glass(46, -236, 1.0)) + watch(H, (50, -196))
    elif stage == 'failed':
        left = arm(SL, (-46, -146), (-26, -116), SHIRT_JAMES, SKIN_JAMES)
        right = arm(SR, (46, -146), (26, -116), SHIRT_JAMES, SKIN_JAMES) + watch((26, -116), (46, -146))
    out += left + james_head(look, expr) + right
    return out + '  </g>\n'


# ======================================================================================== Tim, the EA, with the memo
def tim():
    s = '  <g class="tim">\n'
    s += '  <ellipse cx="96" cy="391" rx="28" ry="5.5" fill="#1F4245"/>\n'
    s += f'  <g class="walk"><g transform="translate(96 390) scale(0.9)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    s += '    <path d="M-22,-104 L22,-104 L20,-56 L17,-8 L3,-8 L1,-88 L-1,-88 L-3,-8 L-17,-8 L-20,-56 Z" fill="#C8B387"/>\n'
    s += '    <path d="M-19,-9 L-3,-9 L-2,0 L-23,0 C-25,-3 -23,-8 -19,-9 Z M3,-9 L19,-9 C23,-8 25,-3 23,0 L2,0 Z" fill="#6B4A32"/>\n'
    s += '    <path d="M-8,-182 C-18,-181 -26,-178 -29,-172 C-31,-152 -28,-126 -23,-104 L23,-104 C28,-126 31,-152 29,-172 C26,-178 18,-181 8,-182 Z" fill="#FBF8F0"/>\n'
    # the sweater vest
    s += '    <path d="M-22,-170 C-25,-150 -24,-126 -21,-104 L21,-104 C24,-126 25,-150 22,-170 L10,-178 L0,-150 L-10,-178 Z" fill="#7D8B3F"/>\n'
    s += '    <path d="M-18,-112 L18,-112" stroke="#66732F" stroke-width="2"/>\n'
    s += '    <path d="M-2.8,-176 L2.8,-176 L4.5,-152 L0,-148 L-4.5,-152 Z" fill="#2F6F73"/>\n'
    s += '    <path d="M-8,-182 L-1,-174 L-9,-171 L-12,-178 Z M8,-182 L1,-174 L9,-171 L12,-178 Z" fill="#FBF8F0" stroke-width="1.6"/>\n'
    s += f'    <path d="M-5.5,-194 L-6,-180 L6,-180 L5.5,-194 Z" fill="{SKIN_TIM}"/>\n'
    s += f'    <ellipse cx="-15" cy="-208" rx="3.2" ry="5" fill="{SKIN_TIM}"/><ellipse cx="15" cy="-208" rx="3.2" ry="5" fill="{SKIN_TIM}"/>\n'
    s += f'    <path d="M-14.5,-218 C-15,-200 -10,-188 0,-188 C10,-188 15,-200 14.5,-218 Z" fill="{SKIN_TIM}"/>\n'
    s += f'    <path d="M-16,-210 C-19,-226 -10,-234 1,-234 C12,-234 19,-226 16,-210 C14,-218 9,-222 3,-221 C-3,-224 -11,-220 -16,-210 Z" fill="{HAIR_TIM}"/>\n'
    s += f'    <path d="M2,-233 C4,-240 9,-241 10,-238 C7,-238 5,-236 4,-232 Z" fill="{HAIR_TIM}" stroke-width="1.6"/>\n'
    for ex in (-4.2, 4.2):
        s += f'    <ellipse cx="{ex}" cy="-209" rx="4" ry="5" fill="#FFFFFF" stroke-width="1.7"/><circle cx="{f(ex + 1.5)}" cy="-208.5" r="1.6" fill="{INK}" stroke="none"/>\n'
    s += '    <path d="M-9,-217 L-2,-217.5 M2,-217.5 L9,-216.5" fill="none" stroke-width="2.2"/>\n'
    s += '    <path d="M1,-204 Q4.5,-199 1,-198" fill="none" stroke-width="1.5"/>\n'
    s += '    <path d="M-6,-195 Q0,-192 7,-195.5 Q3,-188.5 0,-189 Q-4,-189.5 -6,-195 Z" fill="#5A2320" stroke-width="1.6"/><path d="M-3.5,-194 L4.5,-194.4" stroke="#FFFFFF" stroke-width="1.4"/>\n'
    s += '    <path d="M-9,-201 L-8,-200 M-11,-202 L-10,-201 M9,-201 L10,-200" stroke="#C98A6A" stroke-width="1.2"/>\n'
    # the memo from the owner in a manila folder, held to his chest
    folder = (f'<g stroke="{INK}" stroke-width="2"><path d="M-28,-166 L4,-160 L2,-118 L-30,-124 Z" fill="{MANILA}"/>'
              f'<path d="M-24,-166 L-12,-164 L-12,-160 L-24,-162 Z" fill="{MANILA_DK}" stroke-width="1.2"/>'
              f'<path d="M-22,-148 L-4,-145" stroke="#B23A2E" stroke-width="1.6"/>'
              f'<path d="M-6,-163 L0,-162 L-1,-170 L-7,-171 Z" fill="#FBF8F0" stroke-width="1.2"/></g>')
    s += arm((-24, -172), (-34, -132), (-8, -138), '#FBF8F0', SKIN_TIM, hand=False) + folder
    s += f'<circle cx="-8" cy="-138" r="6" fill="{SKIN_TIM}" stroke="{INK}" stroke-width="2.4"/>\n'
    s += arm((24, -172), (42, -186), (48, -218), '#FBF8F0', SKIN_TIM, cls='wave')
    s += '  </g></g>\n  </g>\n'
    return s


# ======================================================================================== speech
def bubble(x, y, w, lines, tail, cls='bubble'):
    """A cartoon balloon, lettered in caps; its tail points at (tail)."""
    h = 12 + 14 * len(lines)
    tx = min(max(tail[0], x + 18), x + w - 18)
    t = ''.join(f'<text x="{f(x + w / 2)}" y="{f(y + 18 + 14 * i)}" text-anchor="middle" font-family="{TYPE}" font-size="11" font-weight="700" fill="{INK}" stroke="none">{escape(l)}</text>' for i, l in enumerate(lines))
    return (f'  <g class="{cls}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round">\n'
            f'    <path d="M{x + 10},{y} L{x + w - 10},{y} Q{x + w},{y} {x + w},{y + 10} L{x + w},{y + h - 10} Q{x + w},{y + h} {x + w - 10},{y + h} '
            f'L{f(tx + 9)},{y + h} L{f(tail[0])},{f(tail[1])} L{f(tx - 3)},{y + h} L{x + 10},{y + h} Q{x},{y + h} {x},{y + h - 10} L{x},{y + 10} Q{x},{y} {x + 10},{y} Z" fill="#FFFDF6"/>\n'
            f'    {t}\n  </g>\n')


# ======================================================================================== a scene
LABELS = {
    'idle': ('Ten to eleven at night in the CTO\'s office. John, the Chief Engineer, types at the terminal behind the '
             'partners\' desk; James, the CTO, stands by the window with a whisky. Two cigars smoulder in the ashtray, '
             'Chinese takeout waits on the desk, and the org chart on the wall has the two of them at the top.'),
    'tim': 'Tim walks in with a memo in a manila folder: "Memo from Patrick. It\'s for you two." James and John look up.',
    'reading': 'Reading the state: John reads the green screen, chin in hand; James reads the memo in the folder.',
    'flowchart': 'James draws the run on the run board, three lanes into the gate; John watches from the desk, eating.',
    'consulting': 'John makes his one call, pencil raised: "Smallest correct change. Then it ships." James listens, hand at his chin.',
    'spec': 'John types out the prompts; the spec feeds off the dot-matrix printer and James reads the first sheet.',
    'done': 'Done: the run is pinned to the board and stamped. James raises his glass: "Paste blocks are up. We move." John raises his.',
    'failed': 'The run did not publish: the screen says ERROR, John holds his forehead: "That one didn\'t land. We go again."',
}

HEAD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <title>{title}</title>
'''


def scene(stage):
    out = HEAD.format(vb='0 0 640 400', w=640, h=400, label=escape(LABELS[stage], quote=True), title="James and John's Coworking Space")
    out += f'  <!-- Scene "{stage}". Drawn by art/build.py; edit that, not this file. -->\n'
    out += wall() + window() + board(stage) + org_chart() + clock() + credenza()
    if stage == 'flowchart':
        out += james('flowchart', x=98, y=286, s=0.82)
    john_look, john_expr = {
        'idle': ('left', 'smile'), 'tim': ('left', 'smile'), 'reading': ('left', 'smile'), 'flowchart': ('left', 'smile'),
        'consulting': ('right', 'talk'), 'spec': ('left', 'smile'), 'done': ('right', 'talk'), 'failed': ('down', 'frown'),
    }[stage]
    out += john_chair() + john_body(john_look, john_expr)
    out += desk_top() + terminal(stage) + printer(stage) + keyboard()
    out += desk_items(stage, james_glass_on_desk=stage not in ('idle', 'tim', 'done'))
    out += john_arms(stage)
    out += desk_front()
    if stage == 'spec':
        out += printout()
    if stage == 'tim':
        out += tim()
    if stage != 'flowchart':
        out += james(stage)
    if stage == 'tim':
        out += bubble(24, 118, 176, ['MEMO FROM PATRICK.', "IT'S FOR YOU TWO."], (88, 180))
    elif stage == 'consulting':
        out += bubble(214, 150, 186, ['SMALLEST CORRECT CHANGE.', 'THEN IT SHIPS.'], (318, 196))
    elif stage == 'failed':
        out += bubble(214, 150, 176, ["THAT ONE DIDN'T LAND.", 'WE GO AGAIN.'], (318, 196))
    elif stage == 'done':
        out += bubble(420, 96, 172, ['PASTE BLOCKS ARE UP.', 'WE MOVE.'], (540, 146))
    return out + '</svg>\n'


# ======================================================================================== the door figure and the avatars
def john_standing(x, y, look='front', expr='smile'):
    """John on his feet (for the door): his seated drawing, plus a belt and his trousers. (x, y) is his middle."""
    s = f'  <g class="john" transform="translate({x} {y})" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    s += '    <path d="M-35,6 L35,6 L34,70 L2,70 L0,30 L-2,70 L-34,70 Z" fill="#5A4636"/>\n'
    s += john_torso()
    s += '    <rect x="-35" y="2" width="70" height="7" fill="#2E1E14" stroke-width="2"/><rect x="-3.5" y="2" width="7" height="7" fill="#C9A24A" stroke-width="1.4"/>\n'
    s += john_head(look, expr)
    roll = (f'<g stroke="{INK}" stroke-width="1.6"><path d="M2,-24 L30,-14 L26,-4 L-2,-14 Z" fill="#FFFFFF"/>'
            '<path d="M4,-20 L26,-12 M2,-16 L24,-8" stroke="#BFE3BC" stroke-width="2.6"/></g>')
    s += arm(SJL, (-37, -8), (-34, 22), SHIRT_JOHN, SKIN_JOHN)
    s += arm(SJR, (44, -10), (16, -14), SHIRT_JOHN, SKIN_JOHN, hold=roll)
    return s + '  </g>\n'


def door():
    """The two of them in the doorway, colleagues side by side: the CTO with his whisky, the Chief Engineer with the spec."""
    out = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-94 -258 196 170" width="196" height="170" role="img" aria-label="James, the CTO, and John, the Chief Engineer, side by side in shirtsleeves and ties">
  <title>James and John</title>
  <!-- Drawn by art/build.py; edit that, not this file. -->
'''
    body = james('door', x=-38, y=0, s=1.0)
    body = body.split('\n', 1)[1]  # no floor shadow in the doorway
    out += john_standing(46, -134)
    out += body
    return out + '</svg>\n'


def avatar_svg(label, body, clip):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="{label}">
  <title>{label}</title>
  <!-- Drawn by art/build.py from the scenes' own parts. Two colleagues side by side, each in their own half. -->
  <defs><clipPath id="{clip}"><rect width="64" height="64" rx="14"/></clipPath></defs>
  <rect width="64" height="64" rx="14" fill="#D9A441"/>
  <g clip-path="url(#{clip})">
{body}  </g>
  <rect x="1" y="1" width="62" height="62" rx="13" fill="none" stroke="{INK}" stroke-width="2"/>
</svg>
'''


def james_bust(t):
    return (f'  <g transform="{t}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
            + james_torso() + james_head('front', 'smile') + '  </g>\n')


def john_bust(t):
    return (f'  <g transform="{t}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
            + john_torso() + john_head('front', 'smile') + '  </g>\n')


def write(rel, text):
    path = os.path.join(HOME, *rel.split('/'))
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


if __name__ == '__main__':
    for st in LABELS:
        write(f'art/{st}.svg', scene(st))
    write('art.svg', scene('idle'))
    write('art/door.svg', door())
    pair = (james_bust('translate(17 162) scale(0.62)')
            + john_bust('translate(48 77) scale(0.6)')
            + f'  <path d="M32,0 L32,64" stroke="{INK}" stroke-width="1.6"/>\n')
    write('mark.svg', avatar_svg("James and John's Coworking Space", pair, 'cw-mark'))
    write('art/james.svg', avatar_svg('James, CTO', james_bust('translate(32 202) scale(0.78)'), 'cw-james'))
    write('art/john.svg', avatar_svg('John, Chief Engineer', john_bust('translate(32 96) scale(0.74)'), 'cw-john'))
    print('drew', len(LABELS), 'scenes, the door figure, the mark and two avatars')
