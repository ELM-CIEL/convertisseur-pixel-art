from PIL import Image
import json


def quantifier_couleurs_kmeans(img, nb_couleurs=5, max_iterations=20):
    """Quantifie les couleurs avec K-means (algorithme professionnel)"""
    import random

    # Récupérer tous les pixels non transparents
    pixels = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a >= 128:  # Ignorer transparents
                pixels.append([r, g, b])

    if len(pixels) == 0:
        return [(0, 0, 0)] * nb_couleurs

    # Initialiser les centres (moyennes) aléatoirement
    centres = random.sample(pixels, min(nb_couleurs, len(pixels)))

    # K-means : itérations pour trouver les meilleures couleurs
    for _ in range(max_iterations):
        # Assigner chaque pixel au centre le plus proche
        clusters = [[] for _ in range(len(centres))]

        for pixel in pixels:
            distances = [
                sum((pixel[i] - centre[i]) ** 2 for i in range(3)) for centre in centres
            ]
            cluster_id = distances.index(min(distances))
            clusters[cluster_id].append(pixel)

        # Recalculer les centres
        nouveaux_centres = []
        for cluster in clusters:
            if len(cluster) > 0:
                moy = [sum(p[i] for p in cluster) // len(cluster) for i in range(3)]
                nouveaux_centres.append(moy)
            else:
                nouveaux_centres.append(centres[len(nouveaux_centres)])

        centres = nouveaux_centres

    return [tuple(c) for c in centres]


def trouver_couleur_proche(r, g, b, palette):
    """Trouve la couleur la plus proche dans la palette"""
    min_dist = float("inf")
    meilleure_couleur = 0

    for i, (pr, pg, pb) in enumerate(palette):
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < min_dist:
            min_dist = dist
            meilleure_couleur = i

    return meilleure_couleur + 1


def image_vers_matrice(image_path, target_size=24, nb_couleurs=5):
    """Convertit une image en matrice avec quantification optimale"""
    img = Image.open(image_path)

    # ✅ AJOUT : Recadrage automatique
    if img.mode == "RGBA" or img.mode == "LA":
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

    # ✅ CHANGEMENT : LANCZOS pour courbes douces
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Convertir en RGBA
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # ✅ AJOUT : Seuillage alpha strict pour contours nets
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a < 200:
                img.putpixel((x, y), (0, 0, 0, 0))
            else:
                img.putpixel((x, y), (r, g, b, 255))

    width, height = img.size
    print(f"Taille de l'image : {width}x{height}")

    # Quantifier les couleurs avec K-means
    palette = quantifier_couleurs_kmeans(img, nb_couleurs)
    print(f"Palette créée : {len(palette)} couleurs")
    for i, (r, g, b) in enumerate(palette):
        print(f"  Couleur {i+1}: rgb({r}, {g}, {b})")

    # Créer la matrice
    matrice = []
    for y in range(height):
        ligne = []
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))

            if a < 128:
                ligne.append(0)
            else:
                couleur_id = trouver_couleur_proche(r, g, b, palette)
                ligne.append(couleur_id)

        matrice.append(ligne)

    return matrice, width, height, palette


def sauvegarder_matrice(matrice, width, height, palette, nom_fichier="matrice"):
    """Sauvegarde la matrice en JSON et JS"""

    palette_rgb = [f"rgb({r}, {g}, {b})" for r, g, b in palette]

    # JSON
    data = {"width": width, "height": height, "pixel": matrice, "palette": palette_rgb}
    with open(f"{nom_fichier}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Fichier JSON : {nom_fichier}.json")

    # JavaScript
    with open(f"{nom_fichier}.js", "w") as f:
        f.write(f"const pixel = {json.dumps(matrice)};\n")
        f.write(f"const width = {width};\n")
        f.write(f"const height = {height};\n")
        f.write(f"const palette = {json.dumps(palette_rgb)};\n")
    print(f"Fichier JS : {nom_fichier}.js")


def generer_image(
    matrice, width, height, palette, nom_fichier="pixel_art.png", scale=20
):
    """Génère une image PNG à partir de la matrice"""
    from PIL import ImageDraw

    img_output = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_output)

    colors_palette = [(0, 0, 0, 0)] + [(r, g, b, 255) for r, g, b in palette]

    for y in range(height):
        for x in range(width):
            value = matrice[y][x]
            color = colors_palette[value]

            x1 = x * scale
            y1 = y * scale
            x2 = x1 + scale
            y2 = y1 + scale
            draw.rectangle([x1, y1, x2, y2], fill=color)

    img_output.save(nom_fichier)
    print(f"Image générée : {nom_fichier}")


# Test
if __name__ == "__main__":
    chemin = input("Chemin de l'image : ")
    taille = input("Taille (16, 24, 32) [24 par défaut] : ") or "24"
    nb_couleurs = input("Nombre de couleurs (2-10) [5 par défaut] : ") or "5"

    matrice, w, h, palette = image_vers_matrice(chemin, int(taille), int(nb_couleurs))
    print(f"Matrice créée ! {w}x{h} avec {len(palette)} couleurs")

    # Générer les fichiers
    sauvegarder_matrice(matrice, w, h, palette)
    generer_image(matrice, w, h, palette)
