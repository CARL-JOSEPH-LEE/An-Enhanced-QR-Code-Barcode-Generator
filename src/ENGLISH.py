import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from barcode import EAN13, Code128, Code39, UPCA, ISBN13, PZN, JAN, EAN8, ISBN10, ISSN, ITF, Gs1_128
from barcode.writer import ImageWriter
from pylibdmtx.pylibdmtx import encode as dmtx_encode
from PIL import Image, ImageTk, ImageDraw, ImageOps
from io import BytesIO
import pdf417gen
import pyqrcodeng
import ttkbootstrap as ttkb
from reportlab.pdfgen import canvas
import base64
import svgwrite
from reportlab.lib.utils import ImageReader


class BarcodeGenerator:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Enhanced QR Code & Barcode Generator")
        self.root.geometry("800x800")
        self.root.configure(bg='#1e90ff')

        style = ttkb.Style(theme="flatly")
        frame = ttk.Frame(self.root, padding="20", style='TFrame')
        frame.grid(row=0, column=0, sticky="")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(frame, text="Select Code Type:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_type_combobox = ttk.Combobox(frame,
                                                  values=["QR Code", "EAN13", "EAN8", "Code128", "Code39", "UPCA",
                                                          "ISBN13", "ISBN10", "ISSN", "PZN", "JAN", "ITF", "GS1-128",
                                                          "DataMatrix", "Aztec", "PDF417"], state="readonly",
                                                  style='TCombobox')
        self.barcode_type_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.barcode_type_combobox.current(0)
        self.barcode_type_combobox.bind("<<ComboboxSelected>>", self.on_barcode_type_change)

        ttk.Label(frame, text="Enter Data:", style='TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_entry = ttk.Entry(frame, width=40, style='TEntry')
        self.data_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        self.qr_settings_frame = ttk.Frame(frame, style='TFrame')
        self.qr_settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(self.qr_settings_frame, text="QR Code Version (1-40):", style='TLabel').grid(row=0, column=0,
                                                                                               sticky=tk.W, pady=5)
        self.version_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.version_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.version_entry.insert(0, "1")

        ttk.Label(self.qr_settings_frame, text="Error Correction:", style='TLabel').grid(row=1, column=0, sticky=tk.W,
                                                                                         pady=5)
        self.error_correction_combobox = ttk.Combobox(self.qr_settings_frame, values=["L", "M", "Q", "H"],
                                                      state="readonly", style='TCombobox')
        self.error_correction_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.error_correction_combobox.current(3)

        ttk.Label(self.qr_settings_frame, text="Box Size:", style='TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.box_size_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.box_size_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.box_size_entry.insert(0, "10")

        ttk.Label(self.qr_settings_frame, text="Border Size:", style='TLabel').grid(row=3, column=0, sticky=tk.W,
                                                                                    pady=5)
        self.border_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.border_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.border_entry.insert(0, "4")

        self.barcode_settings_frame = ttk.Frame(frame, style='TFrame')
        self.barcode_settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        self.barcode_settings_frame.grid_remove()

        ttk.Label(self.barcode_settings_frame, text="Module Width:", style='TLabel').grid(row=0, column=0, sticky=tk.W,
                                                                                          pady=5)
        self.module_width_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.module_width_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.module_width_entry.insert(0, "0.2")

        ttk.Label(self.barcode_settings_frame, text="Module Height:", style='TLabel').grid(row=1, column=0, sticky=tk.W,
                                                                                           pady=5)
        self.module_height_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.module_height_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.module_height_entry.insert(0, "15")

        ttk.Label(self.barcode_settings_frame, text="Font Size:", style='TLabel').grid(row=2, column=0, sticky=tk.W,
                                                                                       pady=5)
        self.font_size_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.font_size_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.font_size_entry.insert(0, "10")

        ttk.Label(self.barcode_settings_frame, text="Text Distance:", style='TLabel').grid(row=3, column=0, sticky=tk.W,
                                                                                           pady=5)
        self.text_distance_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.text_distance_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.text_distance_entry.insert(0, "5")

        ttk.Label(frame, text="Fill Color:", style='TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fill_color_btn = tk.Button(frame, bg="black", command=lambda: self.choose_color(self.fill_color_btn),
                                        relief=tk.RAISED, bd=5, activebackground="#3498db")
        self.fill_color_btn.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(frame, text="Background Color:", style='TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.back_color_btn = tk.Button(frame, bg="white", command=lambda: self.choose_color(self.back_color_btn),
                                        relief=tk.RAISED, bd=5, activebackground="#3498db")
        self.back_color_btn.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        self.batch_frame = ttk.Frame(frame, style='TFrame')
        self.batch_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.batch_var = tk.IntVar()
        self.batch_checkbutton = ttk.Checkbutton(self.batch_frame, text="Batch Export", variable=self.batch_var,
                                                 style='TCheckbutton')
        self.batch_checkbutton.grid(row=0, column=0, sticky=tk.W)

        self.batch_entry = ttk.Entry(self.batch_frame, width=40, style='TEntry')
        self.batch_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.batch_entry.insert(0, "data1,data2,data3")  # Placeholder for batch data

        button_frame = ttk.Frame(frame, style='TFrame')
        button_frame.grid(row=12, column=0, columnspan=2, pady=10)

        generate_button = tk.Button(button_frame, text="Generate",
                                    command=lambda: self.on_generate_or_preview(preview=False), relief=tk.RAISED, bd=5,
                                    activebackground="#3498db", bg="SystemButtonFace", fg="black")
        generate_button.grid(row=0, column=0, padx=5)

        preview_button = tk.Button(button_frame, text="Preview",
                                   command=lambda: self.on_generate_or_preview(preview=True), relief=tk.RAISED, bd=5,
                                   activebackground="#3498db", bg="SystemButtonFace", fg="black")
        preview_button.grid(row=0, column=1, padx=5)

        self.add_button_effects(generate_button)
        self.add_button_effects(preview_button)

    def add_button_effects(self, button):
        button.bind("<Enter>", lambda e: button.config(bg="#2980b9", relief=tk.SUNKEN))
        button.bind("<Leave>", lambda e: button.config(bg="SystemButtonFace", relief=tk.RAISED))

    def on_barcode_type_change(self, event):
        barcode_type = self.barcode_type_combobox.get()
        if barcode_type == 'QR Code':
            self.qr_settings_frame.grid()
            self.barcode_settings_frame.grid_remove()
        elif barcode_type in ['EAN13', 'EAN8', 'Code128', 'Code39', 'UPCA', 'ISBN13', 'ISBN10', 'ISSN', 'PZN', 'JAN',
                              'ITF', 'GS1-128']:
            self.qr_settings_frame.grid_remove()
            self.barcode_settings_frame.grid()
        else:
            self.qr_settings_frame.grid_remove()
            self.barcode_settings_frame.grid_remove()

    def choose_color(self, btn):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            btn.config(bg=color_code)

    def on_generate_or_preview(self, preview=False):
        fill_color = self.fill_color_btn['bg'] if self.fill_color_btn['bg'] != "SystemButtonFace" else "black"
        back_color = self.back_color_btn['bg'] if self.back_color_btn['bg'] != "SystemButtonFace" else "white"

        if fill_color == "SystemButtonFace":
            fill_color = "black"
        if back_color == "SystemButtonFace":
            back_color = "white"

        try:
            if self.batch_var.get() == 1:
                batch_data = self.batch_entry.get().split(',')
                for data in batch_data:
                    img = self.generate_image(data.strip(), fill_color, back_color)
                    if not preview:
                        output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                                   filetypes=[("PNG files", "*.png"),
                                                                              ("JPG files", "*.jpg"),
                                                                              ("BMP files", "*.bmp"),
                                                                              ("GIF files", "*.gif"),
                                                                              ("TIFF files", "*.tiff"),
                                                                              ("ICO files", "*.ico"),
                                                                              ("WEBP files", "*.webp"),
                                                                              ("SVG files", "*.svg"),
                                                                              ("PDF files", "*.pdf"),
                                                                              ("EPS files", "*.eps"),
                                                                              ("PBM files", "*.pbm"),
                                                                              ("PGM files", "*.pgm"),
                                                                              ("PPM files", "*.ppm"),
                                                                              ("XBM files", "*.xbm"),
                                                                              ("XPM files", "*.xpm"),
                                                                              ("PCX files", "*.pcx"),
                                                                              ("TGA files", "*.tga"),
                                                                              ("All files", "*.*")])
                        if output_path:
                            self.save_image(img, output_path)
            else:
                data = self.data_entry.get()
                img = self.generate_image(data, fill_color, back_color)
                if preview:
                    self.preview_image(img)
                else:
                    output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                               filetypes=[("PNG files", "*.png"),
                                                                          ("JPG files", "*.jpg"),
                                                                          ("BMP files", "*.bmp"),
                                                                          ("GIF files", "*.gif"),
                                                                          ("TIFF files", "*.tiff"),
                                                                          ("ICO files", "*.ico"),
                                                                          ("WEBP files", "*.webp"),
                                                                          ("SVG files", "*.svg"),
                                                                          ("PDF files", "*.pdf"),
                                                                          ("EPS files", "*.eps"),
                                                                          ("PBM files", "*.pbm"),
                                                                          ("PGM files", "*.pgm"),
                                                                          ("PPM files", "*.ppm"),
                                                                          ("XBM files", "*.xbm"),
                                                                          ("XPM files", "*.xpm"),
                                                                          ("PCX files", "*.pcx"),
                                                                          ("TGA files", "*.tga"),
                                                                          ("All files", "*.*")])
                    if output_path:
                        self.save_image(img, output_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_image(self, data, fill_color="black", back_color="white"):
        barcode_type = self.barcode_type_combobox.get()
        if barcode_type == 'QR Code':
            version = int(self.version_entry.get())
            error_correction = self.error_correction_combobox.get()
            box_size = int(self.box_size_entry.get())
            border = int(self.border_entry.get())
            self.validate_inputs(data, barcode_type, version, box_size, border, None, None, None, None)
            img = self.generate_qr_code(data, version, error_correction, box_size, border, fill_color=fill_color,
                                        back_color=back_color)
        elif barcode_type == 'DataMatrix':
            img = self.generate_datamatrix(data, fill_color=fill_color, back_color=back_color)
        elif barcode_type == 'Aztec':
            img = self.generate_aztec(data, fill_color=fill_color, back_color=back_color)
        elif barcode_type == 'PDF417':
            img = self.generate_pdf417(data, fill_color=fill_color, back_color=back_color)
        else:
            module_width = float(self.module_width_entry.get())
            module_height = float(self.module_height_entry.get())
            font_size = int(self.font_size_entry.get())
            text_distance = int(self.text_distance_entry.get())
            self.validate_inputs(data, barcode_type, None, None, None, module_width, module_height, font_size,
                                 text_distance)
            img = self.generate_barcode(data, barcode_type, module_width, module_height, font_size, text_distance,
                                        fill_color=fill_color, back_color=back_color)
        return img

    def generate_qr_code(self, data, version, error_correction, box_size, border, fill_color="black",
                         back_color="white"):
        error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction_map[error_correction],
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
        return img

    def generate_barcode(self, data, barcode_type='EAN13', module_width=0.2, module_height=15, font_size=10,
                         text_distance=5, fill_color="black", back_color="white"):
        writer = ImageWriter()
        writer.set_options({
            'module_width': module_width,
            'module_height': module_height,
            'font_size': font_size,
            'text_distance': text_distance,
        })

        if barcode_type == 'EAN13':
            barcode = EAN13(data, writer=writer)
        elif barcode_type == 'EAN8':
            barcode = EAN8(data, writer=writer)
        elif barcode_type == 'Code128':
            barcode = Code128(data, writer=writer)
        elif barcode_type == 'Code39':
            barcode = Code39(data, writer=writer)
        elif barcode_type == 'UPCA':
            barcode = UPCA(data, writer=writer)
        elif barcode_type == 'ISBN13':
            barcode = ISBN13(data, writer=writer)
        elif barcode_type == 'ISBN10':
            barcode = ISBN10(data, writer=writer)
        elif barcode_type == 'ISSN':
            barcode = ISSN(data, writer=writer)
        elif barcode_type == 'PZN':
            barcode = PZN(data, writer=writer)
        elif barcode_type == 'JAN':
            barcode = JAN(data, writer=writer)
        elif barcode_type == 'ITF':
            barcode = ITF(data, writer=writer)
        elif barcode_type == 'GS1-128':
            barcode = Gs1_128(data, writer=writer)
        else:
            raise ValueError("Unsupported barcode type")

        barcode_bytes = BytesIO()
        barcode.write(barcode_bytes)
        barcode_bytes.seek(0)
        img = Image.open(barcode_bytes).convert("RGB")

        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)

        return img

    def generate_datamatrix(self, data, fill_color="black", back_color="white"):
        encoded = dmtx_encode(data.encode('utf-8'))
        img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)
        return img

    def generate_aztec(self, data, fill_color="black", back_color="white"):
        qr = pyqrcodeng.create(data)
        buffer = BytesIO()
        qr.png(buffer, scale=5, module_color=fill_color, background=back_color)
        img = Image.open(buffer)
        return img

    def generate_pdf417(self, data, fill_color="black", back_color="white"):
        codes = pdf417gen.encode(data)
        img = pdf417gen.render_image(codes, scale=3, ratio=3)
        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)
        return img

    def save_image(self, img, file_path):
        try:
            extension = file_path.split('.')[-1].lower()
            if extension == 'pdf':
                self.save_as_pdf(img, file_path)
            elif extension == 'svg':
                self.save_as_svg(img, file_path)
            elif extension == 'bmp':
                img.save(file_path, format='BMP')
            elif extension == 'gif':
                img = img.convert("P", palette=Image.ADAPTIVE)
                img.save(file_path, format='GIF')
            elif extension in ['tiff', 'tif']:
                img.save(file_path, format='TIFF')
            elif extension == 'ico':
                img.save(file_path, format='ICO')
            elif extension == 'webp':
                img.save(file_path, format='WEBP')
            elif extension in ['jpg', 'jpeg']:
                img.save(file_path, format='JPEG')
            elif extension == 'eps':
                img.save(file_path, format='EPS')
            elif extension == 'pbm':
                img.save(file_path, format='PBM')
            elif extension == 'pgm':
                img.save(file_path, format='PGM')
            elif extension == 'ppm':
                img.save(file_path, format='PPM')
            elif extension == 'xbm':
                img.save(file_path, format='XBM')
            elif extension == 'xpm':
                img.save(file_path, format='XPM')
            elif extension == 'pcx':
                img.save(file_path, format='PCX')
            elif extension == 'tga':
                img.save(file_path, format='TGA')
            else:
                img.save(file_path, format='PNG')
            messagebox.showinfo("Success", f"Image saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def save_as_pdf(self, img, file_path):
        try:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            pdf_canvas = canvas.Canvas(file_path, pagesize=(img.width, img.height))
            pdf_canvas.drawImage(ImageReader(buffer), 0, 0, width=img.width, height=img.height)
            pdf_canvas.showPage()
            pdf_canvas.save()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def save_as_svg(self, img, file_path):
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        dwg = svgwrite.Drawing(file_path, profile='tiny', size=img.size)
        image_data = buffer.getvalue()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        dwg.add(dwg.image(href='data:image/png;base64,' + image_base64, insert=(0, 0), size=img.size))
        dwg.save()

    def preview_image(self, img):
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview")
        preview_window.geometry("600x600")
        preview_canvas = tk.Canvas(preview_window, width=600, height=600)
        preview_canvas.pack()

        img.thumbnail((600, 600), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)

        preview_canvas.create_image(300, 300, image=tk_img, anchor=tk.CENTER)
        preview_canvas.image = tk_img
        preview_window.mainloop()

    def validate_inputs(self, data, barcode_type, version, box_size, border, module_width, module_height, font_size,
                        text_distance):
        if not data:
            raise ValueError("Please enter data to encode")

        if barcode_type == 'QR Code':
            if not (1 <= version <= 40):
                raise ValueError("QR Code version must be between 1 and 40")
            if box_size <= 0:
                raise ValueError("Box size must be greater than 0")
            if border < 0:
                raise ValueError("Border size cannot be negative")
        else:
            if module_width <= 0:
                raise ValueError("Module width must be greater than 0")
            if module_height <= 0:
                raise ValueError("Module height must be greater than 0")
            if font_size <= 0:
                raise ValueError("Font size must be greater than 0")
            if text_distance < 0:
                raise ValueError("Text distance cannot be negative")


if __name__ == "__main__":
    root = ttkb.Window()
    app = BarcodeGenerator(root)
    root.mainloop()