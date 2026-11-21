"""Gorro de Papá Noel en SVG. Origen: centro del borde inferior del ribete. Ancho base 100 (se escala).
La punta cae hacia atrás (x negativa)."""
def gorro(x, y, ancho, giro=0, espejo=False, tinta="#16181d", trazo=3.0, rojo="#d62f2f", sombra="#a81f24", piel="#ffffff"):
    s = ancho / 100
    t = trazo / s
    cuerpo = ("M42 -14 C46 -40 42 -74 16 -90 C-8 -104 -40 -94 -54 -64 "
              "C-44 -72 -30 -76 -18 -70 C-32 -56 -42 -36 -44 -14 Z")
    pliegue = "M22 -80 C32 -60 34 -40 30 -16"
    return (f'<g transform="translate({x} {y}) rotate({giro}) scale({-s if espejo else s} {s})" stroke="{tinta}" stroke-width="{t:.2f}" '
            f'stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="{cuerpo}" fill="{rojo}"/>'
            f'<path d="{pliegue}" fill="none" stroke="{sombra}" stroke-width="{t*1.6:.2f}" opacity=".55"/>'
            f'<rect x="-52" y="-20" width="104" height="22" rx="11" fill="{piel}"/>'
            f'<circle cx="-55" cy="-62" r="13" fill="{piel}"/>'
            f'</g>')
