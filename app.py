import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
from convertisseur_simple import image_vers_matrice_simple
from convertisseur import image_vers_matrice


class PixelArtApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration fenêtre
        self.title("Convertisseur Pixel Art")
        self.geometry("700x800")

        # Variables
        self.image_path = None
        self.matrice = None
        self.width = None
        self.height = None
        self.palette = None
        self.preview_image = None

        # Mode sombre
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()

    def create_widgets(self):
        # Titre
        title = ctk.CTkLabel(
            self, text="Convertisseur Pixel Art", font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)

        # Sélection fichier
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(
            file_frame, text="Aucune image sélectionnée", font=("Helvetica", 12)
        )
        self.file_label.pack(side="left", padx=10, pady=10)

        file_btn = ctk.CTkButton(
            file_frame, text="Choisir image", command=self.choose_file
        )
        file_btn.pack(side="right", padx=10, pady=10)

        # Options
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=10, padx=20, fill="x")

        # Algorithme
        ctk.CTkLabel(options_frame, text="Algorithme:", font=("Helvetica", 12)).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.algo_var = ctk.StringVar(value="kmeans")

        algo_simple = ctk.CTkRadioButton(
            options_frame, text="Simple (RGBA)", variable=self.algo_var, value="simple"
        )
        algo_simple.grid(row=0, column=1, padx=5, pady=10)

        algo_kmeans = ctk.CTkRadioButton(
            options_frame, text="K-means", variable=self.algo_var, value="kmeans"
        )
        algo_kmeans.grid(row=0, column=2, padx=5, pady=10)

        # Dimension
        ctk.CTkLabel(options_frame, text="Dimension:", font=("Helvetica", 12)).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        self.size_var = ctk.StringVar(value="24")
        size_menu = ctk.CTkOptionMenu(
            options_frame, values=["16", "24", "32"], variable=self.size_var
        )
        size_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="w")

        # Nombre de couleurs
        ctk.CTkLabel(options_frame, text="Couleurs:", font=("Helvetica", 12)).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )

        self.colors_var = ctk.StringVar(value="5")
        colors_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            variable=self.colors_var,
        )
        colors_menu.grid(row=2, column=1, columnspan=2, padx=5, pady=10, sticky="w")

        # Message d'erreur/succès
        self.message_label = ctk.CTkLabel(
            self, text="", font=("Helvetica", 12), height=30
        )
        self.message_label.pack(pady=5)

        # Bouton Convertir
        convert_btn = ctk.CTkButton(
            self,
            text="Convertir",
            command=self.convert_image,
            font=("Helvetica", 14, "bold"),
            height=40,
        )
        convert_btn.pack(pady=20)

        # Prévisualisation
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            preview_frame, text="Prévisualisation", font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        self.preview_label = ctk.CTkLabel(preview_frame, text="")
        self.preview_label.pack(pady=10, expand=True)

    def choose_file(self):
        """Ouvre l'explorateur pour choisir une image"""
        file_path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Tous", "*.*")],
        )

        if file_path:
            self.image_path = file_path
            # Afficher le nom du fichier
            filename = file_path.split("/")[-1].split("\\")[-1]
            self.file_label.configure(text=filename)

    def convert_image(self):
        """Convertit l'image avec l'algorithme choisi"""
        # Effacer ancien message
        self.message_label.configure(text="", text_color="white")

        if not self.image_path:
            self.show_error("⚠️ Veuillez choisir une image !")
            return

        try:
            size = int(self.size_var.get())
            algo = self.algo_var.get()

            if algo == "simple":
                # Algorithme simple RGBA simple (sans palette)
                self.matrice, self.width, self.height = image_vers_matrice(
                    self.image_path, size
                )
                self.palette = None
            else:
                # Algorithme K-means (avec palette)
                nb_colors = int(self.colors_var.get())
                self.matrice, self.width, self.height, self.palette = (
                    image_vers_matrice_simple(self.image_path, size, nb_colors)
                )

            # Générer prévisualisation
            self.generate_preview()

            # Message de succès
            self.show_success(f"Image convertie en {self.width}x{self.height} !")

        except Exception as e:
            self.show_error(f"❌ Erreur : {str(e)}")

    def generate_preview(self):
        """Génère l'aperçu de l'image convertie"""
        scale = 10

        if self.algo_var.get() == "simple":
            # Simple RGBA
            img = Image.new(
                "RGBA", (self.width * scale, self.height * scale), (0, 0, 0, 0)
            )
            pixels = img.load()

            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = self.matrice[y][x]
                    for sy in range(scale):
                        for sx in range(scale):
                            pixels[x * scale + sx, y * scale + sy] = (r, g, b, a)
        else:
            # K-means avec palette
            img = Image.new(
                "RGBA", (self.width * scale, self.height * scale), (0, 0, 0, 0)
            )
            pixels = img.load()
            colors_palette = [(0, 0, 0, 0)] + [
                (r, g, b, 255) for r, g, b in self.palette
            ]

            for y in range(self.height):
                for x in range(self.width):
                    color_id = self.matrice[y][x]
                    color = colors_palette[color_id]
                    for sy in range(scale):
                        for sx in range(scale):
                            pixels[x * scale + sx, y * scale + sy] = color

        # Redimensionner pour l'affichage (max 400x400)
        max_size = 400
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.NEAREST)

        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_label.configure(image=self.preview_image, text="")

    def show_error(self, message):
        """Affiche un message d'erreur avec animation"""
        self.message_label.configure(text=message, text_color="#ff4444")
        self.animate_message()

    def show_success(self, message):
        """Affiche un message de succès"""
        self.message_label.configure(text=message, text_color="#44ff44")
        # Effacer après 3 secondes
        self.after(3000, lambda: self.message_label.configure(text=""))

    def animate_message(self):
        """Animation clignotement pour erreur"""

        def blink(count=0):
            if count < 6:
                # Utiliser gris foncé au lieu de transparent
                if count % 2 == 0:
                    self.message_label.configure(text_color="#ff4444")
                else:
                    self.message_label.configure(text_color="#2b2b2b")  # Fond sombre
                self.after(200, lambda: blink(count + 1))
            else:
                self.message_label.configure(text_color="#ff4444")

        blink()


if __name__ == "__main__":
    app = PixelArtApp()
    app.mainloop()
