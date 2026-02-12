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
            self,
            text="Convertisseur Pixel Art",
            font=("Helvetica", 24, "bold"),
        )
        title.pack(pady=20)

        # Message test
        ctk.CTkLabel(self, text="Hello, je suis un test").pack(pady=100)


if __name__ == "__main__":
    app = PixelArtApp()
    app.mainloop()
