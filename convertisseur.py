from PIL import Image, ImageDraw
import json


def image_matrice(image_path, target_size=16):
    """Convertit une image en matrice + redimensionnement"""
    img = Image.open(image_path)

    # Redimensionner l'image
    img = img.resize((target_size, target_size), Image.Resampling.NEAREST)

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
            ligne.append([r, g, b, a])
        matrice.append(ligne)

    return matrice, width, height


def sauvegarder_matrice(matrice, width, height, nom_fichier="matrice"):
    """Sauvegarde la matrice en JSON et JS"""

    # JSON
    data = {"width": width, "height": height, "pixel": matrice}
    with open(f"{nom_fichier}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Fichier JSON : {nom_fichier}.json")

    # JavaScript
    with open(f"{nom_fichier}.js", "w") as f:
        f.write(f"const pixel = {json.dumps(matrice)};\n")
        f.write(f"const width = {width};\n")
        f.write(f"const height = {height};\n")
    print(f"Fichier JS : {nom_fichier}.js")


def generer_image(matrice, width, height, nom_fichier="pixel_art.png", scale=20):
    """Génère une image PNG avec la matrice de pixels"""

    # Créer une image agrandie
    img_sortie = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_sortie)

    # Dessiner chaque pixel
    for y in range(height):
        for x in range(width):
            r, g, b, a = matrice[y][x]

            x1 = x * scale
            y1 = y * scale
            x2 = x1 + scale
            y2 = y1 + scale

            draw.rectangle([x1, y1, x2, y2], fill=(r, g, b, a))

    img_sortie.save(nom_fichier)
    print(f"Image générée : {nom_fichier}")


# Test
if __name__ == "__main__":
    chemin = input("Chemin de l'image : ")
    taille = input("Taille demandée (16, 24, 32) [16 par défaut] : ") or "16"

    matrice, w, h = image_matrice(chemin, int(taille))
    print(f"Matrice créée ! {w}x{h} pixels")

    # Générer les fichiers
    sauvegarder_matrice(matrice, w, h)
    generer_image(matrice, w, h)
