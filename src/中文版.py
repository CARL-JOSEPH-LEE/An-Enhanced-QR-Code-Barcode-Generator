import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from barcode import (EAN13, EAN8, Code128, Code39, UPCA, ISBN13, PZN, JAN,
                     ISBN10, ISSN, ITF, Gs1_128)
from barcode.writer import ImageWriter
from pylibdmtx.pylibdmtx import encode as dmtx_encode
from PIL import Image, ImageTk, ImageOps
from io import BytesIO
import pdf417gen
import pyqrcodeng
import ttkbootstrap as ttkb
from reportlab.pdfgen import canvas
import base64
import svgwrite
from reportlab.lib.utils import ImageReader

# 导入所需的库

class BarcodeGenerator:
    """
    条码生成器类，用于创建条码和二维码的GUI应用
    """
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        """
        设置用户界面，包括所有的控件和布局
        """
        # 设置主窗口属性
        self.root.title("增强型二维码 & 条形码生成器")
        self.root.geometry("800x800")
        self.root.configure(bg='#1e90ff')  # 设置背景颜色

        # 设置ttkbootstrap的样式
        style = ttkb.Style(theme="flatly")

        # 创建主框架
        frame = ttk.Frame(self.root, padding="20", style='TFrame')
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 创建条码类型选择部分
        self.create_barcode_type_selection(frame)

        # 创建数据输入部分
        self.create_data_input(frame)

        # 创建QR码设置框架
        self.create_qr_settings_frame(frame)

        # 创建条码设置框架
        self.create_barcode_settings_frame(frame)

        # 创建颜色选择部分
        self.create_color_selection(frame)

        # 创建批量处理部分
        self.create_batch_processing(frame)

        # 创建按钮部分
        self.create_buttons(frame)

    def create_barcode_type_selection(self, parent_frame):
        """
        创建条码类型选择部分
        """
        barcode_types = ["QR Code", "EAN13", "EAN8", "Code128", "Code39", "UPCA",
                         "ISBN13", "ISBN10", "ISSN", "PZN", "JAN", "ITF", "GS1-128",
                         "DataMatrix", "Aztec", "PDF417"]
        ttk.Label(parent_frame, text="选择码类型:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_type_combobox = ttk.Combobox(parent_frame,
                                                  values=barcode_types,
                                                  state="readonly", style='TCombobox')
        self.barcode_type_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.barcode_type_combobox.current(0)  # 默认选择第一个
        self.barcode_type_combobox.bind("<<ComboboxSelected>>", self.on_barcode_type_change)

    def create_data_input(self, parent_frame):
        """
        创建数据输入部分
        """
        ttk.Label(parent_frame, text="输入数据:", style='TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_entry = ttk.Entry(parent_frame, width=40, style='TEntry')
        self.data_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    def create_qr_settings_frame(self, parent_frame):
        """
        创建QR码设置框架
        """
        self.qr_settings_frame = ttk.Frame(parent_frame, style='TFrame')
        self.qr_settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # QR码版本
        ttk.Label(self.qr_settings_frame, text="QR Code 版本 (1-40):", style='TLabel').grid(row=0, column=0,
                                                                                           sticky=tk.W, pady=5)
        self.version_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.version_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.version_entry.insert(0, "1")

        # 纠错等级
        ttk.Label(self.qr_settings_frame, text="纠错等级:", style='TLabel').grid(row=1, column=0, sticky=tk.W,
                                                                                 pady=5)
        self.error_correction_combobox = ttk.Combobox(self.qr_settings_frame, values=["L", "M", "Q", "H"],
                                                      state="readonly", style='TCombobox')
        self.error_correction_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.error_correction_combobox.current(3)  # 默认选择'H'

        # 方块大小
        ttk.Label(self.qr_settings_frame, text="方块大小(Box Size):", style='TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.box_size_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.box_size_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.box_size_entry.insert(0, "10")

        # 边框大小
        ttk.Label(self.qr_settings_frame, text="边框大小:", style='TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.border_entry = ttk.Entry(self.qr_settings_frame, width=10, style='TEntry')
        self.border_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.border_entry.insert(0, "4")

    def create_barcode_settings_frame(self, parent_frame):
        """
        创建条码设置框架
        """
        self.barcode_settings_frame = ttk.Frame(parent_frame, style='TFrame')
        self.barcode_settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        self.barcode_settings_frame.grid_remove()  # 默认隐藏

        # 模块宽度
        ttk.Label(self.barcode_settings_frame, text="模块宽度(Module Width):", style='TLabel').grid(row=0, column=0, sticky=tk.W,
                                                                                                  pady=5)
        self.module_width_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.module_width_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.module_width_entry.insert(0, "0.2")

        # 模块高度
        ttk.Label(self.barcode_settings_frame, text="模块高度(Module Height):", style='TLabel').grid(row=1, column=0, sticky=tk.W,
                                                                                                   pady=5)
        self.module_height_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.module_height_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.module_height_entry.insert(0, "15")

        # 字体大小
        ttk.Label(self.barcode_settings_frame, text="字体大小(Font Size):", style='TLabel').grid(row=2, column=0, sticky=tk.W,
                                                                                               pady=5)
        self.font_size_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.font_size_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.font_size_entry.insert(0, "10")

        # 文字距离
        ttk.Label(self.barcode_settings_frame, text="文字距离(Text Distance):", style='TLabel').grid(row=3, column=0, sticky=tk.W,
                                                                                                   pady=5)
        self.text_distance_entry = ttk.Entry(self.barcode_settings_frame, width=10, style='TEntry')
        self.text_distance_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.text_distance_entry.insert(0, "5")

    def create_color_selection(self, parent_frame):
        """
        创建颜色选择部分
        """
        # 前景色选择
        ttk.Label(parent_frame, text="填充颜色:", style='TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fill_color_btn = tk.Button(parent_frame, bg="black", command=lambda: self.choose_color(self.fill_color_btn),
                                        relief=tk.RAISED, bd=5, activebackground="#3498db")
        self.fill_color_btn.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # 背景色选择
        ttk.Label(parent_frame, text="背景颜色:", style='TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.back_color_btn = tk.Button(parent_frame, bg="white", command=lambda: self.choose_color(self.back_color_btn),
                                        relief=tk.RAISED, bd=5, activebackground="#3498db")
        self.back_color_btn.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

    def create_batch_processing(self, parent_frame):
        """
        创建批量处理部分
        """
        self.batch_frame = ttk.Frame(parent_frame, style='TFrame')
        self.batch_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.batch_var = tk.IntVar()
        self.batch_checkbutton = ttk.Checkbutton(self.batch_frame, text="批量导出", variable=self.batch_var,
                                                 style='TCheckbutton')
        self.batch_checkbutton.grid(row=0, column=0, sticky=tk.W)

        self.batch_entry = ttk.Entry(self.batch_frame, width=40, style='TEntry')
        self.batch_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.batch_entry.insert(0, "data1,data2,data3")  # 批量数据占位符

    def create_buttons(self, parent_frame):
        """
        创建生成和预览按钮部分
        """
        button_frame = ttk.Frame(parent_frame, style='TFrame')
        button_frame.grid(row=12, column=0, columnspan=2, pady=10)

        generate_button = tk.Button(button_frame, text="生成",
                                    command=lambda: self.on_generate_or_preview(preview=False), relief=tk.RAISED, bd=5,
                                    activebackground="#3498db", bg="SystemButtonFace", fg="black")
        generate_button.grid(row=0, column=0, padx=5)

        preview_button = tk.Button(button_frame, text="预览",
                                   command=lambda: self.on_generate_or_preview(preview=True), relief=tk.RAISED, bd=5,
                                   activebackground="#3498db", bg="SystemButtonFace", fg="black")
        preview_button.grid(row=0, column=1, padx=5)

        self.add_button_effects(generate_button)
        self.add_button_effects(preview_button)

    def add_button_effects(self, button):
        """
        为按钮添加鼠标悬停效果
        """
        button.bind("<Enter>", lambda e: button.config(bg="#2980b9", relief=tk.SUNKEN))
        button.bind("<Leave>", lambda e: button.config(bg="SystemButtonFace", relief=tk.RAISED))

    def on_barcode_type_change(self, event):
        """
        当条码类型改变时，更新界面显示
        """
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
        """
        弹出颜色选择器，选择颜色
        """
        color_code = colorchooser.askcolor(title="选择颜色")[1]
        if color_code:
            btn.config(bg=color_code)

    def on_generate_or_preview(self, preview=False):
        """
        处理生成或预览按钮的点击事件
        """
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
                                                                   filetypes=[("PNG文件", "*.png"),
                                                                              ("JPG文件", "*.jpg"),
                                                                              ("BMP文件", "*.bmp"),
                                                                              ("GIF文件", "*.gif"),
                                                                              ("TIFF文件", "*.tiff"),
                                                                              ("ICO文件", "*.ico"),
                                                                              ("WEBP文件", "*.webp"),
                                                                              ("SVG文件", "*.svg"),
                                                                              ("PDF文件", "*.pdf"),
                                                                              ("EPS文件", "*.eps"),
                                                                              ("PBM文件", "*.pbm"),
                                                                              ("PGM文件", "*.pgm"),
                                                                              ("PPM文件", "*.ppm"),
                                                                              ("XBM文件", "*.xbm"),
                                                                              ("XPM文件", "*.xpm"),
                                                                              ("PCX文件", "*.pcx"),
                                                                              ("TGA文件", "*.tga"),
                                                                              ("所有文件", "*.*")])
                        if output_path:
                            self.save_image(img, output_path)
            else:
                data = self.data_entry.get()
                img = self.generate_image(data, fill_color, back_color)
                if preview:
                    self.preview_image(img)
                else:
                    output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                               filetypes=[("PNG文件", "*.png"),
                                                                          ("JPG文件", "*.jpg"),
                                                                          ("BMP文件", "*.bmp"),
                                                                          ("GIF文件", "*.gif"),
                                                                          ("TIFF文件", "*.tiff"),
                                                                          ("ICO文件", "*.ico"),
                                                                          ("WEBP文件", "*.webp"),
                                                                          ("SVG文件", "*.svg"),
                                                                          ("PDF文件", "*.pdf"),
                                                                          ("EPS文件", "*.eps"),
                                                                          ("PBM文件", "*.pbm"),
                                                                          ("PGM文件", "*.pgm"),
                                                                          ("PPM文件", "*.ppm"),
                                                                          ("XBM文件", "*.xbm"),
                                                                          ("XPM文件", "*.xpm"),
                                                                          ("PCX文件", "*.pcx"),
                                                                          ("TGA文件", "*.tga"),
                                                                          ("所有文件", "*.*")])
                    if output_path:
                        self.save_image(img, output_path)
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {e}")

    def generate_image(self, data, fill_color="black", back_color="white"):
        """
        根据输入的数据和参数生成条码/二维码的图像
        """
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
        """
        生成二维码图像
        """
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
        """
        生成条形码图像
        """
        writer = ImageWriter()
        writer.set_options({
            'module_width': module_width,
            'module_height': module_height,
            'font_size': font_size,
            'text_distance': text_distance,
        })

        # 条形码类型映射
        barcode_class = {
            'EAN13': EAN13,
            'EAN8': EAN8,
            'Code128': Code128,
            'Code39': Code39,
            'UPCA': UPCA,
            'ISBN13': ISBN13,
            'ISBN10': ISBN10,
            'ISSN': ISSN,
            'PZN': PZN,
            'JAN': JAN,
            'ITF': ITF,
            'GS1-128': Gs1_128
        }.get(barcode_type)

        if not barcode_class:
            raise ValueError("不支持的条码类型")

        barcode = barcode_class(data, writer=writer)

        barcode_bytes = BytesIO()
        barcode.write(barcode_bytes)
        barcode_bytes.seek(0)
        img = Image.open(barcode_bytes).convert("RGB")

        # 应用填充颜色和背景颜色
        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)

        return img

    def generate_datamatrix(self, data, fill_color="black", back_color="white"):
        """
        生成DataMatrix码图像
        """
        encoded = dmtx_encode(data.encode('utf-8'))
        img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)
        return img

    def generate_aztec(self, data, fill_color="black", back_color="white"):
        """
        生成Aztec码图像
        """
        qr = pyqrcodeng.create(data)
        buffer = BytesIO()
        qr.png(buffer, scale=5, module_color=fill_color, background=back_color)
        img = Image.open(buffer)
        return img

    def generate_pdf417(self, data, fill_color="black", back_color="white"):
        """
        生成PDF417码图像
        """
        codes = pdf417gen.encode(data)
        img = pdf417gen.render_image(codes, scale=3, ratio=3)
        img = ImageOps.colorize(ImageOps.grayscale(img), black=fill_color, white=back_color)
        return img

    def save_image(self, img, file_path):
        """
        保存图像到指定路径
        """
        try:
            extension = file_path.split('.')[-1].lower()
            if extension == 'pdf':
                self.save_as_pdf(img, file_path)
            elif extension == 'svg':
                self.save_as_svg(img, file_path)
            else:
                img.save(file_path)
            messagebox.showinfo("成功", f"图像成功保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图像失败: {e}")

    def save_as_pdf(self, img, file_path):
        """
        将图像保存为PDF格式
        """
        try:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            pdf_canvas = canvas.Canvas(file_path, pagesize=(img.width, img.height))
            pdf_canvas.drawImage(ImageReader(buffer), 0, 0, width=img.width, height=img.height)
            pdf_canvas.showPage()
            pdf_canvas.save()
        except Exception as e:
            messagebox.showerror("错误", f"保存PDF失败: {e}")

    def save_as_svg(self, img, file_path):
        """
        将图像保存为SVG格式
        """
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        dwg = svgwrite.Drawing(file_path, profile='tiny', size=img.size)
        image_data = buffer.getvalue()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        dwg.add(dwg.image(href='data:image/png;base64,' + image_base64, insert=(0, 0), size=img.size))
        dwg.save()

    def preview_image(self, img):
        """
        预览生成的图像
        """
        preview_window = tk.Toplevel(self.root)
        preview_window.title("预览")
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
        """
        验证输入的参数是否合法
        """
        if not data:
            raise ValueError("请输入要编码的数据")

        if barcode_type == 'QR Code':
            if not (1 <= version <= 40):
                raise ValueError("QR Code版本必须在1到40之间")
            if box_size <= 0:
                raise ValueError("方块大小必须大于0")
            if border < 0:
                raise ValueError("边框大小不能为负数")
        else:
            if module_width <= 0:
                raise ValueError("模块宽度必须大于0")
            if module_height <= 0:
                raise ValueError("模块高度必须大于0")
            if font_size <= 0:
                raise ValueError("字体大小必须大于0")
            if text_distance < 0:
                raise ValueError("文字距离不能为负数")

if __name__ == "__main__":
    root = ttkb.Window()
    app = BarcodeGenerator(root)
    root.mainloop()

