from PIL import Image

def image_matrice(image_path, target_size=16):
    """Conertit une image en matrice + redimensionnenemt"""
    img = Image.open(image_path)

    #Redimensionner l'image
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    #Convertir en RGBA pour gérer la transparence
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    width, height = img.size
    print(f"Taille de l'image : {width}x{height}")

    return img, width, height

# Test
if __name__ == "__main__":
    chemin = input("Chemin de l'image :")
    taille = input("Taille demandée (16, 24, 32) [16 par défaut] :") or "16"


    img, w ,h = image_matrice(chemin, int(taille))
    print("Image chargée !")