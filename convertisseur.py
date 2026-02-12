from PIL import Image
import json


def image_matrice(image_path, target_size=16):
    """Convertit une image en matrice + redimensionnement"""
    img = Image.open(image_path)

    # Redimensionner l'image
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Convertir en RGBA pour gérer la transparence
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    width, height = img.size
    print(f"Taille de l'image : {width}x{height}")

    # Créer une matrice de pixels
    matrice = []
    for y in range(height):
        ligne = []
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            ligne.append((r, g, b, a))
        matrice.append(ligne)

    return matrice, width, height


def generer_html(matrice, width, height, nom_fichier="pixel_art.html"):
    """Génère un fichier HTML avec la matrice de pixels"""

    # Convertir les tuples en listes pour JSON
    matrice_json = json.dumps(matrice)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixel Art - {width}x{height}</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #1a1a1a;
            font-family: Arial, sans-serif;
        }}
        .container {{
            text-align: center;
        }}
        h1 {{
            color: #fff;
            margin-bottom: 20px;
        }}
        #canvas {{
            border: 2px solid #333;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Pixel Art {width}x{height}</h1>
        <canvas id="canvas" width="{width}" height="{height}"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Matrice de pixels
        const pixels = {matrice_json};
        
        // Dessiner chaque pixel
        for (let y = 0; y < {height}; y++) {{
            for (let x = 0; x < {width}; x++) {{
                const [r, g, b, a] = pixels[y][x];
                ctx.fillStyle = `rgba(${{r}}, ${{g}}, ${{b}}, ${{a / 255}})`;
                ctx.fillRect(x, y, 1, 1);
            }}
        }}
        
        // Agrandir le canvas pour mieux voir
        canvas.style.width = '{width * 20}px';
        canvas.style.height = '{height * 20}px';
    </script>
</body>
</html>"""

    # Sauvegarder le fichier
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Fichier généré : {nom_fichier}")


# Test
if __name__ == "__main__":
    chemin = input("Chemin de l'image :")
    taille = input("Taille demandée (16, 24, 32) [16 par défaut] :") or "16"

    matrice, w, h = image_matrice(chemin, int(taille))
    print(f"Matrice créée ! {w}x{h} pixels")
    print("Premiers pixels :", matrice[0][:3])

    # Générer le HTML
    generer_html(matrice, w, h)
