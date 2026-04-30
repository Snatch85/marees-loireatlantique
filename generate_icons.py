"""
Génère toutes les icônes PWA pour l'application Marées Loire-Atlantique.
Utilise uniquement la bibliothèque standard (pas de PIL requis).
Crée des fichiers PNG valides avec une vague stylisée.
"""
import struct, zlib, math, os

def make_png(width, height, pixels_rgba):
    """Crée un PNG valide depuis une liste de pixels RGBA."""
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(name + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            r, g, b = pixels_rgba[y * width + x]
            raw += bytes([r, g, b])

    sig = b'\x89PNG\r\n\x1a\n'
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    return sig + chunk(b'IHDR', ihdr) + idat + chunk(b'IEND', b'')

def draw_icon(size):
    """Dessine une icône vague sur fond dégradé bleu marine."""
    pixels = []
    cx, cy = size / 2, size / 2
    r_outer = size * 0.5
    r_inner = size * 0.42

    for y in range(size):
        row = []
        for x in range(size):
            # Fond : dégradé bleu marine → bleu mer
            bg_r = int(15  + (26  - 15)  * (y / size))
            bg_g = int(79  + (107 - 79)  * (y / size))
            bg_b = int(107 + (138 - 107) * (y / size))

            # Cercle avec coin arrondi
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            corner_r = size * 0.22

            # Anti-aliasing bord du cercle
            aa = max(0.0, min(1.0, (r_outer - dist)))
            if aa <= 0:
                row.append((240, 247, 251))  # fond page
                continue

            # Vague : cos sur largeur, décalée sur hauteur
            wave_y = cy + size * 0.08 * math.cos(x / size * math.pi * 3)
            wave_h = size * 0.18

            if y > wave_y + wave_h:
                # Zone eau (en dessous de la vague)
                r, g, b = 42, 157, 143   # --sea
            elif y > wave_y:
                # Zone crête de vague
                t = (y - wave_y) / wave_h
                r = int(26  + (42  - 26)  * t)
                g = int(107 + (157 - 107) * t)
                b = int(138 + (143 - 138) * t)
            else:
                # Zone ciel (au dessus)
                r, g, b = bg_r, bg_g, bg_b

            # Bord de cercle AA
            blend = min(1.0, aa)
            r = int(r * blend + 240 * (1 - blend))
            g = int(g * blend + 247 * (1 - blend))
            b = int(b * blend + 251 * (1 - blend))

            row.append((r, g, b))
        pixels.extend(row)
    return make_png(size, size, pixels)

# Créer le dossier icons
os.makedirs('icons', exist_ok=True)

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for s in sizes:
    data = draw_icon(s)
    path = f'icons/icon-{s}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'  OK {path} ({len(data)} bytes)')

# favicon 32px et 16px
for s in [32, 16]:
    data = draw_icon(s)
    path = f'icons/favicon-{s}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'  OK {path}')

print('\nToutes les icones generees dans ./icons/')
