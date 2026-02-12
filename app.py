import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json


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
            file_frame, text="Aucun fichier sélectionné", font=("Helvetica", 12)
        )
        self.file_label.pack(side="left", padx=10, pady=10)

        file_btn = ctk.CTkButton(
            file_frame, text="Choisir fichier", command=self.choose_file
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
            options_frame,
            values=[
                "16",
                "24",
                "32",
            ],
            variable=self.size_var,
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


if __name__ == "__main__":
    app = PixelArtApp()
    app.mainloop()
