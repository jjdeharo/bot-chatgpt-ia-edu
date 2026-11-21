def gorro3d(x, y, ancho, giro=0, espejo=False):
    """Gorro con volumen para pegar sobre un dibujo en 3D: degradados, brillo, sombra propia y sombra arrojada,
    sin contorno negro."""
    s = ancho / 100
    sx = -s if espejo else s
    cuerpo = ("M42 -14 C46 -40 42 -74 16 -90 C-8 -104 -40 -94 -54 -64 "
              "C-44 -72 -30 -76 -18 -70 C-32 -56 -42 -36 -44 -14 Z")
    return f'''<defs>
<linearGradient id="rojo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8e1218"/><stop offset=".35" stop-color="#d1262c"/><stop offset=".6" stop-color="#e43a3a"/><stop offset="1" stop-color="#7a0f14"/></linearGradient>
<linearGradient id="rojo-v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></linearGradient>
<linearGradient id="piel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#eef1f4"/><stop offset="1" stop-color="#b9c0c8"/></linearGradient>
<radialGradient id="bola" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#e9edf1"/><stop offset="1" stop-color="#aab2bb"/></radialGradient>
<filter id="sombra" x="-30%" y="-30%" width="160%" height="180%"><feGaussianBlur in="SourceAlpha" stdDeviation="9"/><feOffset dy="14"/><feComponentTransfer><feFuncA type="linear" slope=".55"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="pelo"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" result="r"/><feColorMatrix in="r" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.2 .75" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>
</defs>
<g transform="translate({x} {y}) rotate({giro}) scale({sx} {s})" filter="url(#sombra)">
<path d="{cuerpo}" fill="url(#rojo)"/>
<path d="{cuerpo}" fill="url(#rojo-v)"/>
<path d="M-6 -84 C-20 -70 -28 -46 -30 -20" fill="none" stroke="#ff8a80" stroke-width="5" stroke-linecap="round" opacity=".45"/>
<path d="M22 -80 C32 -60 34 -40 30 -16" fill="none" stroke="#6d0b10" stroke-width="4" opacity=".5"/>
<rect x="-52" y="-20" width="104" height="24" rx="12" fill="url(#piel)"/>
<rect x="-52" y="-20" width="104" height="24" rx="12" fill="#fff" filter="url(#pelo)" opacity=".5"/>
<circle cx="-55" cy="-62" r="14" fill="url(#bola)"/>
</g>'''
