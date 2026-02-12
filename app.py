import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import json
import numpy as np
from convertisseur_simple import image_vers_matrice_simple
from convertisseur import image_vers_matrice


class PixelArtApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration fenêtre
        self.title("Convertisseur Pixel Art")
        self.geometry("700x950")

        # Variables
        self.image_path = None
        self.matrice = None
        self.width = None
        self.height = None
        self.palette = None
        self.preview_image = None
        self.base_image = None  # Cache image

        # Variables drag
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False

        # Variable zoom
        self.last_zoom = 10

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

        # Zoom
        ctk.CTkLabel(options_frame, text="Zoom:", font=("Helvetica", 12)).grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )

        self.zoom_var = ctk.IntVar(value=10)
        self.zoom_slider = ctk.CTkSlider(
            options_frame,
            from_=5,
            to=30,
            variable=self.zoom_var,
            number_of_steps=25,
            command=self.update_zoom_label,
        )
        self.zoom_slider.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        self.zoom_label = ctk.CTkLabel(
            options_frame, text="10x", font=("Helvetica", 12)
        )
        self.zoom_label.grid(row=3, column=2, padx=5, pady=10)

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
            width=200,
        )
        convert_btn.pack(pady=(20, 10))

        # Frame pour l'export
        export_container = ctk.CTkFrame(self, fg_color="transparent")
        export_container.pack(pady=(0, 20))

        export_frame = ctk.CTkFrame(export_container, fg_color="transparent")
        export_frame.pack(padx=(0, 45))

        # Label format
        ctk.CTkLabel(export_frame, text="Format :", font=("Helvetica", 12)).pack(
            side="left", padx=(0, 10)
        )

        # Menu format
        self.export_format_var = ctk.StringVar(value="JSON")
        export_format_menu = ctk.CTkOptionMenu(
            export_frame,
            values=["JSON", "JS", "Image PNG"],
            variable=self.export_format_var,
            width=120,
            command=self.on_format_change,
        )
        export_format_menu.pack(side="left", padx=5)

        # Label et menu scale
        self.scale_label = ctk.CTkLabel(
            export_frame, text="Taille :", font=("Helvetica", 12)
        )

        self.scale_var = ctk.StringVar(value="10x")
        self.scale_menu = ctk.CTkOptionMenu(
            export_frame,
            values=["5x", "10x", "20x", "30x", "50x"],
            variable=self.scale_var,
            width=80,
        )

        # Bouton Exporter
        self.export_btn = ctk.CTkButton(
            export_frame,
            text="Exporter",
            command=self.export_data,
            font=("Helvetica", 14, "bold"),
            height=40,
            width=150,
            state="disabled",
            fg_color="#2b7a2b",
            hover_color="#3a9a3a",
        )
        self.export_btn.pack(side="left", padx=10)

        # Prévisualisation (prend tout l'espace restant)
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            preview_frame, text="Prévisualisation", font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 5))

        # Canvas pour affichage avec drag (prend tout l'espace)
        self.canvas = Canvas(preview_frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Bind événements drag
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

        # Bind événements molette
        self.canvas.bind("<MouseWheel>", self.zoom_molette)
        self.canvas.bind("<Button-4>", self.zoom_molette)
        self.canvas.bind("<Button-5>", self.zoom_molette)

        # Bind resize canvas
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # ID de l'image sur le canvas
        self.canvas_image_id = None

    def choose_file(self):
        """Ouvre l'explorateur pour choisir une image"""
        file_path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Tous", "*.*")],
        )

        if file_path:
            self.image_path = file_path
            filename = file_path.split("/")[-1].split("\\")[-1]
            self.file_label.configure(text=filename)

    def on_canvas_resize(self, event):
        """Gère le redimensionnement du canvas"""
        pass

    def on_format_change(self, choice):
        """Affiche le menu scale si Image PNG est sélectionné"""
        if choice == "Image PNG":
            self.scale_label.pack(side="left", padx=(10, 5))
            self.scale_menu.pack(side="left", padx=5)
        else:
            self.scale_label.pack_forget()
            self.scale_menu.pack_forget()

    def start_drag(self, event):
        """Démarre le drag"""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        """Gère le déplacement pendant le drag"""
        if not self.is_dragging or self.canvas_image_id is None:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        self.canvas.move(self.canvas_image_id, dx, dy)

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def stop_drag(self, event):
        """Arrête le drag"""
        self.is_dragging = False

    def zoom_molette(self, event):
        """Zoom avec la molette centré sur le curseur"""
        if self.matrice is None or self.canvas_image_id is None:
            return

        if event.num == 5 or event.delta < 0:
            direction = -1
        elif event.num == 4 or event.delta > 0:
            direction = 1
        else:
            return

        current_zoom = self.zoom_var.get()
        new_zoom = current_zoom + (direction * 2)
        new_zoom = max(5, min(30, new_zoom))

        if new_zoom == current_zoom:
            return

        img_coords = self.canvas.coords(self.canvas_image_id)
        if not img_coords:
            return

        img_x, img_y = img_coords[0], img_coords[1]
        cursor_x = event.x
        cursor_y = event.y

        dx = cursor_x - img_x
        dy = cursor_y - img_y

        zoom_ratio = new_zoom / current_zoom

        new_img_x = cursor_x - (dx * zoom_ratio)
        new_img_y = cursor_y - (dy * zoom_ratio)

        self.zoom_var.set(new_zoom)
        self.zoom_label.configure(text=f"{new_zoom}x")
        self.last_zoom = new_zoom

        self.generate_preview_at_position(new_img_x, new_img_y)

    def update_zoom_label(self, value):
        """Met à jour le label du zoom"""
        self.zoom_label.configure(text=f"{int(value)}x")

        if self.matrice is not None and self.canvas_image_id is not None:
            img_coords = self.canvas.coords(self.canvas_image_id)
            if img_coords:
                current_x, current_y = img_coords[0], img_coords[1]

                self.canvas.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                canvas_center_x = canvas_width // 2
                canvas_center_y = canvas_height // 2

                dx = current_x - canvas_center_x
                dy = current_y - canvas_center_y

                old_zoom = self.last_zoom
                new_zoom = int(value)
                zoom_ratio = new_zoom / old_zoom if old_zoom > 0 else 1

                new_x = canvas_center_x + (dx * zoom_ratio)
                new_y = canvas_center_y + (dy * zoom_ratio)

                self.last_zoom = new_zoom
                self.generate_preview_at_position(new_x, new_y)
            else:
                self.generate_preview()

    def convert_image(self):
        """Convertit l'image avec l'algorithme choisi"""
        self.message_label.configure(text="", text_color="white")

        if not self.image_path:
            self.show_error("⚠️ Veuillez choisir une image !")
            return

        try:
            size = int(self.size_var.get())
            algo = self.algo_var.get()

            if algo == "simple":
                self.matrice, self.width, self.height = image_vers_matrice(
                    self.image_path, size
                )
                self.palette = None
            else:
                nb_colors = int(self.colors_var.get())
                self.matrice, self.width, self.height, self.palette = (
                    image_vers_matrice_simple(self.image_path, size, nb_colors)
                )

            self.creer_image_base()
            self.generate_preview()

            # Activer le bouton exporter
            self.export_btn.configure(state="normal")

            self.show_success(f"Image convertie en {self.width}x{self.height} !")

        except Exception as e:
            self.show_error(f"❌ Erreur : {str(e)}")

    def export_data(self):
        """Exporte selon le format choisi"""
        if self.matrice is None:
            self.show_error("⚠️ Aucune image convertie !")
            return

        format_type = self.export_format_var.get()

        try:
            if format_type == "JSON":
                self.export_json()
            elif format_type == "JS":
                self.export_js()
            elif format_type == "Image PNG":
                self.export_image()
        except Exception as e:
            self.show_error(f"❌ Erreur export : {str(e)}")

    def export_json(self):
        """Exporte en JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Exporter JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tous", "*.*")],
        )

        if not file_path:
            return

        if self.algo_var.get() == "simple":
            data = {"width": self.width, "height": self.height, "pixel": self.matrice}
        else:
            palette_rgb = [f"rgb({r}, {g}, {b})" for r, g, b in self.palette]
            data = {
                "width": self.width,
                "height": self.height,
                "pixel": self.matrice,
                "palette": palette_rgb,
            }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        self.show_success(f"Exporté : {file_path.split('/')[-1].split(chr(92))[-1]}")

    def export_js(self):
        """Exporte en JS"""
        file_path = filedialog.asksaveasfilename(
            title="Exporter JS",
            defaultextension=".js",
            filetypes=[("JavaScript", "*.js"), ("Tous", "*.*")],
        )

        if not file_path:
            return

        with open(file_path, "w") as f:
            f.write(f"const pixel = {json.dumps(self.matrice)};\n")
            f.write(f"const width = {self.width};\n")
            f.write(f"const height = {self.height};\n")

            if self.palette:
                palette_rgb = [f"rgb({r}, {g}, {b})" for r, g, b in self.palette]
                f.write(f"const palette = {json.dumps(palette_rgb)};\n")

        self.show_success(f"Exporté : {file_path.split('/')[-1].split(chr(92))[-1]}")

    def export_image(self):
        """Exporte l'image pixelisée en PNG"""
        file_path = filedialog.asksaveasfilename(
            title="Exporter Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Tous", "*.*")],
        )

        if not file_path:
            return

        # Récupérer le facteur de scale (ex: "10x" -> 10)
        scale_factor = int(self.scale_var.get().replace("x", ""))

        # Upscaler l'image de base avec NEAREST
        upscaled = self.base_image.resize(
            (self.width * scale_factor, self.height * scale_factor),
            Image.Resampling.NEAREST,
        )

        upscaled.save(file_path, "PNG")

        final_size = f"{self.width * scale_factor}x{self.height * scale_factor}"
        self.show_success(
            f"Exporté : {file_path.split('/')[-1].split(chr(92))[-1]} ({final_size})"
        )

    def creer_image_base(self):
        """Crée l'image de base en taille réelle"""
        if self.algo_var.get() == "simple":
            arr = np.array(self.matrice, dtype=np.uint8)
            self.base_image = Image.fromarray(arr, mode="RGBA")
        else:
            colors_palette = np.array(
                [(0, 0, 0, 0)] + [(r, g, b, 255) for r, g, b in self.palette],
                dtype=np.uint8,
            )
            arr = np.array(self.matrice, dtype=np.uint8)
            img_array = colors_palette[arr]
            self.base_image = Image.fromarray(img_array, mode="RGBA")

    def generate_preview(self):
        """Génère l'aperçu de l'image convertie"""
        if self.base_image is None:
            return

        scale = self.zoom_var.get()
        self.last_zoom = scale  # Mémoriser le zoom

        img = self.base_image.resize(
            (self.width * scale, self.height * scale), Image.Resampling.NEAREST
        )

        self.preview_image = ImageTk.PhotoImage(img)

        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)

        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x = canvas_width // 2 if canvas_width > 1 else 300
        y = canvas_height // 2 if canvas_height > 1 else 200

        self.canvas_image_id = self.canvas.create_image(
            x, y, image=self.preview_image, anchor="center"
        )

    def generate_preview_at_position(self, x, y):
        """Génère la preview à une position spécifique"""
        if self.base_image is None:
            return

        scale = self.zoom_var.get()

        img = self.base_image.resize(
            (self.width * scale, self.height * scale), Image.Resampling.NEAREST
        )

        self.preview_image = ImageTk.PhotoImage(img)

        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)

        self.canvas_image_id = self.canvas.create_image(
            x, y, image=self.preview_image, anchor="center"
        )

    def show_error(self, message):
        """Affiche un message d'erreur avec animation"""
        self.message_label.configure(text=message, text_color="#ff4444")
        self.animate_message()

    def show_success(self, message):
        """Affiche un message de succès"""
        self.message_label.configure(text=message, text_color="#44ff44")
        self.after(3000, lambda: self.message_label.configure(text=""))

    def animate_message(self):
        """Animation clignotement pour erreur"""

        def blink(count=0):
            if count < 6:
                if count % 2 == 0:
                    self.message_label.configure(text_color="#ff4444")
                else:
                    self.message_label.configure(text_color="#2b2b2b")
                self.after(200, lambda: blink(count + 1))
            else:
                self.message_label.configure(text_color="#ff4444")

        blink()


if __name__ == "__main__":
    app = PixelArtApp()
    app.mainloop()
