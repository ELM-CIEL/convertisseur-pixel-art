from PIL import Image

def image_matrice(image_path):
    """Conertit une image en matrice"""
    img = Image.open(image_path)

    #Convertir en RGBA pour gérer la transparence
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    width, height = img.size
    print(f"Taille de l'image : {width}x{height}")

    return img, width, height

# Test
if __name__ == "__main__":
    chemin = input("Chemin de l'image :")
    img, w ,h = image_matrice(chemin)
    print("Image chargée !")""