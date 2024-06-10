import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import ImageGrab, Image, ImageTk
import math
from queue import Queue

class VektorDraw:
    def __init__(self, root, cb, parent=None):
        self.root = root
        self.root.title("VEKTOR DRAW")
        self.root.geometry("1150x720")
        self.root.configure(bg="#f0f0f0")

        self.canvas = tk.Canvas(root, height=600, width=1000, bg=cb)
        self.canvas.grid(row=1, column=0, columnspan=2000, padx=10, pady=10)

        self.cl = "black"
        self.current_algorithm = None
        self.temp_shape = None
        self.start = None
        self.triangle_points = []
        self.transform_item = None

        # Toolbar
        self.toolbar = tk.Frame(root, bg="#e0e0e0", bd=2)
        self.toolbar.grid(row=0, column=0, columnspan=2000, sticky="we")

        self.toolbar_buttons = []
        self.toolbar_labels = []

        # Icons
        self.icons = {
            "save_image": ImageTk.PhotoImage(Image.open("icons/save-image.png")),
            "line_bresenham": ImageTk.PhotoImage(Image.open("icons/bresenham-line.png")),
            "line_dda": ImageTk.PhotoImage(Image.open("icons/dda-line.png")),
            "circle_midpoint": ImageTk.PhotoImage(Image.open("icons/circle.png")),
            "ellipse_midpoint": ImageTk.PhotoImage(Image.open("icons/ellips.png")),
            "triangle": ImageTk.PhotoImage(Image.open("icons/triangle.png")),
            "choose_color": ImageTk.PhotoImage(Image.open("icons/choose-color.png")),
            "background_color": ImageTk.PhotoImage(Image.open("icons/background-color.png")),
            "translate": ImageTk.PhotoImage(Image.open("icons/translate.png")),
            "rotate": ImageTk.PhotoImage(Image.open("icons/rotate.png")),
            "scale": ImageTk.PhotoImage(Image.open("icons/scale.png")),
            "reflect": ImageTk.PhotoImage(Image.open("icons/reflect.png")),
            "boundary_fill": ImageTk.PhotoImage(Image.open("icons/boundary-fill.png")),
            "flood_fill": ImageTk.PhotoImage(Image.open("icons/flood-fill.png")),
        }

        self.add_toolbar_button("save_image", self.save_image, "Save Image")
        self.add_toolbar_button("line_bresenham", self.line_bresenham_mode, "Bresenham Line")
        self.add_toolbar_button("line_dda", self.line_dda_mode, "DDA Line")
        self.add_toolbar_button("circle_midpoint", self.circle_midpoint_mode, "Circle Shape")
        self.add_toolbar_button("ellipse_midpoint", self.ellipse_midpoint_mode, "Ellipse Shape")
        self.add_toolbar_button("triangle", self.triangle_mode, "Triangle Shape")
        self.add_toolbar_button("translate", self.translate_mode, "Translate Transfrom")
        self.add_toolbar_button("rotate", self.rotate_mode, "Rotate Transfrom")
        self.add_toolbar_button("scale", self.scale_mode, "Scale Transfrom")
        self.add_toolbar_button("reflect", self.reflect_mode, "Reflect Transfrom")
        self.add_toolbar_button("choose_color", self.choose_color, "Choose Color")
        self.add_toolbar_button("background_color", self.choose_bg_color, "Background Color")
        self.add_toolbar_button("boundary_fill", self.boundary_fill_mode, "Boundary Fill")
        self.add_toolbar_button("flood_fill", self.flood_fill_mode, "Flood Fill")

        # Status bar
        self.status = tk.Label(root, text="Welcome to VectorDraw", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.grid(row=2, column=0, columnspan=2000, sticky="we")

        self.drawn = None

    def add_toolbar_button(self, icon_name, command, text_label):
        button_frame = tk.Frame(self.toolbar, bg="#e0e0e0")
        button_frame.pack(side=tk.LEFT, padx=2, pady=2)

        button = tk.Button(button_frame, image=self.icons[icon_name], command=command, bg="#e0e0e0", bd=0)
        button.pack(side=tk.TOP)

        label = tk.Label(button_frame, text=text_label, bg="#e0e0e0")
        label.pack(side=tk.BOTTOM)

        # Save the button and label references if needed
        self.toolbar_buttons.append(button)
        self.toolbar_labels.append(label)



    def choose_color(self):
        cx = colorchooser.askcolor()
        self.cl = cx[1]

    def choose_bg_color(self):
        cb = colorchooser.askcolor()
        self.canvas.configure(bg=cb[1])

    def save_image(self):
        x2 = self.root.winfo_rootx() + self.canvas.winfo_x()
        y2 = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x2 + self.canvas.winfo_width()
        y1 = y2 + self.canvas.winfo_height()
        I = ImageGrab.grab().crop((x2, y2, x1, y1))
        filename = filedialog.askdirectory()
        if filename:
            I.save(f"{filename}/canvas_image.jpg")

    def line_bresenham_mode(self):
        self.current_algorithm = "line_bresenham"
        self.bind_canvas_events()
        self.update_status("Bresenham Line Drawing Mode")

    def circle_midpoint_mode(self):
        self.current_algorithm = "circle_midpoint"
        self.bind_canvas_events()
        self.update_status("Midpoint Circle Drawing Mode")

    def ellipse_midpoint_mode(self):
        self.current_algorithm = "ellipse_midpoint"
        self.bind_canvas_events()
        self.update_status("Midpoint Ellipse Drawing Mode")

    def line_dda_mode(self):
        self.current_algorithm = "line_dda"
        self.bind_canvas_events()
        self.update_status("DDA Line Drawing Mode")

    def triangle_mode(self):
        self.current_algorithm = "triangle"
        self.canvas.bind('<ButtonPress-1>', self.onTriangleClick)
        self.update_status("Triangle Drawing Mode")

    def bind_canvas_events(self):
        self.canvas.bind('<ButtonPress-1>', self.onStart)
        self.canvas.bind('<ButtonRelease-1>', self.onEnd)
        self.canvas.bind('<Motion>', self.onDrag)

    def onStart(self, event):
        self.start = (event.x, event.y)
        self.temp_shape = None

    def onDrag(self, event):
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
        if self.current_algorithm == "line_bresenham" or self.current_algorithm == "line_dda":
            self.temp_shape = self.canvas.create_line(self.start[0], self.start[1], event.x, event.y, fill=self.cl)
        elif self.current_algorithm == "circle_midpoint":
            radius = int(((self.start[0] - event.x) ** 2 + (self.start[1] - event.y) ** 2) ** 0.5)
            self.temp_shape = self.canvas.create_oval(self.start[0] - radius, self.start[1] - radius, self.start[0] + radius, self.start[1] + radius, outline=self.cl)
        elif self.current_algorithm == "ellipse_midpoint":
            rx = abs(self.start[0] - event.x)
            ry = abs(self.start[1] - event.y)
            self.temp_shape = self.canvas.create_oval(self.start[0] - rx, self.start[1] - ry, self.start[0] + rx, self.start[1] + ry, outline=self.cl)

    def onEnd(self, event):
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
        if self.current_algorithm == "line_bresenham":
            if self.start:
                line_bresenham(self.start[0], self.start[1], event.x, event.y, self.canvas, self.cl)
        elif self.current_algorithm == "line_dda":
            if self.start:
                line_dda(self.start[0], self.start[1], event.x, event.y, self.canvas, self.cl)
        elif self.current_algorithm == "circle_midpoint":
            if self.start:
                radius = int(((self.start[0] - event.x) ** 2 + (self.start[1] - event.y) ** 2) ** 0.5)
                circle_midpoint(self.start[0], self.start[1], radius, self.canvas, self.cl)
        elif self.current_algorithm == "ellipse_midpoint":
            if self.start:
                rx = abs(self.start[0] - event.x)
                ry = abs(self.start[1] - event.y)
                ellipse_midpoint(self.start[0], self.start[1], rx, ry, self.canvas, self.cl)

        self.canvas.unbind('<Motion>')
        self.start = None


    def onTriangleClick(self, event):
        self.triangle_points.append((event.x, event.y))
        if len(self.triangle_points) == 3:
            self.canvas.create_polygon(self.triangle_points, outline=self.cl, fill='')
            self.triangle_points = []

    def onFillStart(self, event=None):
        self.canvas.unbind('<Motion>')
        boundary_color = "#ffffff"
        boundary_fill(self.canvas, event.x, event.y, self.cl, boundary_color)

    def onFloodFillStart(self, event=None):
        self.canvas.unbind('<Motion>')
        x, y = event.x, event.y
        self.flood_fill(x, y, self.cl)

    def translate_mode(self):
        self.current_algorithm = "translate"
        self.canvas.bind('<ButtonPress-1>', self.onTranslate)
        self.update_status("Translation Mode")

    def rotate_mode(self):
        self.current_algorithm = "rotate"
        self.canvas.bind('<ButtonPress-1>', self.onRotate)
        self.update_status("Rotation Mode")

    def scale_mode(self):
        self.current_algorithm = "scale"
        self.canvas.bind('<ButtonPress-1>', self.onScale)
        self.update_status("Scaling Mode")

    def reflect_mode(self):
        self.current_algorithm = "reflect"
        self.canvas.bind('<ButtonPress-1>', self.onReflect)
        self.update_status("Reflection Mode")

    def onTranslate(self, event):
        dx = simpledialog.askinteger("Input", "Enter translation distance for X:")
        dy = simpledialog.askinteger("Input", "Enter translation distance for Y:")
        if dx is not None and dy is not None:
            items = self.canvas.find_all()
            for item in items:
                self.canvas.move(item, dx, dy)

    def onRotate(self, event):
        angle = simpledialog.askfloat("Input", "Enter rotation angle (in degrees):")
        if angle is not None:
            items = self.canvas.find_all()
            for item in items:
                coords = self.canvas.coords(item)
                if len(coords) >= 4:
                    cx = sum(coords[::2]) / len(coords[::2])
                    cy = sum(coords[1::2]) / len(coords[1::2])
                    new_coords = []
                    for i in range(0, len(coords), 2):
                        x, y = coords[i], coords[i+1]
                        x_new = cx + math.cos(math.radians(angle)) * (x - cx) - math.sin(math.radians(angle)) * (y - cy)
                        y_new = cy + math.sin(math.radians(angle)) * (x - cx) + math.cos(math.radians(angle)) * (y - cy)
                        new_coords.extend([x_new, y_new])
                    self.canvas.coords(item, new_coords)

    def onScale(self, event):
        sx = simpledialog.askfloat("Input", "Enter scaling factor for X:")
        sy = simpledialog.askfloat("Input", "Enter scaling factor for Y:")
        if sx is not None and sy is not None:
            items = self.canvas.find_all()
            for item in items:
                coords = self.canvas.coords(item)
                if len(coords) >= 4:
                    cx = sum(coords[::2]) / len(coords[::2])
                    cy = sum(coords[1::2]) / len(coords[1::2])
                    new_coords = []
                    for i in range(0, len(coords), 2):
                        x, y = coords[i], coords[i+1]
                        x_new = cx + sx * (x - cx)
                        y_new = cy + sy * (y - cy)
                        new_coords.extend([x_new, y_new])
                    self.canvas.coords(item, new_coords)

    def onReflect(self, event):
        axis = simpledialog.askstring("Input", "Enter reflection axis (x or y):")
        if axis is not None:
            items = self.canvas.find_all()
            for item in items:
                coords = self.canvas.coords(item)
                if len(coords) >= 4:
                    cx = sum(coords[::2]) / len(coords[::2])
                    cy = sum(coords[1::2]) / len(coords[1::2])
                    new_coords = []
                    if axis == 'x':
                        for i in range(0, len(coords), 2):
                            x, y = coords[i], coords[i+1]
                            y_new = cy - (y - cy)
                            new_coords.extend([x, y_new])
                    elif axis == 'y':
                        for i in range(0, len(coords), 2):
                            x, y = coords[i], coords[i+1]
                            x_new = cx - (x - cx)
                            new_coords.extend([x_new, y])
                    self.canvas.coords(item, new_coords)

    def update_status(self, message):
        self.status.config(text=message)

    def boundary_fill_mode(self):
        self.canvas.bind('<ButtonPress-1>', self.onFillStart)
        self.update_status("Boundary Fill Mode")

    def flood_fill_mode(self):
        self.current_algorithm = "flood_fill"
        self.canvas.bind('<ButtonPress-1>', self.onFloodFillStart)
        self.update_status("Flood Fill Mode")

def line_bresenham(x1, y1, x2, y2, canvas, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        canvas.create_line(x1, y1, x1+1, y1, fill=color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def line_dda(x1, y1, x2, y2, canvas, color):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1
    for _ in range(steps + 1):
        canvas.create_line(round(x), round(y), round(x) + 1, round(y), fill=color)
        x += x_inc
        y += y_inc

def circle_midpoint(xc, yc, r, canvas, color):
    x = 0
    y = r
    p = 1 - r
    while x <= y:
        canvas.create_line(xc + x, yc + y, xc + x + 1, yc + y, fill=color)
        canvas.create_line(xc - x, yc + y, xc - x + 1, yc + y, fill=color)
        canvas.create_line(xc + x, yc - y, xc + x + 1, yc - y, fill=color)
        canvas.create_line(xc - x, yc - y, xc - x + 1, yc - y, fill=color)
        canvas.create_line(xc + y, yc + x, xc + y + 1, yc + x, fill=color)
        canvas.create_line(xc - y, yc + x, xc - y + 1, yc + x, fill=color)
        canvas.create_line(xc + y, yc - x, xc + y + 1, yc - x, fill=color)
        canvas.create_line(xc - y, yc - x, xc - y + 1, yc - x, fill=color)
        if p < 0:
            p += 2 * x + 3
        else:
            p += 2 * (x - y) + 5
            y -= 1
        x += 1

def ellipse_midpoint(xc, yc, rx, ry, canvas, color):
    x = 0
    y = ry
    p1 = ry**2 - rx**2 * ry + rx**2 / 4
    while 2 * ry**2 * x <= 2 * rx**2 * y:
        canvas.create_line(xc + x, yc + y, xc + x + 1, yc + y, fill=color)
        canvas.create_line(xc - x, yc + y, xc - x + 1, yc + y, fill=color)
        canvas.create_line(xc + x, yc - y, xc + x + 1, yc - y, fill=color)
        canvas.create_line(xc - x, yc - y, xc - x + 1, yc - y, fill=color)
        if p1 < 0:
            x += 1
            p1 += 2 * ry**2 * x + ry**2
        else:
            x += 1
            y -= 1
            p1 += 2 * ry**2 * x - 2 * rx**2 * y + ry**2
    p2 = ry**2 * (x + 0.5)**2 + rx**2 * (y - 1)**2 - rx**2 * ry**2
    while y >= 0:
        canvas.create_line(xc + x, yc + y, xc + x + 1, yc + y, fill=color)
        canvas.create_line(xc - x, yc + y, xc - x + 1, yc + y, fill=color)
        canvas.create_line(xc + x, yc - y, xc + x + 1, yc - y, fill=color)
        canvas.create_line(xc - x, yc - y, xc - x + 1, yc - y, fill=color)
        if p2 > 0:
            y -= 1
            p2 -= 2 * rx**2 * y + rx**2
        else:
            y -= 1
            x += 1
            p2 += 2 * ry**2 * x - 2 * rx**2 * y + rx**2

def boundary_fill(canvas, x, y, fill_color, boundary_color):
    # Ambil warna latar belakang canvas dalam format yang dapat dikenali Tkinter
    bg_color = canvas["bg"]

    # Cek apakah warna latar belakang valid
    try:
        bg_rgb = canvas.winfo_rgb(bg_color)[:3]
    except:
        # Jika tidak valid, atur warna latar belakang ke putih
        bg_rgb = (255, 255, 255)

    # Ambil warna piksel awal pada titik (x, y)
    pixel_color = canvas.winfo_rgb(canvas.itemcget(canvas.find_closest(x, y), "fill"))[:3]

    # Ubah warna fill dan boundary ke format RGB
    fill_rgb = canvas.winfo_rgb(fill_color)
    boundary_rgb = canvas.winfo_rgb(boundary_color)

    # Jika warna latar belakang atau warna batas adalah warna fill atau sama dengan warna piksel awal, keluar
    if pixel_color == fill_rgb or pixel_color == boundary_rgb:
        return

    # Buat antrian untuk operasi pengisian
    q = Queue()
    q.put((x, y))

    # Simpan titik yang telah diisi untuk menghindari pengisian berulang
    filled_points = set()

    # Loop sampai antrian kosong
    while not q.empty():
        x, y = q.get()
        
        # Jika titik sudah diisi sebelumnya, lanjutkan ke titik selanjutnya
        if (x, y) in filled_points:
            continue
        
        # Ambil warna piksel saat ini pada posisi (x, y)
        current_pixel_color = canvas.winfo_rgb(canvas.itemcget(canvas.find_closest(x, y), "fill"))[:3]

        # Jika warna piksel saat ini adalah warna piksel awal, ganti warna fill
        if current_pixel_color == pixel_color:
            canvas.create_line(x, y, x+1, y, fill=fill_color)
            
            # Tandai titik sebagai telah diisi
            filled_points.add((x, y))

            # Tambahkan tetangga yang belum diisi ke antrian
            if x + 1 < canvas.winfo_width():
                q.put((x + 1, y))
            if x - 1 >= 0:
                q.put((x - 1, y))
            if y + 1 < canvas.winfo_height():
                q.put((x, y + 1))
            if y - 1 >= 0:
                q.put((x, y - 1))

def flood_fill(self, x, y, new_color):
    def get_pixel_color(x, y):
        ids = self.canvas.find_overlapping(x, y, x, y)
        if ids:
            color = self.canvas.itemcget(ids[-1], "fill")
            return color if color else "white"
        return "white"

    def set_pixel_color(x, y, color):
        self.canvas.create_rectangle(x, y, x+1, y+1, outline=color, fill=color)

    target_color = get_pixel_color(x, y)
    if target_color == new_color:
        return

    q = Queue()
    q.put((x, y))
    while not q.empty():
        px, py = q.get()
        if get_pixel_color(px, py) == target_color:
            set_pixel_color(px, py, new_color)
            q.put((px + 1, py))
            q.put((px - 1, py))
            q.put((px, py + 1))
            q.put((px, py - 1))

if __name__ == "__main__":
    root = tk.Tk()
    cb = "#828181"  # Background color
    fillColor = "#000000"  # Fill color
    boundaryColor = "#000000"  # Boundary color
    gui = VektorDraw(root, cb)
    root.mainloop()
