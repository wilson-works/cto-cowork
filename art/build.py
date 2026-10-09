"""art/build.py: draws every picture of James and John's Coworking Space from one set of parts, so the room, the people
and the ink are the same hand in every scene. Run it from the space's folder (python art/build.py); it writes:

  art.svg                the dashboard's still (the idle scene)
  art/<scene>.svg        one scene per stage of a run, which the dashboard swaps in as the run moves:
                         idle (John types, James paces with a whisky), tim (Tim walks in with the memo), reading (James
                         types, John paces reading the memo), flowchart (James at the run board), consulting (both on
                         their feet, John makes his one call), spec (John types, the spec feeds off the printer, James
                         paces reading it), done (they clink glasses), failed
  art/door.svg           the two of them for the office door: the CTO and the Chief Engineer, side by side
  art/office-door.svg    the CTO's office door with nobody in it: the space's logo (the WilsonWorks site's card)
  mark.svg               the pair, two colleagues each in their own half (the office floor shows it as their avatar)
  art/james.svg, art/john.svg   one avatar each

Owner 2026-10-07 ~22:40 CDT, a ground-up redesign that scraps the lounge look: "recreate them like a 1980s Software
Startup setting, working in an executive office, both in dress shirt, tie, rolled up sleeves, a couple glasses with brown
liquid in them, a couple cigars on the table, and still some boxes of chinese takeout food. Think Mad Men meets Scooby Doo
cartoon art style. And redesign James and John to resemble like a CTO and Chief Engineer, not like 2 partners living
together in an apartment. Really need to land the coworking and leadership elements more."
Then, 2026-10-07 ~23:45 CDT: "Can the clock in the back keep real time, and can the city in the window follow a day/night
cycle. Get James hand out of his pants and not looking at John that way.. Its creepy. Also they need better looking hands
with 3 finger and 1 thumb like normal cartoons. And the computer monitor should be facing John and James, and James should
have different movements like pacing back and forth, or John pacing and James typing, or both standing and talking, etc.
The desk is also facing the wrong way. The drawers would be facing John and we would be see the front side of the desk."

Style: Saturday-morning cel on a painted background. The room is flat painted shapes with a thin brown line and no black
ink. The people and everything they touch are cels: heavy warm-black ink, flat colour, eyes as white ovals with dot
pupils, cartoon hands of three fingers and a thumb. Arms, fingers and legs are outlined tubes (one ink stroke under one
colour stroke), so every pose is drawn by the same hand. The desk shows us its front panel; the drawers, the monitor and
the printer face whoever is in the chair. Colour by fill and stroke attributes only.

What moves is named by class, and the dashboard's CSS and script move it; with neither, every scene is a complete still
at ten to eleven at night:
  CSS     tim (tim-side walks in, tim-front turns to us), wave, bubble, draw, scribble, tap, smoke, ember, feed,
          printhead, blink, twinkle, nod, toast,
          pace (a man walking his beat side-on: frames f0..f7, his upper body on bob; turned round at each end)
  script  the clock's hour, minute and second hands (Central time), and the window: sky (data-band 0..3), sun, moon,
          stars, bldg-back, bldg-front and lit (data-c is its colour at night)
Two colleagues at work, never a likeness of anyone real.
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
TROUSERS_JAMES, TROUSERS_JOHN = '#3A3E48', '#5A4636'
HAIR_JAMES, HAIR_JOHN, BEARD_JOHN, HAIR_TIM = '#2A211C', '#1C1612', '#231C18', '#6B3E26'
WHISKY, WHISKY_DK, GLASS = '#A9651F', '#7E4716', '#E4EEEC'
MANILA, MANILA_DK = '#E6C47C', '#C9A55C'
FLOOR_Y = 390        # where feet stand in the front of the room


def f(n):
    """A number for a path: one decimal, no trailing zero."""
    s = f'{n:.1f}'
    return '0' if s in ('0.0', '-0.0') else (s[:-2] if s.endswith('.0') else s)


def pts(*ps):
    return ' L'.join(f'{f(x)},{f(y)}' for x, y in ps)


def tube(points, w, fill, ow=2.4, ink=INK):
    """An outlined tube along a polyline: (the ink stroke, the colour stroke). Draw every ink before every colour."""
    d = 'M' + pts(*points)
    return (f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{f(w + 2 * ow)}" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


# ======================================================================================== hands: three fingers and a thumb
# Each hand is drawn pointing along +x from the wrist at (0, 0), the thumb on the -y side; arm() turns it to the forearm
# (or to `ang`) and `flip` puts the thumb on the other side. Parts are (start, end, width): the palm, three fingers, the
# thumb. Fingers that touch get a seam line, so they read as three.
HANDS = {
    'open': dict(palm=((1, 0), (6.5, 0), 10.5), fingers=[((8.5, -3.8), (15.5, -5.6)), ((9.5, -0.2), (17.2, -0.8)), ((8.5, 3.6), (15.2, 5.0))],
                 thumb=((4, -4.4), (8, -10.4)), seams=False),
    'wave': dict(palm=((1, 0), (6.5, 0), 10.5), fingers=[((8, -3.8), (13.4, -8.8)), ((9.2, -0.4), (16.4, -2.2)), ((8.6, 3.4), (15.6, 4.2))],
                 thumb=((3.8, -4.6), (4.6, -11.6)), seams=False),
    'flat': dict(palm=((1, 0), (6, 0), 10.5), fingers=[((8, -3.6), (12.8, -4.0)), ((8.6, 0), (13.8, 0)), ((8, 3.6), (12.8, 4.0))],
                 thumb=((3.5, -4.8), (6.8, -8.4)), seams=True),
    'fist': dict(palm=((0.5, 0), (5.5, 0), 11), fingers=[((7.6, -3.7), (9.9, -3.6)), ((8.2, 0), (10.5, 0)), ((7.6, 3.7), (9.9, 3.8))],
                 thumb=((3, -5.2), (8.4, -6.6)), seams=True),
    'point': dict(palm=((0.5, 0), (5.5, 0), 11), fingers=[((8, -3.7), (19, -4.6)), ((8.2, 0.2), (10.5, 0.3)), ((7.6, 3.8), (9.9, 3.9))],
                  thumb=((3, -5.2), (8, -5.8)), seams=True),
    'wrap': dict(palm=((-1, 0), (2.5, 0), 10.5), fingers=[((4, -4.1), (12.6, -4.5)), ((4.6, 0), (13.4, 0)), ((4, 4.1), (12.6, 4.5))],
                 thumb=((0.5, -5.6), (7.6, -8.8)), seams=True),
    'pinch': dict(palm=((0.5, 0), (5.5, 0), 10.5), fingers=[((7.4, -2.6), (9.8, -2.4)), ((7.8, 1.2), (10.2, 1.3)), ((7.2, 4.8), (9.4, 4.9))],
                  thumb=((3, -5), (11.4, -7.4)), seams=True),
}
FINGER_W, THUMB_W, HAND_OW, HAND_SCALE = 3.8, 4.1, 1.5, 1.25


def hand(H, ang, pose, skin, flip=1):
    P = HANDS[pose]
    parts = [P['palm']] + [(a, b, FINGER_W) for a, b in P['fingers']]
    ink = ''.join(tube([a, b], w, skin, HAND_OW)[0] for a, b, w in parts)
    fill = ''.join(tube([a, b], w, skin, HAND_OW)[1] for a, b, w in parts)
    seams = ''
    if P['seams']:
        fs = P['fingers']
        for (a1, b1), (a2, b2) in zip(fs, fs[1:]):
            s0 = lerp(a1, a2, 0.5)
            s1 = lerp(b1, b2, 0.5)
            s1 = lerp(s0, s1, 0.8)
            seams += f'<path d="M{f(s0[0] + 0.6)},{f(s0[1])} L{f(s1[0])},{f(s1[1])}" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>'
    a, b = P['thumb']
    th = tube([a, b], THUMB_W, skin, HAND_OW)
    return (f'<g transform="translate({f(H[0])} {f(H[1])}) rotate({f(ang)}) scale({HAND_SCALE} {HAND_SCALE * flip})">'
            + ink + fill + seams + th[0] + th[1] + '</g>')


def held_glass(H, ang, s=1.2):
    """The glass a 'wrap' hand at H is holding by its side, out at the fingertips, so the whisky still shows."""
    c = add(H, rot((19, 0), ang))
    return glass(c[0], c[1] + 8 * s, s)


def arm(S, E, H, shirt, skin, pose='fist', ang=None, flip=1, cls=None, hold='', over='', watch=False, ow=2.4):
    """A shirt-sleeved arm, sleeve rolled to the elbow: shoulder S, elbow E, hand H. `hold` is drawn under the hand, `over`
    over it. `ang` turns the hand away from the line of the forearm (a wrist bends)."""
    sleeve = tube([S, E], 14, shirt, ow)
    fore = tube([lerp(E, H, 0.12), H], 9.5, skin, ow)
    cuff = tube([lerp(E, H, 0.04), lerp(E, H, 0.30)], 15.5, shirt, ow)
    ux, uy = H[0] - E[0], H[1] - E[1]
    L = math.hypot(ux, uy) or 1
    nx, ny = -uy / L * 7, ux / L * 7
    m = lerp(E, H, 0.17)
    fold = f'<path d="M{f(m[0] + nx)},{f(m[1] + ny)} L{f(m[0] - nx)},{f(m[1] - ny)}" fill="none" stroke="{INK}" stroke-width="1.3"/>'
    if ang is None:
        ang = math.degrees(math.atan2(uy, ux))
    s = f'<g class="{cls}">' if cls else '<g>'
    s += sleeve[0] + fore[0] + sleeve[1] + fore[1] + cuff[0] + cuff[1] + fold
    if watch:
        p = lerp(H, E, 0.3)
        s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="3.4" fill="#D9A441" stroke="{INK}" stroke-width="1.4"/>'
    s += hold + hand(H, ang, pose, skin, flip) + over
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


def crescent(cx, cy, r1, dx, dy, r2):
    """A crescent: the circle (cx, cy, r1) less the circle offset by (dx, dy) with radius r2."""
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(r1 * r1 - a * a)
    ux, uy = dx / d, dy / d
    px, py = cx + a * ux, cy + a * uy
    i1 = (px - h * uy, py + h * ux)
    i2 = (px + h * uy, py - h * ux)
    return (f'M{f(i1[0])},{f(i1[1])} A{f(r1)},{f(r1)} 0 1 1 {f(i2[0])},{f(i2[1])} '
            f'A{f(r2)},{f(r2)} 0 0 0 {f(i1[0])},{f(i1[1])} Z')


def window():
    """The city through the window. Drawn at night; the page's script turns it to the hour (see the module notes)."""
    r = lcg(31)
    s = f'  <g class="window" stroke="{LINE}" stroke-width="1.3">\n'
    s += '    <rect x="398" y="24" width="224" height="190" fill="#4E321D"/>\n'
    for i, (y, h, c) in enumerate(((32, 50, '#1B1638'), (82, 40, '#231C45'), (122, 36, '#2E2552'), (158, 48, '#3C2C5C'))):
        s += f'    <rect class="sky" data-band="{i}" x="406" y="{y}" width="208" height="{h}" fill="{c}" stroke="none"/>\n'
    s += ('    <g class="sun" opacity="0" transform="translate(510 200)" stroke="none"><circle r="17" fill="#F6D365" fill-opacity="0.3"/>'
          '<circle r="11" fill="#F6D365"/></g>\n')
    s += f'    <g class="moon" stroke="none"><path d="{crescent(590, 104, 10, 4.5, -4, 8.5)}" fill="#F2E6C4"/></g>\n'
    s += '    <g class="stars" stroke="none">'
    for x, y in ((430, 96), (466, 112), (540, 92), (582, 128), (452, 140), (520, 124), (488, 100)):
        s += f'<circle cx="{x}" cy="{y}" r="1.1" fill="#F3E9C6"/>'
    s += '</g>\n'
    # the skyline: back row, front row, a water tower, the windows of the towers (some twinkle)
    back = [(406, 150), (424, 132), (446, 158), (470, 120), (494, 146), (518, 128), (548, 152), (572, 136), (596, 156)]
    for i, (x, top) in enumerate(back):
        w = (back[i + 1][0] if i + 1 < len(back) else 614) - x
        s += f'    <rect class="bldg-back" x="{x}" y="{top}" width="{w}" height="{206 - top}" fill="#1E2040" stroke="none"/>\n'
    front = [(406, 172, 22), (432, 160, 26), (466, 176, 20), (492, 154, 30), (530, 170, 24), (560, 162, 28), (594, 178, 20)]
    for x, top, w in front:
        s += f'    <rect class="bldg-front" x="{x}" y="{top}" width="{w}" height="{206 - top}" fill="#15172E" stroke="none"/>\n'
        for wy in range(top + 6, 202, 8):
            for wx in range(x + 4, x + w - 4, 7):
                v = next(r)
                if v < 0.42:
                    c = '#F2C14E' if v > 0.12 else '#E89B3A'
                    cls = 'lit twinkle' if v < 0.05 else 'lit'
                    s += f'    <rect class="{cls}" data-c="{c}" x="{wx}" y="{wy}" width="3" height="4" fill="{c}" stroke="none"/>\n'
    s += ('    <path class="bldg-front" d="M500,154 L500,144 L506,140 L512,144 L512,154 Z" fill="#15172E" stroke="none"/>'
          '<rect class="bldg-front" x="501" y="153" width="1.6" height="7" fill="#15172E" stroke="none"/>'
          '<rect class="bldg-front" x="509.4" y="153" width="1.6" height="7" fill="#15172E" stroke="none"/>\n')
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


CLOCK = (317, 23)


def clock():
    """The wall clock. Its hands point at twelve and are turned by their transform: ten to eleven here, the real time in
    Chicago on the page."""
    cx, cy = CLOCK
    s = f'  <g class="clock" stroke="{LINE}" stroke-width="1.2">\n'
    s += f'    <circle cx="{cx}" cy="{cy}" r="13" fill="#C9A24A"/><circle cx="{cx}" cy="{cy}" r="10.5" fill="#F3EBD6"/>\n'
    for i in range(12):
        a = math.radians(i * 30)
        s += f'    <path d="M{f(cx + 8.6 * math.sin(a))},{f(cy - 8.6 * math.cos(a))} L{f(cx + 10 * math.sin(a))},{f(cy - 10 * math.cos(a))}" stroke="#3A2A18" stroke-width="1"/>\n'
    s += f'    <path class="hour" d="M{cx},{cy} L{cx},{f(cy - 5.6)}" stroke="{INK}" stroke-width="2" stroke-linecap="round" transform="rotate(325 {cx} {cy})"/>\n'
    s += f'    <path class="minute" d="M{cx},{cy} L{cx},{f(cy - 8.4)}" stroke="{INK}" stroke-width="1.4" stroke-linecap="round" transform="rotate(300 {cx} {cy})"/>\n'
    s += f'    <path class="second" d="M{cx},{f(cy + 2.4)} L{cx},{f(cy - 9)}" stroke="#B23A2E" stroke-width="0.8" stroke-linecap="round" transform="rotate(0 {cx} {cy})"/>\n'
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
    s += '    <ellipse cx="252" cy="215" rx="10" ry="2.8" fill="#C9A24A"/><rect x="250.6" y="196" width="2.8" height="18" fill="#C9A24A" stroke-width="0.8"/>\n'
    s += '    <path d="M236,201 Q252,186 268,201 L266,205 L238,205 Z" fill="#2E6A49"/>\n'
    s += '    <path d="M241,198 Q252,190 263,198" fill="none" stroke="#4E9A70" stroke-width="1.4"/>\n'
    s += '    <path d="M262,205 L262,211" stroke="#C9A24A" stroke-width="1"/>\n'
    for i, c in enumerate(('#B23A2E', '#D9A441', '#2F6F73', '#3A3E48')):
        x = 274 + i * 8
        s += f'    <rect x="{x}" y="{193 + (i % 2) * 2}" width="7.5" height="{23 - (i % 2) * 2}" fill="{c}"/><rect x="{x + 1.5}" y="{198 + (i % 2) * 2}" width="4.5" height="5" fill="#EFE6CE" stroke-width="0.6"/>\n'
    s += f'    <path d="M368,216 C366,207 368,199 374,195 L374,189 L382,189 L382,195 C388,199 390,207 388,216 Z" fill="{GLASS}" fill-opacity="0.55"/>\n'
    s += f'    <path d="M367.6,216 C366.8,211 367.2,207 368.4,204 L387.6,204 C388.8,207 389.2,211 388.4,216 Z" fill="{WHISKY}" stroke="none"/>\n'
    s += '    <path d="M368,216 C366,207 368,199 374,195 L374,189 L382,189 L382,195 C388,199 390,207 388,216 Z" fill="none"/>\n'
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
            '<path d="M-7.5,-15 L7.5,-15 L6.5,0 L-6.5,0 Z" fill="none"/>'
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


def terminal():
    """The PC, turned to face the chair: we see the CRT side-on (the big face to the right, the tube tapering away to the
    left), the system unit's side under it, and the green of the screen falling toward whoever is typing."""
    s = '  <path d="M246,232 L304,216 L304,302 L246,292 Z" fill="#4DFF88" fill-opacity="0.09"/>\n'
    s += f'  <g class="pc" stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    # the system unit: its side to us, its drives toward the chair
    s += '    <path d="M170,312 L170,292 L178,287 L254,287 L248,292 L248,312 Z" fill="#D8CCB0"/>\n'
    s += '    <path d="M170,292 L178,287 L254,287 L248,292 Z" fill="#E6DCC4" stroke-width="1.4"/>\n'
    s += '    <path d="M248,292 L254,287 L254,307 L248,312 Z" fill="#C4B796" stroke-width="1.4"/>\n'
    s += '    <path d="M250.5,293 L250.5,298 M252.5,292 L252.5,297" stroke="#2A2620" stroke-width="1.2"/>\n'
    for x in range(178, 200, 4):
        s += f'    <path d="M{x},296 L{x},307" stroke="#B4A788" stroke-width="1.2"/>\n'
    # the CRT in profile, on its swivel foot
    s += '    <path d="M210,287 L214,282 L236,282 L240,287 Z" fill="#C9BD9F" stroke-width="1.6"/>\n'
    s += '    <path d="M240,230 L240,284 L204,281 C196,280 192,276 192,270 L192,250 C192,244 196,240 204,238 Z" fill="#DCD1B6"/>\n'
    s += '    <path d="M204,238 L240,230 L247,226 L212,234 Z" fill="#E6DCC4" stroke-width="1.6"/>\n'
    s += '    <path d="M240,230 L247,226 L247,287 L240,284 Z" fill="#C9BD9F"/>\n'
    s += '    <path d="M243.5,233 L246,231.5 L246,282 L243.5,281 Z" fill="#4DFF88" stroke="none"/>\n'
    for y in range(248, 274, 5):
        s += f'    <path d="M198,{y} L206,{y - 1}" stroke="#B4A788" stroke-width="1.3"/>\n'
    s += '    <path d="M192,268 C186,270 184,282 186,304" fill="none" stroke-width="1.6"/>\n'
    return s + '  </g>\n'


def printer(stage):
    """The dot-matrix printer, its back to us: paper goes in below and comes out over the top toward us."""
    s = f'  <g class="printer" stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <path d="M262,292 C262,280 288,280 288,292" fill="#FFFFFF" stroke-width="1.4"/>\n'
    s += '    <path d="M265,286 L285,286" stroke="#BFE3BC" stroke-width="2.6"/>\n'
    s += '    <path d="M256,312 L253,294 L299,294 L296,312 Z" fill="#D8CCB0"/>\n'
    s += '    <rect x="259" y="296" width="34" height="4" fill="#3A372F" stroke-width="1"/>\n'
    cls = ' class="printhead"' if stage == 'spec' else ''
    s += f'    <rect{cls} x="262" y="295" width="6" height="6" fill="#8A8170" stroke-width="1"/>\n'
    s += '    <path d="M260,306 L290,306" stroke="#B4A788" stroke-width="1.2"/>\n'
    return s + '  </g>\n'


def printout():
    """Spec: the printout feeding off the near edge of the desk and folding onto the carpet."""
    s = f'  <g stroke="{INK}" stroke-width="1.4" stroke-linejoin="round">\n'
    s += '    <g class="feed">\n'
    s += '      <path d="M258,318 L292,318 L292,378 L258,378 Z" fill="#FFFFFF"/>\n'
    for y in range(324, 376, 10):
        s += f'      <rect x="262" y="{y}" width="26" height="4" fill="#BFE3BC" stroke="none"/>\n'
    for y in range(322, 378, 6):
        s += f'      <circle cx="260.5" cy="{y}" r="0.9" fill="#9A9A9A" stroke="none"/><circle cx="289.5" cy="{y}" r="0.9" fill="#9A9A9A" stroke="none"/>\n'
    s += '    </g>\n'
    s += '    <path d="M252,394 L298,394 L300,386 L254,386 Z" fill="#FFFFFF"/><path d="M254,386 L300,386 L296,380 L256,380 Z" fill="#F2F2EC"/>\n'
    s += '    <path d="M262,389 L292,389" stroke="#BFE3BC" stroke-width="2.4"/>\n'
    return s + '  </g>\n'


def keyboard():
    """At the far edge of the desk, in front of the chair."""
    s = f'  <g stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">\n'
    s += '    <path d="M300,302 L360,302 L364,309 L296,309 Z" fill="#D8CCB0"/>\n'
    for i, y in enumerate((304.3, 306.6)):
        x0 = 300 - i * 1.4
        s += f'    <path d="M{f(x0)},{y} L{f(x0 + 60 + i * 2.8)},{y}" stroke="#7E7461" stroke-width="1.3" stroke-dasharray="3 1.5"/>\n'
    return s + '  </g>\n'


def desk_top():
    return (f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
            '    <path d="M172,304 L488,304 L498,318 L162,318 Z" fill="#8E5D36"/>\n'
            '    <path d="M190,313 L240,313 M380,313 L470,313" stroke="#9E6B41" stroke-width="1.4"/>\n'
            '  </g>\n')


def desk_front():
    """The desk's front: a walnut modesty panel in three raised fields (the drawers face the chair), the two nameplates."""
    s = f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <path d="M150,393 L510,393 L522,399 L138,399 Z" fill="#1F4245" stroke="none"/>\n'
    s += '    <rect x="164" y="324" width="332" height="69" fill="#6C4327"/>\n'
    s += '    <rect x="160" y="318" width="340" height="7" fill="#A36D42"/>\n'
    for x0, w in ((172, 90), (270, 120), (398, 90)):
        s += f'    <rect x="{x0}" y="331" width="{w}" height="54" fill="#76492A" stroke-width="1.6"/>\n'
        s += f'    <path d="M{x0 + 4},381 L{x0 + 4},335 L{x0 + w - 4},335" fill="none" stroke="#8E5D36" stroke-width="2"/>\n'
        s += f'    <path d="M{x0 + 4},381 L{x0 + w - 4},381 L{x0 + w - 4},335" fill="none" stroke="#5A371F" stroke-width="2"/>\n'
    s += '    <rect x="168" y="388" width="324" height="5" fill="#5A371F" stroke-width="1.4"/>\n'
    for y, name in ((340, 'JAMES · CTO'), (358, 'JOHN · CHIEF ENGINEER')):
        s += f'    <rect x="282" y="{y}" width="96" height="14" rx="1.5" fill="#D1A447" stroke-width="1.3"/>\n'
        s += f'    <text x="330" y="{y + 9.6}" text-anchor="middle" font-family="{TYPE}" font-size="6.6" font-weight="700" fill="#3A2A10" stroke="none">{escape(name)}</text>\n'
    return s + '  </g>\n'


def desk_items(stage, johns_glass, james_glass):
    s = '  <g>\n'
    if johns_glass:
        s += '    ' + glass(380, 313) + '\n'
    s += (f'    <g stroke="{INK}" stroke-width="1.8" stroke-linejoin="round">'
          '<path d="M394,313 L422,313 L419,306 L397,306 Z" fill="#C68A3A" fill-opacity="0.9"/>'
          '<path d="M397,306 Q408,303 419,306" fill="none" stroke-width="1.2"/>'
          '<path d="M400,311 L416,311" stroke="#E7B66A" stroke-width="1.4"/></g>\n')
    s += '    ' + cigar((404, 305), (386, 298), 's1') + '\n'
    s += '    ' + cigar((412, 305), (431, 297), 's2') + '\n'
    if james_glass:
        s += '    ' + glass(444, 313) + '\n'
    if stage != 'flowchart':
        s += '    ' + pail(460, 312, 0.95, open_=stage not in ('idle', 'tim'), sticks=stage not in ('idle', 'tim')) + '\n'
    s += '    ' + pail(480, 313, 1.0) + '\n'
    s += '    ' + pail(468, 316, 0.9, open_=True) + '\n'
    return s + '  </g>\n'


def chair(empty):
    """The tufted leather chair behind the desk; all its buttons show when nobody is in it."""
    s = f'  <g stroke="{INK}" stroke-width="2" stroke-linejoin="round">\n'
    s += '    <path d="M286,304 L286,236 C286,206 374,206 374,236 L374,304 Z" fill="#6E2A22"/>\n'
    s += '    <path d="M292,300 L292,238 C292,214 368,214 368,238 L368,300" fill="none" stroke="#8A3A30" stroke-width="2"/>\n'
    for y in (226, 244, 262, 280):
        for x in (300, 316, 330, 344, 360):
            if empty or not (296 < x < 364 and y > 230):
                s += f'    <circle cx="{x}" cy="{y}" r="1.5" fill="#4A1A14" stroke="none"/>\n'
    return s + '  </g>\n'


def crumpled():
    """Failed: a few drafts screwed up and thrown at the carpet."""
    s = f'  <g stroke="{INK}" stroke-width="1.6" stroke-linejoin="round">\n'
    for x, y, r in ((128, 386, 7), (146, 392, 5.5), (112, 393, 5)):
        s += f'    <circle cx="{x}" cy="{y}" r="{r}" fill="#F4F1E7"/>\n'
        s += f'    <path d="M{x - r * 0.6},{y - r * 0.2} L{x - r * 0.1},{y + r * 0.3} L{x + r * 0.5},{y - r * 0.4} M{x - r * 0.2},{y - r * 0.7} L{x + r * 0.1},{y - r * 0.2}" fill="none" stroke-width="1"/>\n'
    return s + '  </g>\n'


# ======================================================================================== the people
# Each man is drawn in his own coordinates and placed: James with his feet at (0, 0); John with (0, 0) at his middle, where
# the desk top crosses him when he sits, so his feet are at (0, 128). Seated, either sits in the chair behind the desk.
JAMES_SEAT = (330, 440)
JOHN_SEAT = (330, 304)
JOHN_FEET = 128
SL, SR = (-28, -181), (28, -181)            # James's shoulders
SJL, SJR = (-32, -45), (32, -45)            # John's shoulders

LOOKS = {'front': (0, 0), 'left': (-1.7, 0.2), 'right': (1.7, 0.2), 'down': (0, 1.5), 'up': (0.6, -1.3)}


def james_head(look='front', expr='smile'):
    dx, dy = LOOKS[look]
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
    # eyes: two white ovals that touch, dot pupils; open and level
    for ex in (-4.4, 4.4):
        s += f'    <ellipse cx="{ex}" cy="-221" rx="4.2" ry="5.2" fill="#FFFFFF" stroke-width="1.8"/>\n'
        s += f'    <circle cx="{f(ex + dx)}" cy="{f(-220.5 + dy)}" r="1.6" fill="{INK}" stroke="none"/>\n'
    s += f'    <g class="blink" opacity="0"><ellipse cx="-4.4" cy="-221" rx="4.2" ry="5.2" fill="{SKIN_JAMES}" stroke-width="1.8"/><ellipse cx="4.4" cy="-221" rx="4.2" ry="5.2" fill="{SKIN_JAMES}" stroke-width="1.8"/></g>\n'
    brow = {'stern': 'M-10,-229.5 L-2,-228 M2,-228 L10,-229.5', 'talk': 'M-10,-231.5 L-2,-232.5 M2,-232.5 L10,-231.5',
            'listen': 'M-10,-231 L-2,-231.5 M2,-231.5 L10,-231'}.get(expr, 'M-10,-230.5 L-2,-231 M2,-231 L10,-230.5')
    s += f'    <path d="{brow}" fill="none" stroke-width="2.6"/>\n'
    nx = dx * 0.6
    s += f'    <path d="M{f(0.5 + nx)},-215 Q{f(4.5 + nx)},-207.5 {f(1 + nx)},-206.5 Q{f(-1.5 + nx)},-206 {f(-3 + nx)},-207.5" fill="none" stroke-width="1.6"/>\n'
    mx = dx * 0.5
    if expr == 'talk':
        s += f'    <path d="M{f(-6 + mx)},-202.5 Q{f(mx)},-200.5 {f(6 + mx)},-202.5 Q{f(3 + mx)},-196 {f(mx)},-196.5 Q{f(-3 + mx)},-196 {f(-6 + mx)},-202.5 Z" fill="#5A2320" stroke-width="1.6"/>\n'
        s += f'    <path d="M{f(-3.5 + mx)},-201.6 L{f(3.5 + mx)},-201.6" stroke="#FFFFFF" stroke-width="1.4"/>\n'
    elif expr in ('stern', 'listen'):
        s += f'    <path d="M{f(-4.5 + mx)},-201.2 Q{f(mx)},-200.4 {f(4.5 + mx)},-201.2" fill="none" stroke-width="1.8"/>\n'
    else:
        s += f'    <path d="M{f(-5.5 + mx)},-202.2 Q{f(mx)},-198.6 {f(5.5 + mx)},-202.2" fill="none" stroke-width="1.8"/>\n'
    s += '    <path d="M-2.5,-196.6 Q0,-195.6 2.5,-196.6" fill="none" stroke="#9A6A4C" stroke-width="1.2"/>\n'
    return s + '    </g>\n'


def james_torso():
    s = f'    <path d="M-9,-190 C-19,-189 -29,-186 -32,-180 C-34,-160 -31,-135 -25,-112 L25,-112 C31,-135 34,-160 32,-180 C29,-186 19,-189 9,-190 Z" fill="{SHIRT_JAMES}"/>\n'
    s += f'    <path d="M-20,-140 Q-14,-136 -10,-140 M12,-160 Q16,-157 20,-160 M-18,-118 Q-14,-114 -10,-118 M12,-118 Q16,-114 20,-118" fill="none" stroke="{SHIRT_JAMES_DK}" stroke-width="1.5"/>\n'
    s += f'    <path d="M-5.5,-190 L0,-180 L5.5,-190 Z" fill="{SKIN_JAMES}" stroke-width="1.4"/>\n'
    for side in (-1, 1):
        a, b = (side * 14, -112), (side * 19, -186)
        s += ''.join(tube([a, b], 4.4, BRACES, ow=1.5))
        s += f'<rect x="{side * 14 - 3}" y="-121" width="6" height="5" fill="#C9A24A" stroke-width="1"/>\n'
    s += f'    <path d="M-3.8,-183 L3.8,-183 L2.8,-176 L-2.8,-176 Z" fill="{TIE_JAMES}"/>\n'
    s += f'    <path d="M-2.8,-176 L2.8,-176 L6.5,-128 L0,-121 L-6.5,-128 Z" fill="{TIE_JAMES}"/>\n'
    s += '    <path d="M-3.4,-166 L3.6,-171 M-4.4,-154 L4.4,-160 M-5.2,-142 L5.2,-148 M-5.6,-131 L5.8,-137" stroke="#D9A84A" stroke-width="1.3"/>\n'
    s += f'    <path d="M-9,-190 L-1,-181 L-11,-178 L-14,-186 Z M9,-190 L1,-181 L11,-178 L14,-186 Z" fill="{SHIRT_JAMES}" stroke-width="1.6"/>\n'
    return s


def shoe(x, y, out):
    """An oxford, its heel at (x, y), its toe pointing `out` (-1 left, 1 right)."""
    o = out
    return (f'<path d="M{f(x - o * 2)},{f(y - 9)} L{f(x + o * 15)},{f(y - 9)} C{f(x + o * 21)},{f(y - 8)} {f(x + o * 23)},{f(y - 3)} '
            f'{f(x + o * 21)},{f(y)} L{f(x - o * 3)},{f(y)} Z" fill="#1E1B1B"/>'
            f'<path d="M{f(x + o * 3)},{f(y - 6)} L{f(x + o * 11)},{f(y - 6)}" stroke="#57504C" stroke-width="1.4"/>')


def legs(who):
    """Trousers, belt and shoes, standing, in the man's own coordinates."""
    if who == 'james':
        top, crotch, foot, hw, color, belt = -112, -92, 0, 25, TROUSERS_JAMES, -115
    else:
        top, crotch, foot, hw, color, belt = 4, 26, JOHN_FEET, 35, TROUSERS_JOHN, 1
    s = (f'    <path d="M{-hw},{top} L{hw},{top} L{hw - 2},{f(top + (foot - top) * 0.48)} L{hw - 6},{foot - 8} L3,{foot - 8} L1,{crotch} '
         f'L-1,{crotch} L-3,{foot - 8} L{-hw + 6},{foot - 8} L{-hw + 2},{f(top + (foot - top) * 0.48)} Z" fill="{color}"/>\n')
    mid = hw * 0.45
    s += f'    <path d="M{f(-mid)},{top + 8} L{f(-mid)},{foot - 12} M{f(mid)},{top + 8} L{f(mid)},{foot - 12}" stroke="#50555F" stroke-opacity="0.7" stroke-width="1.4"/>\n'
    s += '    ' + shoe(-3, foot, -1) + shoe(3, foot, 1) + '\n'
    if who == 'james':
        s += f'    <rect x="-25" y="{belt}" width="50" height="7" fill="#3E2618" stroke-width="2"/><rect x="-3.5" y="{belt}" width="7" height="7" fill="#C9A24A" stroke-width="1.4"/>\n'
    else:
        s += f'    <rect x="-35" y="{belt}" width="70" height="7" fill="#2E1E14" stroke-width="2"/><rect x="-3.5" y="{belt}" width="7" height="7" fill="#C9A24A" stroke-width="1.4"/>\n'
    return s


def john_head(look='front', expr='smile'):
    dx, dy = LOOKS[look]
    s = '    <g class="head">\n'
    s += f'    <ellipse cx="-18.5" cy="-86" rx="3.4" ry="5.4" fill="{SKIN_JOHN}"/><ellipse cx="18.5" cy="-86" rx="3.4" ry="5.4" fill="{SKIN_JOHN}"/>\n'
    s += f'    <path d="M-18,-90 C-18,-106 -10,-112 0,-112 C10,-112 18,-106 18,-90 C18,-74 12,-62 0,-62 C-12,-62 -18,-74 -18,-90 Z" fill="{SKIN_JOHN}"/>\n'
    s += f'    <path d="M-18.5,-91 C-20,-108 -10,-115 0,-115 C10,-115 20,-108 18.5,-91 C16,-99 10,-103 0,-103 C-10,-103 -16,-99 -18.5,-91 Z" fill="{HAIR_JOHN}"/>\n'
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
    s += f'    <g>{"".join(tube([(10, -103), (30, -90)], 3.2, "#E8C34A", ow=1.3))}<path d="M28.5,-91 L33,-88 L30.5,-92.5 Z" fill="#3A2A18" stroke-width="0.8"/><path d="M10,-103 L13,-101" stroke="#E98A8A" stroke-width="3.2"/></g>\n'
    return s + '    </g>\n'


def john_torso():
    s = f'    <path d="M-7,-64 L-7,-52 L7,-52 L7,-64 Z" fill="{SKIN_JOHN}"/>\n'
    s += f'    <path d="M-10,-57 C-24,-56 -33,-52 -36,-45 C-38,-30 -37,-12 -35,6 L35,6 C37,-12 38,-30 36,-45 C33,-52 24,-56 10,-57 Z" fill="{SHIRT_JOHN}"/>\n'
    s += f'    <path d="M-6,-57 L0,-47 L6,-57 Z" fill="{SKIN_JOHN}" stroke-width="1.4"/>\n'
    s += f'    <path d="M-3.4,-49 L3.4,-49 L2.6,-42.5 L-2.6,-42.5 Z" fill="{TIE_JOHN}"/>\n'
    s += f'    <path d="M-2.6,-42.5 L2.6,-42.5 L5.5,4 L-5.5,4 Z" fill="{TIE_JOHN}"/>\n'
    s += '    <path d="M-3,-36 L3,-36 M-3.6,-28 L3.6,-28 M-4.2,-20 L4.2,-20 M-4.8,-12 L4.8,-12" stroke="#A97A22" stroke-width="1.2"/>\n'
    s += f'    <path d="M-10,-57 L-1,-48 L-11,-45 L-14,-53 Z M10,-57 L1,-48 L11,-45 L14,-53 Z" fill="{SHIRT_JOHN}" stroke-width="1.6"/>\n'
    s += f'    <path d="M12,-34 L27,-34 L27,-20 L12,-20 Z" fill="{SHIRT_JOHN_DK}" stroke-width="1.4"/>\n'
    for x, c in ((15, '#B23A2E'), (19, '#1F4E8C'), (23, INK)):
        s += f'    <rect x="{x - 1.3}" y="-40" width="2.6" height="9" rx="1" fill="{c}" stroke-width="0.9"/>\n'
    s += '    <path d="M12.5,-33 L26.5,-33 L26.5,-27 L12.5,-27 Z" fill="#F4F1EA" stroke-width="1.2"/>\n'
    s += f'    <path d="M-30,-20 Q-26,-17 -22,-20 M20,-4 Q24,-1 28,-4" fill="none" stroke="{SHIRT_JOHN_DK}" stroke-width="1.4"/>\n'
    return s


def head(who, look, expr):
    return (james_head if who == 'james' else john_head)(look, expr)


def arms(who, specs):
    """specs: (side, elbow, hand, pose, options) in the man's own coordinates; side 'L' is the arm on our left."""
    S = {'james': (SL, SR), 'john': (SJL, SJR)}[who]
    shirt, skin = (SHIRT_JAMES, SKIN_JAMES) if who == 'james' else (SHIRT_JOHN, SKIN_JOHN)
    out = ''
    for side, E, H, pose, kw in specs:
        kw = dict(kw)
        kw.setdefault('flip', 1 if side == 'L' else -1)
        out += arm(S[0] if side == 'L' else S[1], E, H, shirt, skin, pose, **kw)
    return out


def A(side, E, H, pose='fist', **kw):
    return (side, E, H, pose, kw)


def group(who, x, y, s, inner, cls=None):
    c = f' class="{cls}"' if cls else ''
    return (f'  <g{c} transform="translate({f(x)} {f(y)}) scale({s})" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" '
            f'stroke-linecap="round">\n{inner}  </g>\n')


def standing(who, x, look, expr, arm_specs, s=1.0, y=FLOOR_Y):
    """A man on his feet at (x, y), facing us."""
    oy = y if who == 'james' else y - JOHN_FEET * s
    torso = james_torso() if who == 'james' else john_torso()
    inner = legs(who) + torso + head(who, look, expr) + arms(who, arm_specs)
    shadow = f'  <ellipse cx="{f(x)}" cy="{f(y + 1)}" rx="{f(34 * s)}" ry="{f(6 * s)}" fill="#1F4245"/>\n'
    return shadow + group(who, x, oy, s, inner, cls=who)


def seated(who, look, expr):
    """A man in the chair behind the desk: his body (drawn before the desk). His arms come after the desk: seated_arms."""
    x, y = JAMES_SEAT if who == 'james' else JOHN_SEAT
    torso = james_torso() if who == 'james' else john_torso()
    return group(who, x, y, 1.0, torso + head(who, look, expr), cls=who)


def seated_arms(who, specs):
    x, y = JAMES_SEAT if who == 'james' else JOHN_SEAT
    return group(who, x, y, 1.0, arms(who, specs))


# Arm poses shared between scenes (each man's own coordinates).
def typing(who, cls=True):
    if who == 'james':
        L, R = A('L', (-40, -147), (-16, -132), 'flat', ang=78), A('R', (40, -147), (16, -131), 'flat', ang=102)
    else:
        L, R = A('L', (-42, -8), (-16, 5), 'flat', ang=78), A('R', (42, -8), (16, 6), 'flat', ang=102)
    if cls:
        L[4]['cls'], R[4]['cls'] = 'tap tap-l', 'tap tap-r'
    return [L, R]


def james_glass_chest():
    H = (24, -152)
    return A('R', (40, -146), H, 'wrap', ang=180, flip=-1, hold=held_glass(H, 180), watch=True)


def hanging(who, side):
    if who == 'james':
        x = -1 if side == 'L' else 1
        return A(side, (x * 40, -143), (x * 45, -102), 'flat', ang=100 if side == 'L' else 80)
    x = -1 if side == 'L' else 1
    return A(side, (x * 43, -8), (x * 48, 32), 'flat', ang=98 if side == 'L' else 82)


# ======================================================================================== walking, side-on
# A man walking his beat is drawn in profile, facing left (the page's CSS turns him round at each end). His legs are an
# eight-drawing cycle (classes f0..f7, one shown at a time): contact, down, passing, up on one leg, then the same on the
# other. His upper body rides on `bob`. James's coordinates; John's legs are the same drawings, scaled to his.
WALK = [  # (knee, ankle, foot angle) for the near leg, then the far leg; the second four swap them
    (((-8, -55), (-14, -9), -14), ((6, -55), (12, -13), 28)),     # contact
    (((-6, -51), (-9, -8), 0), ((8, -52), (14, -19), 35)),        # down
    (((-1, -56), (-1, -8), 0), ((-3, -60), (4, -25), 18)),        # passing
    (((3, -56), (5, -9), 8), ((-9, -60), (-15, -17), -6)),        # up
]
WALK = WALK + [(far, near) for near, far in WALK]


def shoe_side(A, ang, color='#1E1B1B'):
    """A shoe seen from the side, toe to the left, its ankle at A."""
    return (f'<g transform="translate({f(A[0])} {f(A[1])}) rotate({f(ang)})"><path d="M6,-3 L6,7 L-14,7 C-19,7 -20,2 -15,0 L-5,-3 Z" fill="{color}"/>'
            '<path d="M-14,5 L4,5" stroke="#57504C" stroke-width="1.3"/></g>')


def walk_frames(who):
    hip, k, w, near_c, far_c, shoe = {
        'james': ((0, -104), 1.0, 17, TROUSERS_JAMES, '#2C3038', '#1E1B1B'),
        'john': ((0, 12), 116 / 104, 21, TROUSERS_JOHN, '#47372A', '#1E1B1B'),
        'tim': ((0, -96), 96 / 104, 16, '#C8B387', '#A8956A', '#6B4A32'),
    }[who]
    P = lambda p: (p[0] * k, hip[1] + (p[1] + 104) * k)
    out = ''
    for i, (near, far) in enumerate(WALK):
        hidden = '' if i == 0 else ' opacity="0"'
        g = f'    <g class="f f{i}"{hidden}>'
        for (K, A_, fa), color in ((far, far_c), (near, near_c)):
            a, b = tube([hip, P(K), P(A_)], w, color)
            g += a + b + shoe_side(P(A_), fa, shoe)
        out += g + '</g>\n'
    return out


def james_side_head(expr='smile'):
    s = '    <g class="head">\n'
    s += f'    <path d="M-5,-202 L7,-202 L8,-185 L-6,-185 Z" fill="{SKIN_JAMES}"/>\n'
    s += (f'    <path d="M13,-232 C15,-222 14,-210 9,-203 L2,-198 C-4,-195 -10,-194 -13,-196 L-15,-199 L-14,-204 L-15,-207 L-14,-209 '
          f'L-20,-211 L-15,-219 L-14,-226 C-14,-234 -6,-242 2,-242 C9,-242 13,-238 13,-232 Z" fill="{SKIN_JAMES}"/>\n')
    s += (f'    <path d="M-14,-228 C-15,-240 -6,-250 4,-249 C13,-248 18,-240 16,-226 C15,-221 14,-219 12,-218 L9,-222 C8,-229 4,-233 '
          f'-2,-233 C-8,-233 -12,-231 -14,-228 Z" fill="{HAIR_JAMES}"/>\n')
    s += '    <path d="M6,-230 L11,-226 L10,-221 Z" fill="#B3ADA5" stroke-width="1.2"/>\n'
    s += f'    <path d="M3,-221 C9,-224 11,-212 4,-210 Z" fill="{SKIN_JAMES}" stroke-width="1.8"/><path d="M5,-218 Q7.5,-216 5.5,-213" fill="none" stroke-width="1.1"/>\n'
    s += '    <ellipse cx="-8" cy="-222" rx="3.2" ry="4.8" fill="#FFFFFF" stroke-width="1.8"/>'
    s += f'<circle cx="-9.6" cy="-221.6" r="1.5" fill="{INK}" stroke="none"/>\n'
    s += f'    <g class="blink" opacity="0"><ellipse cx="-8" cy="-222" rx="3.2" ry="4.8" fill="{SKIN_JAMES}" stroke-width="1.8"/></g>\n'
    s += '    <path d="M-13,-229.5 L-4,-230.5" fill="none" stroke-width="2.6"/>\n'
    s += '    <path d="M-14.2,-203.6 Q-11,-202.4 -8,-204" fill="none" stroke-width="1.7"/>\n'
    return s + '    </g>\n'


def james_side_torso():
    s = f'    <path d="M-6,-190 C-14,-188 -17,-178 -17,-166 C-17,-148 -16,-130 -14,-112 L13,-112 C15,-130 16,-150 15,-170 C14,-182 10,-189 4,-191 Z" fill="{SHIRT_JAMES}"/>\n'
    s += f'    <path d="M-12,-184 C-16,-170 -19,-150 -18,-130 L-14,-127 C-14,-150 -12,-170 -9,-184 Z" fill="{TIE_JAMES}"/>\n'
    s += f'    <path d="M-7,-191 L-13,-184 L-6,-182 Z" fill="{SHIRT_JAMES}" stroke-width="1.5"/>\n'
    s += ''.join(tube([(3, -112), (4, -150), (3, -189)], 4.4, BRACES, ow=1.5)) + '\n'
    s += f'    <path d="M-15,-112 L14,-112 L15,-96 L-15,-96 Z" fill="{TROUSERS_JAMES}"/>\n'
    s += '    <rect x="-16" y="-115" width="31" height="7" fill="#3E2618" stroke-width="2"/>\n'
    return s


def john_side_head(expr='smile'):
    s = '    <g class="head">\n'
    s += f'    <path d="M-6,-66 L8,-66 L9,-52 L-7,-52 Z" fill="{SKIN_JOHN}"/>\n'
    s += (f'    <path d="M16,-92 C17,-76 12,-64 2,-61 C-6,-59 -12,-62 -15,-68 L-16,-76 L-17,-80 L-21,-83 L-17,-88 L-16,-96 '
          f'C-15,-106 -8,-112 1,-112 C10,-112 16,-104 16,-92 Z" fill="{SKIN_JOHN}"/>\n')
    s += f'    <path d="M-16,-96 C-15,-108 -7,-115 2,-115 C12,-115 19,-106 17,-92 C15,-96 12,-99 8,-100 C2,-104 -10,-102 -16,-96 Z" fill="{HAIR_JOHN}"/>\n'
    s += (f'    <path d="M9,-84 C11,-72 6,-61 -2,-59 C-9,-58 -14,-62 -16,-68 L-16,-74 C-12,-72 -8,-72 -6,-75 C-2,-74 2,-78 4,-84 Z" fill="{BEARD_JOHN}"/>\n')
    s += f'    <path d="M-17,-77 Q-12,-80 -7,-76 Q-12,-75 -17,-77 Z" fill="{BEARD_JOHN}" stroke-width="1.2"/>\n'
    s += '    <path d="M-15.6,-72.6 Q-12,-71 -9,-73" fill="none" stroke="#E2C9B8" stroke-width="1.5"/>\n'
    s += f'    <path d="M4,-92 C10,-95 12,-83 5,-81 Z" fill="{SKIN_JOHN}" stroke-width="1.8"/>\n'
    s += '    <path d="M-6,-93 L6,-90" fill="none" stroke="#2B1A10" stroke-width="2"/>\n'
    s += '    <rect x="-17" y="-98" width="11" height="11" rx="3.5" fill="#FFFFFF" stroke="#2B1A10" stroke-width="2.6"/>\n'
    s += f'    <circle cx="-14.2" cy="-92.4" r="1.9" fill="{INK}" stroke="none"/>\n'
    s += f'    <g class="blink" opacity="0"><rect x="-15.6" y="-96.6" width="8.2" height="8.2" rx="2.4" fill="{SKIN_JOHN}" stroke="none"/></g>\n'
    s += '    <path d="M-17,-102 L-7,-103" fill="none" stroke-width="2.6"/>\n'
    s += f'    <g>{"".join(tube([(2, -104), (20, -92)], 3.2, "#E8C34A", ow=1.3))}<path d="M18.6,-93 L23,-90 L20.4,-94.6 Z" fill="#3A2A18" stroke-width="0.8"/></g>\n'
    return s + '    </g>\n'


def john_side_torso():
    s = f'    <path d="M-7,-58 C-20,-55 -25,-42 -25,-26 C-25,-10 -23,0 -21,8 L18,8 C20,-8 20,-30 18,-44 C16,-54 10,-58 2,-59 Z" fill="{SHIRT_JOHN}"/>\n'
    s += f'    <path d="M-15,-50 C-20,-38 -24,-20 -23,4 L-19,6 C-20,-18 -17,-38 -12,-50 Z" fill="{TIE_JOHN}"/>\n'
    s += f'    <path d="M-8,-58 L-16,-50 L-7,-48 Z" fill="{SHIRT_JOHN}" stroke-width="1.5"/>\n'
    s += f'    <path d="M-21,8 L18,8 L19,26 L-21,26 Z" fill="{TROUSERS_JOHN}"/>\n'
    s += '    <rect x="-22" y="4" width="41" height="7" fill="#2E1E14" stroke-width="2"/>\n'
    return s


def walker(who, x, holding, y=FLOOR_Y):
    """A man pacing in front of the window, side-on, with something in his near hand."""
    if who == 'james':
        S, shirt, skin, oy = (1, -180), SHIRT_JAMES, SKIN_JAMES, y
        body = james_side_torso() + james_side_head()
        E, H = (6, -146), (-14, -152)
    else:
        S, shirt, skin, oy = (0, -44), SHIRT_JOHN, SKIN_JOHN, y - JOHN_FEET
        body = john_side_torso() + john_side_head()
        E, H = (6, -10), (-18, -18)
    if holding == 'glass':
        hold = glass(H[0] - 14, H[1] + 9, 1.2)
        near = arm(S, E, H, shirt, skin, 'wrap', ang=180, flip=-1, hold=hold)
    elif holding == 'sheet':
        sheet = (f'<g transform="rotate(14 {H[0] - 14} {H[1] - 22})" stroke="{INK}" stroke-width="1.4"><path d="M{H[0] - 26},{H[1] - 46} L{H[0] - 4},{H[1] - 46} L{H[0] - 4},{H[1] + 2} L{H[0] - 26},{H[1] + 2} Z" fill="#FFFFFF"/>'
                 + ''.join(f'<path d="M{H[0] - 23},{H[1] - 40 + 8 * i} L{H[0] - 7},{H[1] - 40 + 8 * i}" stroke="#BFE3BC" stroke-width="3.2"/>' for i in range(5)) + '</g>')
        near = arm(S, E, H, shirt, skin, 'pinch', ang=200, flip=1, hold=sheet)
    else:  # the memo, open in his hands
        folder = (f'<g stroke="{INK}" stroke-width="2"><path d="M{H[0] - 30},{H[1] - 34} L{H[0] - 4},{H[1] - 30} L{H[0] - 2},{H[1] + 2} L{H[0] - 28},{H[1] - 2} Z" fill="{MANILA}"/>'
                  f'<path d="M{H[0] - 26},{H[1] - 24} L{H[0] - 8},{H[1] - 22} M{H[0] - 26},{H[1] - 16} L{H[0] - 10},{H[1] - 14}" stroke="#8A8A8A" stroke-width="1.2"/></g>')
        near = arm(S, E, H, shirt, skin, 'pinch', ang=200, flip=1, hold=folder)
    inner = walk_frames(who) + f'    <g class="bob">\n{body}{near}    </g>\n'
    shadow = f'  <ellipse cx="{f(x)}" cy="{f(y + 1)}" rx="26" ry="5.5" fill="#1F4245"/>\n'
    # transform-origin: the CSS turns him about his own feet
    return f'  <g class="pace" transform-origin="{f(x)} {f(y)}">\n{shadow}{group(who, x, oy, 1.0, inner, cls=who)}  </g>\n'


def tim_side():
    """Tim walking in, side-on, the memo against his chest (drawn facing left; tim() turns him to face right)."""
    s = walk_frames('tim')
    s += '    <g class="bob">\n'
    s += f'    <path d="M-5,-190 L6,-190 L7,-176 L-6,-176 Z" fill="{SKIN_TIM}"/>\n'
    s += '    <path d="M-6,-180 C-13,-178 -16,-168 -16,-156 C-16,-140 -15,-120 -13,-104 L12,-104 C14,-122 15,-142 14,-160 C13,-172 9,-180 3,-181 Z" fill="#FBF8F0"/>\n'
    s += '    <path d="M-15,-160 C-16,-142 -15,-122 -13,-104 L12,-104 C14,-122 15,-142 14,-162 L4,-170 L-8,-166 Z" fill="#7D8B3F"/>\n'
    s += '    <path d="M-11,-176 C-14,-170 -15,-164 -15,-158 L-12,-157 C-12,-163 -10,-169 -8,-176 Z" fill="#2F6F73"/>\n'
    s += '    <path d="M-6,-181 L-12,-175 L-5,-173 Z" fill="#FBF8F0" stroke-width="1.5"/>\n'
    s += '    <path d="M-14,-104 L12,-104 L13,-90 L-14,-90 Z" fill="#C8B387"/>\n'
    s += (f'    <path d="M12,-212 C13,-200 9,-189 0,-186 C-6,-184 -11,-187 -12,-191 L-13,-195 L-12,-198 L-16,-201 L-12,-207 L-12,-214 '
          f'C-11,-225 -3,-230 2,-230 C8,-230 12,-224 12,-212 Z" fill="{SKIN_TIM}"/>\n')
    s += (f'    <path d="M-12,-212 C-14,-226 -4,-234 4,-233 C12,-232 16,-224 14,-210 L11,-208 C10,-216 6,-221 0,-221 C-5,-221 -9,-218 -12,-212 Z" fill="{HAIR_TIM}"/>\n')
    s += f'    <path d="M2,-232 C3,-239 8,-240 9,-237 C6,-237 4,-235 4,-231 Z" fill="{HAIR_TIM}" stroke-width="1.6"/>\n'
    s += f'    <path d="M2,-207 C8,-210 10,-198 3,-196 Z" fill="{SKIN_TIM}" stroke-width="1.8"/>\n'
    s += f'    <ellipse cx="-6" cy="-208" rx="3" ry="4.4" fill="#FFFFFF" stroke-width="1.7"/><circle cx="-7.4" cy="-207.6" r="1.5" fill="{INK}" stroke="none"/>\n'
    s += '    <path d="M-11,-214.5 L-3,-215" fill="none" stroke-width="2.2"/>\n'
    s += '    <path d="M-12.6,-194 Q-9,-191 -6,-194" fill="none" stroke-width="1.7"/>\n'
    folder = (f'<g stroke="{INK}" stroke-width="2"><path d="M-30,-168 L-14,-166 L-16,-122 L-32,-124 Z" fill="{MANILA}"/>'
              f'<path d="M-28,-150 L-18,-149" stroke="#B23A2E" stroke-width="1.6"/></g>')
    s += arm((0, -170), (5, -136), (-14, -142), '#FBF8F0', SKIN_TIM, 'pinch', ang=200, flip=1, hold=folder)
    return s + '    </g>\n'


# ======================================================================================== Tim, the EA, with the memo
def tim():
    """Tim walks in side-on (tim-side, the page's CSS walks him in) and turns to face the room (tim-front, the still)."""
    s = '  <g class="tim">\n'
    s += '  <ellipse cx="96" cy="391" rx="28" ry="5.5" fill="#1F4245"/>\n'
    s += (f'  <g class="tim-side" opacity="0"><g transform="translate(96 390) scale(-0.9 0.9)" stroke="{INK}" stroke-width="2.4" '
          f'stroke-linejoin="round" stroke-linecap="round">\n{tim_side()}  </g></g>\n')
    s += f'  <g class="tim-front"><g transform="translate(96 390) scale(0.9)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">\n'
    s += '    <path d="M-22,-104 L22,-104 L20,-56 L17,-8 L3,-8 L1,-88 L-1,-88 L-3,-8 L-17,-8 L-20,-56 Z" fill="#C8B387"/>\n'
    s += '    <path d="M-19,-9 L-3,-9 L-2,0 L-23,0 C-25,-3 -23,-8 -19,-9 Z M3,-9 L19,-9 C23,-8 25,-3 23,0 L2,0 Z" fill="#6B4A32"/>\n'
    s += '    <path d="M-8,-182 C-18,-181 -26,-178 -29,-172 C-31,-152 -28,-126 -23,-104 L23,-104 C28,-126 31,-152 29,-172 C26,-178 18,-181 8,-182 Z" fill="#FBF8F0"/>\n'
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
    # the memo from the owner in a manila folder, held to his chest, his thumb over its edge
    folder = (f'<g stroke="{INK}" stroke-width="2"><path d="M-30,-166 L2,-160 L0,-118 L-32,-124 Z" fill="{MANILA}"/>'
              f'<path d="M-26,-166 L-14,-164 L-14,-160 L-26,-162 Z" fill="{MANILA_DK}" stroke-width="1.2"/>'
              f'<path d="M-24,-148 L-6,-145" stroke="#B23A2E" stroke-width="1.6"/>'
              f'<path d="M-8,-163 L-2,-162 L-3,-170 L-9,-171 Z" fill="#FBF8F0" stroke-width="1.2"/></g>')
    s += arm((-24, -172), (-34, -132), (-6, -138), '#FBF8F0', SKIN_TIM, 'pinch', ang=-20, hold=folder)
    s += arm((24, -172), (42, -186), (48, -216), '#FBF8F0', SKIN_TIM, 'wave', ang=-100, flip=1, cls='wave')
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


# ======================================================================================== the scenes
LABELS = {
    'idle': ('The CTO\'s office. John, the Chief Engineer, types at the PC behind the partners\' desk; James, the CTO, paces '
             'by the window with a whisky. Two cigars smoulder in the ashtray, Chinese takeout waits on the desk, and the org '
             'chart on the wall has the two of them at the top.'),
    'tim': 'Tim walks in with a memo in a manila folder: "Memo from Patrick. It\'s for you two." James raises a hand; John looks up.',
    'reading': 'Reading the state: James types at the PC while John paces, reading the memo.',
    'flowchart': 'James draws the run on the run board, three lanes into the gate; John watches from the desk, eating.',
    'consulting': 'Both on their feet: John makes his one call, a finger up: "Smallest correct change. Then it ships." James listens.',
    'spec': 'John types out the prompts; the spec feeds off the printer and James paces, reading the first sheet.',
    'done': 'Done: the run is pinned to the board and stamped. James and John clink glasses: "Paste blocks are up. We move."',
    'failed': 'The run did not publish: John holds his forehead at the desk, James stands by: "That one didn\'t land. We go again."',
}

HEAD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <title>{title}</title>
'''

# Who holds his own glass, and who is in the chair, scene by scene.
SEATED = {'idle': 'john', 'tim': 'john', 'reading': 'james', 'flowchart': 'john', 'spec': 'john', 'failed': 'john'}


def seat_arms(stage, who):
    if stage in ('idle', 'spec', 'reading'):
        return typing(who)
    if stage == 'tim':
        return typing(who, cls=False)
    if stage == 'flowchart':
        Hp, Hc = (-15, -22), (16, -54)
        return [A('L', (-40, -8), Hp, 'wrap', ang=0, hold=pail(-6.5, -10, 0.9, open_=True)),
                A('R', (42, -8), Hc, 'fist', ang=-100, flip=1, hold='<path d="M14,-58 L4,-78 M18,-58 L10,-79" fill="none" stroke="#C49A62" stroke-width="2"/>')]
    if stage == 'failed':
        return [A('L', (-52, -44), (-12, -96), 'flat', ang=-30, flip=1), typing('john', cls=False)[1]]
    return []


def scene(stage):
    out = HEAD.format(vb='0 0 640 400', w=640, h=400, label=escape(LABELS[stage], quote=True), title="James and John's Coworking Space")
    out += f'  <!-- Scene "{stage}". Drawn by art/build.py; edit that, not this file. -->\n'
    out += wall() + window() + board(stage) + org_chart() + clock() + credenza()
    if stage == 'flowchart':
        H = (86, -214)
        marker = (f'<g transform="rotate(-35 {H[0]} {H[1]})"><rect x="{H[0] + 2}" y="{H[1] - 13}" width="5" height="14" rx="1.5" '
                  f'fill="#1F4E8C" stroke="{INK}" stroke-width="1.4"/></g>')
        out += standing('james', 98, 'right', 'smile', [hanging('james', 'L'), A('R', (58, -190), H, 'fist', ang=-60, flip=1, cls='scribble', hold=marker, watch=True)], s=0.82, y=286)
    sitter = SEATED.get(stage)
    if sitter:
        look = {'idle': 'left', 'tim': 'left', 'reading': 'left', 'flowchart': 'left', 'spec': 'left', 'failed': 'down'}[stage]
        expr = 'frown' if stage == 'failed' else 'smile'
        out += chair(empty=False) + seated(sitter, look, expr)
    else:
        out += chair(empty=True)
    out += desk_top() + terminal() + printer(stage) + keyboard()
    johns = stage not in ('done',)
    james_own = stage not in ('idle', 'tim', 'consulting', 'done')
    out += desk_items(stage, johns_glass=johns, james_glass=james_own)
    if sitter:
        out += seated_arms(sitter, seat_arms(stage, sitter))
    out += desk_front()
    if stage == 'spec':
        out += printout()
    if stage == 'failed':
        out += crumpled()
    if stage == 'tim':
        out += tim()

    # the men on their feet
    if stage == 'idle':
        out += walker('james', 592, 'glass')
    elif stage == 'tim':
        out += standing('james', 556, 'left', 'smile', [A('L', (-50, -176), (-58, -208), 'wave', ang=-100, flip=-1), james_glass_chest()])
    elif stage == 'reading':
        out += walker('john', 590, 'memo')
    elif stage == 'consulting':
        out += standing('john', 478, 'right', 'talk', [hanging('john', 'L'), A('R', (54, -60), (56, -96), 'point', ang=-92, flip=1, cls='nod')])
        Hg = (30, -120)
        out += standing('james', 584, 'left', 'listen', [A('L', (-36, -146), (-6, -191), 'fist', ang=-70, flip=1),
                                                         A('R', (40, -144), Hg, 'wrap', ang=180, flip=-1, hold=held_glass(Hg, 180), watch=True)])
    elif stage == 'spec':
        out += walker('james', 592, 'sheet')
    elif stage == 'done':
        Hj = (42, -100)
        out += standing('john', 458, 'right', 'smile', [hanging('john', 'L'), A('R', (52, -60), Hj, 'wrap', ang=0, flip=1, cls='toast', hold=held_glass(Hj, 0))])
        Hm = (-42, -232)
        out += standing('james', 598, 'left', 'talk', [A('L', (-54, -196), Hm, 'wrap', ang=180, flip=-1, cls='toast', hold=held_glass(Hm, 180)), hanging('james', 'R')])
    elif stage == 'failed':
        out += standing('james', 556, 'left', 'stern', [A('L', (-48, -146), (-26, -116), 'fist', ang=45, flip=1),
                                                        A('R', (48, -146), (26, -116), 'fist', ang=135, flip=-1, watch=True)])

    if stage == 'tim':
        out += bubble(24, 118, 176, ['MEMO FROM PATRICK.', "IT'S FOR YOU TWO."], (88, 180))
    elif stage == 'consulting':
        out += bubble(392, 92, 186, ['SMALLEST CORRECT CHANGE.', 'THEN IT SHIPS.'], (474, 140))
    elif stage == 'failed':
        out += bubble(214, 150, 176, ["THAT ONE DIDN'T LAND.", 'WE GO AGAIN.'], (318, 196))
    elif stage == 'done':
        out += bubble(452, 70, 172, ['PASTE BLOCKS ARE UP.', 'WE MOVE.'], (596, 134))
    return out + '</svg>\n'


# ======================================================================================== the door figure and the avatars
def door():
    """The two of them in the doorway, colleagues side by side: the CTO with his whisky, the Chief Engineer with the spec."""
    out = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-98 -258 204 170" width="204" height="170" role="img" aria-label="James, the CTO, and John, the Chief Engineer, side by side in shirtsleeves and ties">
  <title>James and John</title>
  <!-- Drawn by art/build.py; edit that, not this file. -->
'''
    roll = (f'<g stroke="{INK}" stroke-width="1.6"><path d="M-16,-36 L30,-14 L26,-4 L-20,-26 Z" fill="#FFFFFF"/>'
            '<path d="M-14,-31 L26,-12 M-16,-27 L24,-8" stroke="#BFE3BC" stroke-width="2.6"/></g>')
    # each man's inside hand is busy on his own side of the doorway: James straightens his tie, John holds the spec
    john = standing('john', 48, 'front', 'smile', [A('L', (-42, -10), (-12, -30), 'wrap', ang=20, hold=roll),
                                                   A('R', (44, -10), (18, -14), 'wrap', ang=200, flip=1)], y=0)
    Hg = (-25, -152)
    james = standing('james', -42, 'front', 'smile', [A('L', (-40, -144), Hg, 'wrap', ang=0, hold=held_glass(Hg, 0)),
                                                      A('R', (38, -150), (8, -178), 'pinch', ang=-160, flip=1)], y=0)
    strip = lambda s: s.split('\n', 1)[1]  # no floor shadows in the doorway
    out += strip(john) + strip(james)
    return out + '</svg>\n'


def office_door():
    """The CTO's office door, the space's logo (owner, 2026-10-09: "Use the CTO department door as the logo choice ...
    James and John side by side still gives too much like a couple"). The office's door for the space, drawn as one
    picture with the same parts and colours as fleet-office's skin-cowork: the walnut wall, a walnut door with a frosted
    pane lettered in gold leaf (their names, then CTO and CHIEF ENGINEER), a brass knob on its rose, the bar cart on one
    side and the coat rack with the suit jacket on the other. Nobody in it: the door is the department."""
    WAL, WAL_DK, WAL_DEEP = '#5E3D25', '#3F2717', '#2A1A0F'
    BR, BR_DK = '#C9A24A', '#B8893A'
    GL, GL_DK, WHISKY = '#D7E0DC', '#B9C6C1', '#A9651F'
    gilt = "'Bodoni Moda', 'Bodoni 72', Didot, 'Bodoni MT', Georgia, serif"
    s = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 210" width="300" height="210" role="img" aria-label="The CTO's office door: walnut, with James and John, CTO and Chief Engineer, lettered in gold on the frosted glass">
  <title>James and John's Coworking Space</title>
  <!-- Drawn by art/build.py; edit that, not this file. -->
  <defs>
    <clipPath id="od-wall"><rect width="300" height="210" rx="14"/></clipPath>
    <clipPath id="od-glass"><rect x="108" y="42" width="84" height="78"/></clipPath>
    <radialGradient id="od-light" cx="150" cy="0" r="150" gradientUnits="userSpaceOnUse" gradientTransform="translate(0 0) scale(1 0.62)">
      <stop offset="0" stop-color="#F2D49A" stop-opacity="0.34"/><stop offset="1" stop-color="#F2D49A" stop-opacity="0"/></radialGradient>
    <linearGradient id="od-leaf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7A4E2C"/><stop offset="1" stop-color="#5E3D25"/></linearGradient>
    <linearGradient id="od-pane" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D7E0DC"/><stop offset="1" stop-color="#B9C6C1"/></linearGradient>
    <radialGradient id="od-knob" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#FFF1C2"/><stop offset="0.45" stop-color="#C9A24A"/><stop offset="1" stop-color="#7A5A1E"/></radialGradient>
    <linearGradient id="od-ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9CED3"/><stop offset="1" stop-color="#8E949A"/></linearGradient>
  </defs>
  <g clip-path="url(#od-wall)">
'''
    # the walnut wall: a seam every 46px, grain on each board, the warm light from above, the skirting
    s += f'    <rect width="300" height="210" fill="{WAL}"/>\n'
    s += ''.join(f'    <path d="M{x},0 L{x},210" stroke="#000" stroke-opacity="0.22" stroke-width="2"/>'
                 f'<path d="M{x - 37},0 L{x - 37},210 M{x - 21},0 L{x - 21},210" stroke="#FFF" stroke-opacity="0.04" stroke-width="5"/>\n'
                 for x in range(46, 300, 46))
    s += '    <rect width="300" height="210" fill="url(#od-light)"/>\n'
    s += f'    <rect x="0" y="194" width="300" height="16" fill="{WAL_DK}"/><path d="M0,194.5 L300,194.5" stroke="#7A5232" stroke-width="1.4"/>\n'
    # the door in its frame
    s += f'    <rect x="84" y="18" width="132" height="176" fill="{WAL_DEEP}" stroke="#7A5232" stroke-width="2"/>\n'
    s += f'    <rect x="95" y="29" width="110" height="160" fill="url(#od-leaf)" stroke="#000" stroke-opacity="0.4"/>\n'
    s += f'    <rect x="104" y="38" width="92" height="86" fill="{WAL_DK}"/><rect x="108" y="42" width="84" height="78" fill="url(#od-pane)"/>\n'
    s += ('    <g clip-path="url(#od-glass)" fill="#FFF"><path d="M128,42 L138,42 L104,120 L94,120 Z" fill-opacity="0.32"/>'
          '<path d="M146,42 L151,42 L117,120 L112,120 Z" fill-opacity="0.18"/></g>\n')
    s += f'    <rect x="104" y="133" width="92" height="50" fill="{WAL_DK}"/><rect x="108" y="137" width="84" height="42" fill="#6E4527"/>\n'
    # the gilt on the glass, outlined in ink the way sign-writers outline gold leaf; the titles typed under it
    for y, word in ((66, 'JAMES'), (81, 'AND JOHN')):
        s += (f'    <text x="150" y="{y}" text-anchor="middle" font-family="{escape(gilt)}" font-size="13.5" font-weight="700" '
              f'letter-spacing="0.7" fill="#E2B54A" stroke="{WAL_DEEP}" stroke-width="0.8" paint-order="stroke">{word}</text>\n')
    for y, word in ((96, 'CTO'), (106, 'CHIEF ENGINEER')):
        s += (f'    <text x="150" y="{y}" text-anchor="middle" font-family="{escape(TYPE)}" font-size="7.5" font-weight="700" '
              f'letter-spacing="0.75" fill="{WAL_DEEP}">{word}</text>\n')
    s += f'    <circle cx="197" cy="128.5" r="7" fill="{BR_DK}"/><circle cx="197" cy="128.5" r="4.6" fill="url(#od-knob)"/>\n'
    # the bar cart: the decanter and two glasses on top, a bottle and the ice bucket below, brass rails, two wheels
    s += f'    <g stroke="{INK}" stroke-width="1.2" stroke-linejoin="round">\n'
    s += (f'      <rect x="20" y="130" width="3" height="58" fill="{BR_DK}" stroke="none"/><rect x="67" y="130" width="3" height="58" fill="{BR_DK}" stroke="none"/>\n'
          f'      <rect x="30.5" y="99" width="5" height="10" fill="{GL}"/><circle cx="33" cy="97" r="3" fill="#E4EEEC"/>\n'
          f'      <path d="M25,118 C25,110 29,107 33,107 C37,107 41,110 41,118 C41,126 37,130 33,130 C29,130 25,126 25,118 Z" fill="{GL}" fill-opacity="0.85"/>\n'
          f'      <path d="M25.6,120 L40.4,120 C40,126 37,130 33,130 C29,130 26,126 25.6,120 Z" fill="{WHISKY}" stroke="none"/>\n'
          f'      <path d="M25,118 C25,110 29,107 33,107 C37,107 41,110 41,118 C41,126 37,130 33,130 C29,130 25,126 25,118 Z" fill="none"/>\n')
    for gx in (47, 58):
        s += (f'      <path d="M{gx},118 L{gx + 8},118 L{gx + 7.5},130 L{gx + 0.5},130 Z" fill="{GL}" fill-opacity="0.85"/>'
              f'<rect x="{gx + 0.8}" y="123" width="6.4" height="6.6" fill="{WHISKY}" stroke="none"/>\n')
    s += (f'      <rect x="18" y="130" width="54" height="4" fill="{BR}"/>\n'
          f'      <rect x="30.5" y="150" width="4" height="9" fill="#2E6A49"/><rect x="28" y="158" width="9" height="20" rx="1.5" fill="#2E6A49"/>\n'
          f'      <rect x="44" y="164" width="16" height="14" rx="1" fill="url(#od-ice)"/>\n'
          f'      <rect x="18" y="178" width="54" height="4" fill="{BR}"/>\n'
          f'      <circle cx="21.5" cy="189" r="4" fill="{INK}"/><circle cx="68.5" cy="189" r="4" fill="{INK}"/>\n    </g>\n')
    # the coat rack and the suit jacket that came off when the sleeves went up
    s += (f'    <g stroke="{INK}" stroke-width="1.2" stroke-linejoin="round">\n'
          f'      <rect x="251" y="40" width="4" height="148" fill="{WAL_DEEP}"/><circle cx="253" cy="38" r="3.5" fill="{WAL_DEEP}"/>\n'
          f'      <path d="M240,193 L253,186 L266,193 Z" fill="{WAL_DEEP}"/>\n'
          '      <path d="M245,58 L235,63 L231,70 L230,110 L235,111 L236,80 L237,132 L269,132 L270,80 L271,111 L276,110 L275,70 L271,63 L261,58 L253,64 Z" fill="#2B3A63"/>\n'
          '      <path d="M245,58 L253,86 L261,58" fill="none" stroke="#3A4C7E" stroke-width="3"/>\n'
          '      <path d="M253,86 L253,132" stroke="#1E2A47" stroke-width="1.4"/>\n'
          f'      <circle cx="256.5" cy="98" r="1.4" fill="{BR}" stroke="none"/><circle cx="256.5" cy="110" r="1.4" fill="{BR}" stroke="none"/>\n    </g>\n')
    return s + '  </g>\n</svg>\n'


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
    write('art/office-door.svg', office_door())
    pair = (james_bust('translate(17 162) scale(0.62)')
            + john_bust('translate(48 77) scale(0.6)')
            + f'  <path d="M32,0 L32,64" stroke="{INK}" stroke-width="1.6"/>\n')
    write('mark.svg', avatar_svg("James and John's Coworking Space", pair, 'cw-mark'))
    write('art/james.svg', avatar_svg('James, CTO', james_bust('translate(32 202) scale(0.78)'), 'cw-james'))
    write('art/john.svg', avatar_svg('John, Chief Engineer', john_bust('translate(32 96) scale(0.74)'), 'cw-john'))
    print('drew', len(LABELS), 'scenes, the door figure, the office door, the mark and two avatars')
