"""art/build.py: draws every picture of James and John's Coworking Space from one set of parts, so the room, the people
and the ink are the same hand in every scene. Run it from the space's folder (python art/build.py); it writes:

  art.svg                the door figure and the dashboard's still (the idle scene)
  art/<scene>.svg        one scene per stage of a run, which the dashboard swaps in as the run moves:
                         idle, tim (a direction arrives: Tim walks in with it), reading, flowchart (RUN.md: James at the
                         board), consulting (John makes his one call), spec (the prompts: John drawing a spec sheet),
                         done, failed
  mark.svg               the pair, as two colleagues side by side (the office floor shows it as their avatar)
  art/james.svg, art/john.svg   one avatar each

Owner 2026-10-06: "like Cheech and Chong meets corporate world. so clean and collected, but cool and calming" and "Read
their agent bios when designing their office and avatars"; 23:07 CDT: "less blocky, more like the late 90s comic book
cartoon era"; later: "James and John's picture avatar make them look like a couple, not coworkers. Make them a bit more
platonic feeling, and bring their dashboard alive like the rest, like when Tim routes a message, have Tim walk in and talk
to James and John, and then have them doing various activities like writing flow charts, or drawing a spec sheet, and
have chinese takeout containers on the coffee table like they are working through dinner."

Style: inked outlines (#141414), flat cel shading (one hard shadow shape per form), an isometric lounge. Colour by fill
and stroke attributes only. Classes (walk, bubble, draw, scribble, nod) are hooks the dashboard's CSS animates; with no
CSS the scenes are complete stills. The vibe of three easy-going colleagues, never a likeness of anyone real.
"""
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(HERE)
INK = '#141414'

HEAD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <title>{title}</title>
'''

ROOM = '''  <rect width="640" height="400" fill="#CBD9D3"/>
  <polygon points="20,350 320,200 320,20 20,170" fill="#DCE5E0"/>
  <polygon points="320,200 620,350 620,170 320,20" fill="#C6D3CD"/>
  <polygon points="320,200 620,350 320,500 20,350" fill="#EDE6DA"/>
  <g stroke="#E0D6C6" stroke-width="2">
    <line x1="95" y1="312" x2="395" y2="462"/><line x1="170" y1="275" x2="470" y2="425"/><line x1="245" y1="237" x2="545" y2="387"/>
  </g>
  <polyline points="20,170 320,20 620,170" fill="none" stroke="#9FB2AA" stroke-width="2"/>
  <line x1="320" y1="20" x2="320" y2="200" stroke="#9FB2AA" stroke-width="2"/>
  <ellipse cx="232" cy="190" rx="66" ry="40" fill="#F3DCC8" fill-opacity="0.3"/>
'''

WINDOW = '''    <polygon points="430,145 590,225 590,95 430,15" fill="#F3DCC8"/>
    <polygon points="430,145 590,225 590,173 430,93" fill="#EFC3A0" stroke="none"/>
    <line x1="510" y1="55" x2="510" y2="185" stroke="#FFFFFF" stroke-width="5"/>
    <polygon points="430,145 590,225 590,95 430,15" fill="none"/>
'''

# The board sits on the left wall. Board-local coordinates (0..160 across, 0..80 down) map onto the wall by this matrix.
BOARD_M = 'matrix(1 -0.5 0 1 90 165)'
BOARD_FRAME = '    <polygon points="90,245 250,165 250,85 90,165" fill="#FAFBFA"/>\n'

def board(content):
    return BOARD_FRAME + f'    <g transform="{BOARD_M}" stroke-width="1.6">\n{content}    </g>\n'

PLAN = '''      <rect x="15" y="15" width="100" height="8" fill="#2E6B66" stroke="none"/>
      <rect x="15" y="35" width="70" height="8" fill="#7FB3AD" stroke="none"/>
      <rect x="15" y="55" width="125" height="8" fill="#D9895B" stroke="none"/>
'''

def flowchart(draw):
    c = ' class="draw d{}"' if draw else '{}'
    k = (lambda i: c.format(i)) if draw else (lambda i: '')
    return f'''      <rect{k(1)} x="10" y="9" width="34" height="15" rx="3" fill="none" stroke="#2E6B66"/>
      <path{k(2)} d="M44,16.5 L60,16.5 M56,13.5 L60,16.5 L56,19.5" fill="none" stroke="#2E6B66"/>
      <rect{k(3)} x="60" y="9" width="34" height="15" rx="3" fill="none" stroke="#2E6B66"/>
      <path{k(4)} d="M94,16.5 L110,16.5 M106,13.5 L110,16.5 L106,19.5" fill="none" stroke="#2E6B66"/>
      <rect{k(5)} x="110" y="9" width="38" height="15" rx="3" fill="none" stroke="#2E6B66"/>
      <path{k(6)} d="M77,24 L77,36 M74,32 L77,36 L80,32" fill="none" stroke="#2E6B66"/>
      <path{k(7)} d="M77,36 L93,48 L77,60 L61,48 Z" fill="none" stroke="#D9895B"/>
      <path{k(8)} d="M61,48 L28,48 L28,24 M25,28 L28,24 L31,28" fill="none" stroke="#D9895B"/>
      <path{k(9)} d="M93,48 L129,48 L129,24 M126,28 L129,24 L132,28" fill="none" stroke="#2E6B66"/>
      <path{k(10)} d="M18,13 L36,13 M18,17 L30,17 M68,13 L86,13 M68,17 L80,17 M118,13 L140,13 M118,17 L132,17" fill="none" stroke="#7FB3AD" stroke-width="1.2"/>
'''

PINNED = '''      <rect x="112" y="30" width="38" height="44" fill="#FFFFFF" stroke="#141414" stroke-width="1.2"/>
      <circle cx="131" cy="32" r="2.2" fill="#D9895B" stroke="#141414" stroke-width="0.8"/>
      <path d="M117,42 L120,45 L125,39 M117,52 L120,55 L125,49 M117,62 L120,65 L125,59" fill="none" stroke="#2E6B66" stroke-width="1.5"/>
      <path d="M129,42 L145,42 M129,52 L143,52 M129,62 L145,62" fill="none" stroke="#9FB2AA" stroke-width="1.4"/>
'''

PLANT = '''    <g>
      <path d="M296,150 C268,146 258,124 270,112 C288,114 302,130 296,150 Z" fill="#3D6B49"/>
      <path d="M336,146 C364,142 378,120 366,106 C346,108 330,126 336,146 Z" fill="#4F7F5A"/>
      <path d="M316,140 C300,112 306,80 320,66 C334,82 336,112 316,140 Z" fill="#6A9A72"/>
      <path d="M306,166 C282,170 268,158 272,146 C290,142 306,150 306,166 Z" fill="#4F7F5A"/>
      <path d="M330,164 C352,170 368,160 366,148 C348,142 332,150 330,164 Z" fill="#3D6B49"/>
      <path d="M296,150 C288,134 280,124 270,112 M336,146 C344,130 354,118 366,106 M316,140 C318,116 320,90 320,66" fill="none" stroke-width="1.2"/>
    </g>
'''

SOFA = '''    <polygon points="300,280 440,350 330,405 190,335" fill="#CFDCD5" stroke="none"/>
    <polygon points="330,156 510,246 490,256 310,166" fill="#4F8A84"/>
    <polygon points="310,166 490,256 490,306 310,216" fill="#2E6B66"/>
    <polygon points="490,256 510,246 510,296 490,306" fill="#1F4744"/>
    <polygon points="310,216 490,306 440,331 260,241" fill="#4F8A84"/>
    <polygon points="260,241 440,331 440,365 260,275" fill="#2E6B66"/>
    <polygon points="330,186 350,196 280,231 260,221" fill="#5C968F"/>
    <polygon points="260,221 280,231 280,285 260,275" fill="#2E6B66"/>
    <polygon points="280,231 350,196 350,250 280,285" fill="#1F4744"/>
    <polygon points="490,266 510,276 440,311 420,301" fill="#5C968F"/>
    <polygon points="420,301 440,311 440,365 420,355" fill="#2E6B66"/>
    <polygon points="440,311 510,276 510,330 440,365" fill="#1F4744"/>
    <polygon points="262,276 268,279 266,289 262,287" fill="#7A5A3C"/>
    <polygon points="436,364 442,367 440,377 436,375" fill="#7A5A3C"/>
'''

TABLE = '''    <polygon points="260,298 360,348 320,368 220,318" fill="#D9B98F"/>
    <polygon points="220,318 320,368 320,390 220,340" fill="#B8936A"/>
    <polygon points="320,368 360,348 360,370 320,390" fill="#9A774F"/>
'''

def pail(x, y, s=1.0, open_=False, sticks=False):
    """A takeout pail, its base centred at (x, y): white folded box, red mark, wire handle."""
    g = f'<g transform="translate({x} {y}) scale({s})">'
    g += '<path d="M-9,-17 L9,-17 L6,0 L-6,0 Z" fill="#FBFAF6"/>'
    g += '<path d="M3,-17 L9,-17 L6,0 L2,0 Z" fill="#E4E0D6" stroke="none"/>'
    g += '<path d="M-9,-17 L9,-17 L6,0 L-6,0 Z" fill="none"/>'
    if open_:
        g += '<path d="M-9,-17 L-12,-23 L-2,-20 Z M9,-17 L12,-23 L2,-20 Z" fill="#FBFAF6" stroke-width="1.4"/>'
        g += '<path d="M-8,-17 Q0,-21 8,-17" fill="#C9A26B" stroke-width="1.2"/>'
    else:
        g += '<path d="M-9,-17 L0,-24 L9,-17 Z" fill="#FBFAF6" stroke-width="1.4"/>'
        g += '<path d="M-7,-20 Q0,-31 7,-20" fill="none" stroke="#6E737B" stroke-width="1.2"/>'
    g += '<path d="M-3,-11 L0,-14 L3,-11 M-2,-11 L-2,-6 L2,-6 L2,-11" fill="none" stroke="#B23A2E" stroke-width="1.1"/>'
    if sticks:
        g += '<path d="M1,-18 L9,-36 M4,-18 L13,-34" fill="none" stroke="#B8936A" stroke-width="1.8"/>'
    return g + '</g>\n'

def takeout(stage):
    """On the coffee table: dinner. Closed boxes waiting while they start; open ones with chopsticks once they dig in."""
    eating = stage not in ('idle', 'tim')
    s = '    <g class="dinner">\n'
    s += '      ' + pail(306, 345, 0.95, open_=eating, sticks=eating)
    s += '      ' + pail(330, 356, 1.05, open_=eating and stage != 'flowchart')
    s += '      <path d="M282,340 L300,349 L296,351 L278,342 Z" fill="#F7F7F5" stroke-width="1.2"/>\n'
    s += '      <path d="M344,341 Q350,336 356,341 Q350,344 344,341 Z" fill="#E6C27A" stroke-width="1.2"/>\n'
    if stage == 'done':
        s += '      <path d="M268,330 L276,334 L274,336 L266,332 Z" fill="#E6C27A" stroke-width="1"/>\n'
    return s + '    </g>\n'

LAMP = '''  <g stroke="#141414" stroke-width="2" stroke-linejoin="round">
    <ellipse cx="232" cy="263" rx="10" ry="4" fill="#2B2F33"/>
    <rect x="230.5" y="184" width="3" height="79" fill="#2B2F33" stroke-width="1"/>
    <circle cx="232" cy="166" r="20" fill="#FBF3E8"/>
    <path d="M214,174 A20,20 0 0 0 250,174 C244,180 220,180 214,174 Z" fill="#F1E2CF" stroke="none"/>
    <path d="M213,166 C220,170 244,170 251,166" fill="none" stroke-width="1.2"/>
  </g>
'''

# ---------------------------------------------------------------- John, on the sofa (global coordinates)
JOHN_BODY = '''    <path d="M330,210 C328,228 330,246 334,260 L368,260 C372,246 376,228 376,210 C366,202 340,202 330,210 Z" fill="#3B4A4A"/>
    <path d="M361,205 C372,207 377,215 376,226 C375,240 371,252 368,260 L359,260 C363,243 365,222 361,205 Z" fill="#263131" stroke="none"/>
    <path d="M330,210 C328,228 330,246 334,260 L368,260 C372,246 376,228 376,210 C366,202 340,202 330,210 Z" fill="none"/>
    <path d="M344,205 L352,215 L360,205" fill="none" stroke-width="1.6"/>
    <path d="M347,197 L358,197 L359,207 L346,207 Z" fill="#9C6B4E"/>
'''

def john_head(look):
    """look: down (at his lap), up (at whoever is talking), left (toward James or Tim)."""
    s = '''    <path d="M338,180 C337,165 368,163 368,180 L367,190 C366,200 360,205 353,205 C346,205 339,200 338,190 Z" fill="#9C6B4E"/>
    <path d="M360,168 C367,171 368,178 368,184 L367,192 C365,199 362,202 358,204 C362,194 363,180 360,168 Z" fill="#7E5338" stroke="none"/>
    <path d="M338,186 C338,200 345,207 353,207 C361,207 368,200 368,186 C366,192 362,195 360,195 L346,195 C343,195 340,192 338,186 Z" fill="#231C18"/>
    <path d="M346,192 Q353,188.5 360,192 Q353,194.5 346,192 Z" fill="#231C18" stroke-width="1"/>
    <path d="M338,181 C336,164 368,160 368,180 C364,172 354,170 346,172 C342,174 340,177 338,181 Z" fill="#1A1614"/>
    <path d="M353,183 L351,189 L355,189.5" fill="none" stroke-width="1.2"/>
'''
    if look == 'down':
        s += '''    <path d="M343,177.5 L350,176.5 M356,176.5 L363,177.5" fill="none" stroke-width="2.4"/>
    <path d="M343.5,181.5 L350.5,181.5 M355.5,181.5 L362.5,181.5" fill="none" stroke-width="1.8"/>
    <circle cx="347.5" cy="183.6" r="1.5" fill="#141414" stroke="none"/><circle cx="359" cy="183.6" r="1.5" fill="#141414" stroke="none"/>
    <path d="M351,199.8 Q354,200.6 357,199.4" fill="none" stroke="#E9D9CB" stroke-width="1.3"/>
'''
    else:
        dx = -1.6 if look == 'left' else 0
        s += f'''    <path d="M343,176 L350,175.5 M356,175.5 L363,176" fill="none" stroke-width="2.4"/>
    <ellipse cx="{347 + dx}" cy="181" rx="1.6" ry="2" fill="#141414" stroke="none"/><ellipse cx="{359 + dx}" cy="181" rx="1.6" ry="2" fill="#141414" stroke="none"/>
    <path d="M349,199.5 Q353.5,202 358,199" fill="none" stroke="#E9D9CB" stroke-width="1.5"/>
'''
    return s

JOHN_LEGS_TOP = '''    <path d="M336,256 C326,262 312,266 302,270 L306,286 C318,282 330,280 344,276 L370,262 L368,256 Z" fill="#A5A992"/>
    <path d="M306,286 C318,282 330,280 344,276 L370,262 L370,268 L346,282 C332,286 318,288 308,292 Z" fill="#868A74"/>
'''
JOHN_LEGS_DOWN = '''    <path d="M302,270 C292,282 282,298 272,312 L282,318 C292,304 300,290 308,282 Z" fill="#A5A992"/>
    <path d="M308,282 C300,296 292,308 286,320 L296,324 C302,312 310,298 316,288 Z" fill="#868A74"/>
    <path d="M262,312 C257,316 261,323 270,321 L284,318 L280,310 Z" fill="#2A2A2E"/>
    <path d="M278,322 C273,326 277,333 286,331 L300,328 L296,320 Z" fill="#2A2A2E"/>
'''
JOHN_ARM_BACK = '''    <path d="M374,212 C386,206 398,204 410,206 L410,213 C398,212 386,214 376,220 Z" fill="#263131"/>
    <path d="M408,206 C414,204 420,204 426,205 L426,211 C420,211 414,212 408,213 Z" fill="#9C6B4E"/>
    <ellipse cx="430" cy="208" rx="5" ry="4" fill="#9C6B4E"/>
'''
JOHN_ARM_POINT = '''    <g class="nod">
    <path d="M372,214 C382,206 388,196 390,184 L397,186 C395,200 388,212 377,222 Z" fill="#263131"/>
    <path d="M390,186 C391,180 392,174 393,168 L399,170 C398,176 397,182 396,188 Z" fill="#9C6B4E"/>
    <path d="M393,169 C392,163 393,158 395,155 L398,156 C398,160 398,164 399,169 Z" fill="#9C6B4E"/>
    <ellipse cx="396" cy="170" rx="5" ry="4.5" fill="#9C6B4E"/>
    </g>
'''
TABLET = '''    <path d="M300,258 L330,268 L322,280 L292,270 Z" fill="#1E2A2A"/>
    <path d="M302,261 L326,269 L320,277.5 L296,269.5 Z" fill="#7FB3AD" stroke="none"/>
    <path d="M304,264 L313,267 M301,268 L315,272.5 M306,271.5 L318,275.5" fill="none" stroke-width="1.4" stroke="#2E6B66"/>
    <path d="M302,267.2 L309,269.5" fill="none" stroke-width="1.4" stroke="#D9895B"/>
'''
SPEC_SHEET = '''    <path d="M296,254 L332,266 L322,284 L286,272 Z" fill="#7A5A3C"/>
    <path d="M299,256 L329,266.5 L321,281 L291,270.5 Z" fill="#FFFFFF" stroke-width="1.2"/>
    <path d="M302,259 L326,267 M299,263 L323,271 M296,267 L320,275 M305,258 L297,272 M313,261 L305,275 M321,264 L313,278" fill="none" stroke="#C6D3CD" stroke-width="0.8"/>
    <path class="draw d1" d="M300,263 L309,266 L306,271 L297,268 Z" fill="none" stroke="#2E6B66" stroke-width="1.3"/>
    <path class="draw d3" d="M312,268 L320,270.5" fill="none" stroke="#D9895B" stroke-width="1.3"/>
'''
JOHN_HAND_LAP = '''    <path d="M330,212 C324,226 322,240 326,250 L334,248 C333,238 334,226 338,214 Z" fill="#3B4A4A"/>
    <path d="M324,248 C320,254 316,258 311,262 L317,268 C322,264 328,258 334,250 Z" fill="#9C6B4E"/>
    <ellipse cx="312" cy="266" rx="5.5" ry="4" fill="#9C6B4E"/>
'''
JOHN_PENCIL = '''    <g class="scribble">
    <path d="M330,212 C324,226 322,240 326,250 L334,248 C333,238 334,226 338,214 Z" fill="#3B4A4A"/>
    <path d="M324,248 C320,254 316,260 312,264 L318,270 C322,265 328,258 334,250 Z" fill="#9C6B4E"/>
    <ellipse cx="313" cy="268" rx="5.5" ry="4" fill="#9C6B4E"/>
    <path d="M306,272 L318,258 L321,260 L309,274 Z" fill="#E6C27A" stroke-width="1.2"/>
    <path d="M306,272 L309,274 L305,276 Z" fill="#141414" stroke-width="0.8"/>
    </g>
'''
JOHN_CHOPSTICKS = '''    <path d="M330,212 C324,226 322,240 326,250 L334,248 C333,238 334,226 338,214 Z" fill="#3B4A4A"/>
    <path d="M326,248 C326,240 330,232 334,226 L340,230 C336,236 333,242 332,250 Z" fill="#9C6B4E"/>
    <ellipse cx="337" cy="226" rx="5" ry="4" fill="#9C6B4E"/>
    <path d="M336,224 L348,200 M339,226 L352,203" fill="none" stroke="#B8936A" stroke-width="1.8"/>
    <path d="M300,268 L316,273 L313,279 L297,274 Z" fill="#FBFAF6" stroke-width="1.4"/>
    <path d="M300,268 Q308,264 316,273" fill="#C9A26B" stroke-width="1.2"/>
'''

def john(stage):
    look = {'idle': 'down', 'reading': 'down', 'spec': 'down', 'tim': 'left', 'flowchart': 'left',
            'consulting': 'left', 'done': 'left', 'failed': 'down'}[stage]
    s = '  <g class="john" stroke="#141414" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">\n'
    s += JOHN_ARM_POINT if stage in ('consulting', 'done') else JOHN_ARM_BACK
    s += JOHN_BODY + john_head(look) + JOHN_LEGS_TOP
    if stage == 'spec':
        s += SPEC_SHEET + JOHN_PENCIL
    elif stage == 'flowchart':
        s += JOHN_CHOPSTICKS
    else:
        s += TABLET + JOHN_HAND_LAP
    return s + '  </g>\n'

# ---------------------------------------------------------------- James, standing (local coordinates: feet at 0,0)
JAMES_BODY = '''    <path d="M-16,-95 C-18,-60 -15,-30 -14,-6 L-3,-6 C-2,-35 -1,-65 0,-92 Z" fill="#C9CED3"/>
    <path d="M0,-92 C2,-65 4,-35 6,-6 L17,-6 C16,-35 16,-65 14,-95 Z" fill="#A9B1B9"/>
    <path d="M-17,-7 C-22,-6 -27,-1 -22,1 L-2,1 L-2,-7 Z" fill="#2A2A2E"/>
    <path d="M5,-7 L5,1 L24,1 C28,-1 24,-6 18,-7 Z" fill="#2A2A2E"/>
    <path d="M-24,-158 C-30,-140 -26,-110 -20,-86 L20,-86 C24,-110 26,-140 22,-158 C12,-164 -14,-164 -24,-158 Z" fill="#D5D9DD"/>
    <path d="M10,-162 C21,-158 26,-140 22,-120 C21,-108 21,-96 20,-86 L9,-86 C12,-110 13,-140 10,-162 Z" fill="#A9B1B9" stroke="none"/>
    <path d="M-24,-158 C-30,-140 -26,-110 -20,-86 L20,-86 C24,-110 26,-140 22,-158 C12,-164 -14,-164 -24,-158 Z" fill="none"/>
    <path d="M-7,-161 L0,-136 L7,-161 Z" fill="#F7F7F5"/>
    <path d="M-7,-161 L-2,-118 M7,-161 L2,-118" fill="none" stroke-width="1.6"/>
    <circle cx="0" cy="-110" r="1.6" fill="#141414" stroke="none"/>
'''
JAMES_ARM_OPEN = '''    <g transform="rotate({a} -22 -148)"><g{cls}>
    <path d="M-22,-156 C-34,-153 -46,-146 -58,-150 L-60,-141 C-48,-137 -36,-141 -22,-140 Z" fill="#D5D9DD"/>
    <path d="M-60,-153 C-68,-158 -74,-156 -72,-150 C-74,-146 -68,-140 -60,-141 Z" fill="#D6A07C"/>
    {extra}
    </g></g>
'''
MARKER = '<path d="M-72,-152 L-82,-157 L-80,-161 L-70,-156 Z" fill="#2E6B66" stroke-width="1.4"/>'
SHEET_PIN = '<path d="M-86,-170 L-66,-170 L-66,-146 L-86,-146 Z" fill="#FFFFFF" stroke-width="1.4"/>'
JAMES_ARM_MUG = '''    <path d="M18,-158 C26,-150 29,-136 27,-123 C21,-121 13,-123 6,-125 L6,-132 C12,-131 17,-131 20,-133 C20,-142 18,-150 13,-156 Z" fill="#A9B1B9"/>
    <path d="M-2,-146 L10,-146 L10,-130 C10,-127 -2,-127 -2,-130 Z" fill="#D9895B"/>
    <path d="M10,-142 C15,-142 15,-134 10,-134" fill="none" stroke-width="1.8"/>
    <ellipse cx="4" cy="-146" rx="6" ry="2" fill="#E8A77E" stroke-width="1.4"/>
    <path d="M2,-134 C6,-136 10,-133 8,-129 C6,-127 2,-128 2,-131 Z" fill="#D6A07C" stroke-width="1.6"/>
'''
JAMES_ARM_TAKEOUT = '''    <path d="M18,-158 C26,-150 29,-136 27,-123 C21,-121 13,-123 6,-125 L6,-132 C12,-131 17,-131 20,-133 C20,-142 18,-150 13,-156 Z" fill="#A9B1B9"/>
    ''' + pail(4, -126, 0.9, open_=True, sticks=True).strip() + '''
    <path d="M2,-134 C6,-136 10,-133 8,-129 C6,-127 2,-128 2,-131 Z" fill="#D6A07C" stroke-width="1.6"/>
'''

def james_head(look):
    s = '''    <path d="M-5,-171 L5,-171 L6,-158 L-6,-158 Z" fill="#D6A07C"/>
    <path d="M-12,-196 C-13,-211 12,-213 13,-196 L12,-181 C10,-173 4,-169 0,-169 C-5,-169 -11,-174 -12,-181 Z" fill="#D6A07C"/>
    <path d="M5,-201 C12,-199 13,-191 12,-181 C10,-174 6,-171 3,-170 C7,-179 8,-191 5,-201 Z" fill="#B57F5C" stroke="none"/>
    <path d="M-12,-196 C-13,-211 12,-213 13,-196 L12,-181 C10,-173 4,-169 0,-169 C-5,-169 -11,-174 -12,-181 Z" fill="none"/>
    <path d="M-13,-194 C-16,-214 6,-221 14,-206 C15,-201 14,-197 13,-193 C10,-202 2,-206 -5,-204 C-9,-201 -11,-198 -13,-194 Z" fill="#2E2724"/>
    <path d="M-10,-197 Q-5.5,-199.5 -1,-197 M2,-197 Q6.5,-199.5 11,-197" fill="none" stroke-width="1.8"/>
'''
    dx = {'left': -1.4, 'right': 1.4, 'front': 0}[look]
    s += f'''    <circle cx="{-5 + dx}" cy="-190" r="1.4" fill="#141414" stroke="none"/>
    <circle cx="{6 + dx}" cy="-190" r="1.4" fill="#141414" stroke="none"/>
    <circle cx="-5" cy="-190" r="4.6" fill="#FFFFFF" fill-opacity="0.2" stroke-width="1.5"/>
    <circle cx="6" cy="-190" r="4.6" fill="#FFFFFF" fill-opacity="0.2" stroke-width="1.5"/>
    <path d="M-0.4,-190.5 L1.4,-190.5" fill="none" stroke-width="1.5"/>
    <path d="M1,-187 L-1,-182 L2,-181.5" fill="none" stroke-width="1.3"/>
    <path d="M-4,-177 Q1,-173 6,-177" fill="none" stroke-width="1.7"/>
'''
    return s

def james(stage, x=168, y=338):
    look = {'tim': 'left', 'consulting': 'right', 'spec': 'right', 'done': 'right', 'failed': 'right'}.get(stage, 'front')
    s = f'  <ellipse cx="{x}" cy="{y}" rx="28" ry="8" fill="#D5CBBB"/>\n'
    s += f'  <g class="james" transform="translate({x} {y}) scale(0.86)" stroke="#141414" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">\n'
    s += JAMES_BODY
    if stage == 'flowchart':
        s += JAMES_ARM_OPEN.format(a=34, cls=' class="scribble"', extra=MARKER)
    elif stage == 'done':
        s += JAMES_ARM_OPEN.format(a=40, cls='', extra=SHEET_PIN)
    elif stage == 'tim':
        s += JAMES_ARM_OPEN.format(a=-6, cls=' class="wave"', extra='')
    else:
        s += JAMES_ARM_OPEN.format(a=0, cls='', extra='')
    s += JAMES_ARM_TAKEOUT if stage in ('reading', 'spec', 'consulting') else JAMES_ARM_MUG
    s += james_head(look)
    return s + '  </g>\n'

# ---------------------------------------------------------------- Tim, walking in with the direction (feet at 0,0)
def tim():
    return '''  <g class="tim">
  <ellipse cx="66" cy="368" rx="22" ry="7" fill="#D5CBBB"/>
  <g transform="translate(66 368) scale(0.8)" stroke="#141414" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">
    <path d="M-15,-90 C-17,-58 -16,-30 -16,-6 L-5,-6 C-4,-34 -2,-60 0,-88 Z" fill="#4E5A73"/>
    <path d="M0,-88 C3,-62 8,-34 12,-6 L23,-7 C19,-34 15,-62 13,-90 Z" fill="#3B455A"/>
    <path d="M-19,-7 C-24,-6 -28,-1 -23,1 L-4,1 L-4,-7 Z" fill="#6B4A32"/>
    <path d="M10,-7 L10,1 L29,1 C33,-1 29,-6 23,-7 Z" fill="#6B4A32"/>
    <path d="M-23,-150 C-30,-130 -27,-104 -22,-82 L22,-82 C27,-104 30,-130 23,-150 C12,-157 -12,-157 -23,-150 Z" fill="#E7D8B9"/>
    <path d="M9,-155 C22,-150 28,-128 24,-104 C23,-96 22,-89 22,-82 L10,-82 C13,-106 14,-134 9,-155 Z" fill="#CDBB96" stroke="none"/>
    <path d="M-23,-150 C-30,-130 -27,-104 -22,-82 L22,-82 C27,-104 30,-130 23,-150 C12,-157 -12,-157 -23,-150 Z" fill="none"/>
    <path d="M-8,-154 L0,-128 L8,-154 Z" fill="#9CC1E0"/>
    <path d="M-8,-154 L-3,-100 M8,-154 L3,-100" fill="none" stroke-width="1.6"/>
    <path d="M-3,-128 L-6,-112 L-1,-112 Z" fill="#2E6B66" stroke-width="1.2"/>
    <rect x="-17" y="-122" width="9" height="12" rx="1.5" fill="#FFFFFF" stroke-width="1.2"/>
    <path d="M-13,-122 L-9,-140" fill="none" stroke="#2E6B66" stroke-width="1.2"/>
    <path d="M20,-148 C30,-140 34,-124 30,-110 C24,-108 18,-110 12,-112 L12,-120 C18,-119 22,-119 24,-121 C24,-132 22,-140 16,-146 Z" fill="#CDBB96"/>
    <path d="M2,-132 L22,-124 L16,-108 L-4,-116 Z" fill="#1E2A2A"/>
    <path d="M4,-129 L20,-122.5 L15,-111 L-1,-117.5 Z" fill="#F3DCC8" stroke="none"/>
    <path d="M10,-118 C14,-121 18,-118 16,-114 C14,-111 10,-112 10,-115 Z" fill="#E2B48F" stroke-width="1.6"/>
    <path d="M-22,-148 C-32,-140 -38,-126 -36,-112 L-28,-110 C-29,-122 -26,-134 -18,-142 Z" fill="#E7D8B9"/>
    <path d="M-36,-112 C-38,-106 -36,-102 -32,-102 C-28,-102 -27,-106 -28,-110 Z" fill="#E2B48F" stroke-width="1.6"/>
    <path d="M-5,-163 L5,-163 L6,-150 L-6,-150 Z" fill="#E2B48F"/>
    <path d="M-13,-186 C-14,-201 13,-203 14,-186 L13,-174 C11,-166 5,-162 0,-162 C-6,-162 -12,-167 -13,-174 Z" fill="#E2B48F"/>
    <path d="M6,-191 C13,-188 14,-181 13,-174 C11,-168 7,-164 3,-163 C8,-171 9,-182 6,-191 Z" fill="#C99572" stroke="none"/>
    <path d="M-13,-186 C-14,-201 13,-203 14,-186 L13,-174 C11,-166 5,-162 0,-162 C-6,-162 -12,-167 -13,-174 Z" fill="none"/>
    <path d="M-15,-184 C-20,-192 -16,-204 -8,-206 C-6,-212 6,-213 9,-207 C17,-207 20,-196 16,-186 C14,-193 10,-197 4,-197 C-2,-197 -10,-194 -15,-184 Z" fill="#6B3E26"/>
    <path d="M-9,-188 Q-5,-191 -1,-188 M3,-188 Q7,-191 11,-188" fill="none" stroke-width="1.7"/>
    <ellipse cx="-5" cy="-183" rx="1.5" ry="1.9" fill="#141414" stroke="none"/>
    <ellipse cx="7" cy="-183" rx="1.5" ry="1.9" fill="#141414" stroke="none"/>
    <path d="M1,-181 L-1,-176 L2,-175.5" fill="none" stroke-width="1.3"/>
    <path d="M-6,-171 Q1,-164 8,-171 Q1,-168 -6,-171 Z" fill="#FFFFFF" stroke-width="1.5"/>
  </g>
  </g>
'''

def bubble(x, y, w, lines, tail_x, cls='bubble'):
    h = 10 + 13 * len(lines)
    t = ''.join(f'<text x="{x + w / 2}" y="{y + 16 + 13 * i}" text-anchor="middle" font-family="Segoe UI, system-ui, sans-serif" font-size="11" font-weight="600" fill="#1E2A2A" stroke="none">{escape(l)}</text>' for i, l in enumerate(lines))
    return (f'  <g class="{cls}" stroke="#141414" stroke-width="2" stroke-linejoin="round">\n'
            f'    <path d="M{x + 8},{y} L{x + w - 8},{y} Q{x + w},{y} {x + w},{y + 8} L{x + w},{y + h - 8} Q{x + w},{y + h} {x + w - 8},{y + h} '
            f'L{tail_x + 8},{y + h} L{tail_x},{y + h + 10} L{tail_x - 2},{y + h} L{x + 8},{y + h} Q{x},{y + h} {x},{y + h - 8} L{x},{y + 8} Q{x},{y} {x + 8},{y} Z" fill="#FFFFFF"/>\n'
            f'    {t}\n  </g>\n')

def scene(stage):
    out = HEAD.format(vb='0 0 640 400', w=640, h=400, label=escape(LABELS[stage], quote=True), title="James and John's Coworking Space")
    out += f'  <!-- Scene "{stage}". Drawn by art/build.py; edit that, not this file. -->\n'
    out += ROOM
    out += '  <g stroke="#141414" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">\n'
    out += WINDOW
    if stage in ('idle', 'tim', 'reading'):
        out += board(PLAN)
    elif stage == 'flowchart':
        out += board(flowchart(True))
    elif stage == 'done':
        out += board(flowchart(False) + PINNED)
    else:
        out += board(flowchart(False))
    out += PLANT + SOFA + '  </g>\n'
    out += john(stage)  # his thighs on the sofa; his shins go over the table, below
    out += '  <g stroke="#141414" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">\n' + TABLE + takeout(stage)
    out += '  </g>\n'
    out += '  <g stroke="#141414" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">\n' + JOHN_LEGS_DOWN + '  </g>\n'
    out += LAMP
    out += james(stage)
    if stage == 'tim':
        out += tim()
        out += bubble(8, 146, 128, ['Hey James! Hey John!', 'New one from Patrick.'], 66)
    if stage == 'consulting':
        out += bubble(396, 112, 132, ['Smallest correct change.', 'Then it ships.'], 404)
    if stage == 'failed':
        out += bubble(396, 120, 120, ["That one didn't land.", "We'll try again."], 404)
    if stage == 'done':
        out += bubble(28, 168, 108, ['Paste blocks are up.', 'We move.'], 140)
    return out + '</svg>\n'

LABELS = {
    'idle': 'James stands easy by the run board with a coffee; John is on the sofa reading a diff. Dinner waits on the coffee table in takeout boxes.',
    'tim': 'Tim walks in with a new direction on his tablet: "Hey James! Hey John! New one from Patrick." They both look up.',
    'reading': 'Reading the state: John reads on his tablet while James eats takeout by the board.',
    'flowchart': 'James draws the run as a flowchart on the board while John watches and eats.',
    'consulting': 'John makes his one call: "Smallest correct change. Then it ships." James listens, takeout in hand.',
    'spec': 'John draws a spec sheet on a clipboard on his knee while James eats and watches.',
    'done': 'Done: James pins the paste blocks to the board ("Paste blocks are up. We move.") and John points to it.',
    'failed': 'The run did not publish: John says "That one didn\'t land. We\'ll try again." while James looks over.',
}

# ---------------------------------------------------------------- avatars: two colleagues, side by side, never overlapping
def avatar_svg(label, body, clip):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="{label}">
  <title>{label}</title>
  <!-- Drawn by art/build.py from the scenes' own shapes. Two colleagues side by side, each in their own half. -->
  <defs><clipPath id="{clip}"><rect width="64" height="64" rx="14"/></clipPath></defs>
  <rect width="64" height="64" rx="14" fill="#CBD9D3"/>
  <g clip-path="url(#{clip})">
{body}  </g>
  <rect x="0.75" y="0.75" width="62.5" height="62.5" rx="13.25" fill="none" stroke="#141414" stroke-width="1.5"/>
</svg>
'''

def james_bust(t):
    return (f'  <g transform="{t}" stroke="#141414" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">\n'
            '    <path d="M-30,-162 C-34,-140 -32,-120 -30,-100 L26,-100 C28,-120 30,-140 26,-162 C14,-168 -18,-168 -30,-162 Z" fill="#D5D9DD"/>\n'
            '    <path d="M10,-166 C24,-162 30,-140 26,-100 L10,-100 C13,-126 14,-146 10,-166 Z" fill="#A9B1B9" stroke="none"/>\n'
            '    <path d="M-30,-162 C-34,-140 -32,-120 -30,-100 L26,-100 C28,-120 30,-140 26,-162 C14,-168 -18,-168 -30,-162 Z" fill="none"/>\n'
            '    <path d="M-7,-164 L0,-138 L7,-164 Z" fill="#F7F7F5"/>\n'
            + james_head('front') + '  </g>\n')

def john_bust(t):
    return (f'  <g transform="{t}" stroke="#141414" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">\n'
            '    <path d="M326,212 C322,232 324,250 326,262 L380,262 C382,250 384,232 380,212 C368,202 338,202 326,212 Z" fill="#3B4A4A"/>\n'
            '    <path d="M361,205 C376,208 382,216 380,232 C379,246 380,254 380,262 L362,262 C365,243 366,222 361,205 Z" fill="#263131" stroke="none"/>\n'
            '    <path d="M326,212 C322,232 324,250 326,262 L380,262 C382,250 384,232 380,212 C368,202 338,202 326,212 Z" fill="none"/>\n'
            '    <path d="M344,205 L352,215 L360,205" fill="none" stroke-width="1.6"/>\n'
            '    <path d="M347,197 L358,197 L359,207 L346,207 Z" fill="#9C6B4E"/>\n'
            + john_head('up') + '  </g>\n')

def write(rel, text):
    path = os.path.join(HOME, *rel.split('/'))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

if __name__ == '__main__':
    for st in LABELS:
        write(f'art/{st}.svg', scene(st))
    write('art.svg', scene('idle'))
    pair = (james_bust('translate(16 121) scale(0.5)')
            + john_bust('translate(-157 -81) scale(0.58)')
            + '  <path d="M32,6 L32,64" stroke="#141414" stroke-width="1.5"/>\n')
    write('mark.svg', avatar_svg("James and John's Coworking Space", pair, 'cw-mark'))
    write('art/james.svg', avatar_svg('James, CTO', james_bust('translate(32 145) scale(0.62)'), 'cw-james'))
    write('art/john.svg', avatar_svg('John, Chief Engineer', john_bust('translate(-207 -101) scale(0.68)'), 'cw-john'))
    print('drew', len(LABELS), 'scenes, the mark and two avatars')
