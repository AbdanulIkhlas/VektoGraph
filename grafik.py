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
            "save_image": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "line_bresenham": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "line_dda": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "circle_midpoint": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "ellipse_midpoint": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "triangle": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "choose_color": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "background_color": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "translate": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "rotate": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "scale": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "reflect": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "boundary_fill": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
            "flood_fill": ImageTk.PhotoImage(Image.open("icons/line-dda.png")),
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
            x1, y1 = self.triangle_points[0]
            x2, y2 = self.triangle_points[1]
            x3, y3 = self.triangle_points[2]
            self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline=self.cl)
            self.triangle_points = []

    def translate_mode(self):
        self.update_status("Translate Transform Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_translate_start)
        self.canvas.bind('<ButtonRelease-1>', self.on_translate_end)

    def on_translate_start(self, event):
        self.start = (event.x, event.y)
        self.transform_item = self.canvas.find_closest(event.x, event.y)[0]

    def on_translate_end(self, event):
        if self.transform_item:
            dx = event.x - self.start[0]
            dy = event.y - self.start[1]
            self.canvas.move(self.transform_item, dx, dy)
        self.transform_item = None
        self.start = None

    def rotate_mode(self):
        self.update_status("Rotate Transform Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_rotate_start)
        self.canvas.bind('<ButtonRelease-1>', self.on_rotate_end)

    def on_rotate_start(self, event):
        self.start = (event.x, event.y)
        self.transform_item = self.canvas.find_closest(event.x, event.y)[0]

    def on_rotate_end(self, event):
        if self.transform_item:
            angle = simpledialog.askfloat("Input", "Enter angle (in degrees):", parent=self.root)
            if angle is not None:
                self.rotate_item(self.transform_item, angle, self.start)
        self.transform_item = None
        self.start = None

    def rotate_item(self, item, angle, center):
        coords = self.canvas.coords(item)
        angle = math.radians(angle)
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        cx, cy = center
        new_coords = []
        for i in range(0, len(coords), 2):
            x = coords[i] - cx
            y = coords[i + 1] - cy
            new_x = x * cos_val - y * sin_val + cx
            new_y = x * sin_val + y * cos_val + cy
            new_coords.extend([new_x, new_y])
        self.canvas.coords(item, *new_coords)

    def scale_mode(self):
        self.update_status("Scale Transform Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_scale_start)
        self.canvas.bind('<ButtonRelease-1>', self.on_scale_end)

    def on_scale_start(self, event):
        self.start = (event.x, event.y)
        self.transform_item = self.canvas.find_closest(event.x, event.y)[0]

    def on_scale_end(self, event):
        if self.transform_item:
            sx = simpledialog.askfloat("Input", "Enter scaling factor for x-axis:", parent=self.root)
            sy = simpledialog.askfloat("Input", "Enter scaling factor for y-axis:", parent=self.root)
            if sx is not None and sy is not None:
                self.scale_item(self.transform_item, sx, sy, self.start)
        self.transform_item = None
        self.start = None

    def scale_item(self, item, sx, sy, center):
        coords = self.canvas.coords(item)
        cx, cy = center
        new_coords = []
        for i in range(0, len(coords), 2):
            x = (coords[i] - cx) * sx + cx
            y = (coords[i + 1] - cy) * sy + cy
            new_coords.extend([x, y])
        self.canvas.coords(item, *new_coords)

    def reflect_mode(self):
        self.update_status("Reflect Transform Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_reflect_start)
        self.canvas.bind('<ButtonRelease-1>', self.on_reflect_end)

    def on_reflect_start(self, event):
        self.start = (event.x, event.y)
        self.transform_item = self.canvas.find_closest(event.x, event.y)[0]

    def on_reflect_end(self, event):
        if self.transform_item:
            axis = simpledialog.askstring("Input", "Enter axis to reflect (x or y):", parent=self.root)
            if axis in ("x", "y"):
                self.reflect_item(self.transform_item, axis, self.start)
        self.transform_item = None
        self.start = None

    def reflect_item(self, item, axis, center):
        coords = self.canvas.coords(item)
        cx, cy = center
        new_coords = []
        for i in range(0, len(coords), 2):
            if axis == "x":
                new_x = coords[i]
                new_y = 2 * cy - coords[i + 1]
            else:
                new_x = 2 * cx - coords[i]
                new_y = coords[i + 1]
            new_coords.extend([new_x, new_y])
        self.canvas.coords(item, *new_coords)

    def boundary_fill_mode(self):
        self.update_status("Boundary Fill Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_boundary_fill_start)

    def on_boundary_fill_start(self, event):
        boundary_color = self.cl
        fill_color = colorchooser.askcolor()[1]
        if fill_color:
            self.boundary_fill(event.x, event.y, boundary_color, fill_color)

    def boundary_fill(self, x, y, boundary_color, fill_color):
        stack = [(x, y)]
        while stack:
            x, y = stack.pop()
            current_color = self.canvas.winfo_rgb(self.canvas.gettags(self.canvas.find_closest(x, y)))
            if current_color != self.canvas.winfo_rgb(boundary_color) and current_color != self.canvas.winfo_rgb(fill_color):
                self.canvas.create_rectangle(x, y, x+1, y+1, outline=fill_color, fill=fill_color)
                stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

    def flood_fill_mode(self):
        self.update_status("Flood Fill Mode")
        self.canvas.bind('<ButtonPress-1>', self.on_flood_fill_start)

    def on_flood_fill_start(self, event):
        target_color = self.canvas.itemcget(self.canvas.find_closest(event.x, event.y), 'fill')
        replacement_color = colorchooser.askcolor()[1]
        if replacement_color:
            self.flood_fill(event.x, event.y, target_color, replacement_color)

    def flood_fill(self, x, y, target_color, replacement_color):
        if target_color == replacement_color:
            return
        q = Queue()
        q.put((x, y))
        while not q.empty():
            x, y = q.get()
            current_color = self.canvas.itemcget(self.canvas.find_closest(x, y), 'fill')
            if current_color == target_color:
                self.canvas.create_rectangle(x, y, x+1, y+1, outline=replacement_color, fill=replacement_color)
                q.put((x+1, y))
                q.put((x-1, y))
                q.put((x, y+1))
                q.put((x, y-1))

    def update_status(self, message):
        self.status.config(text=message)

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

if __name__ == "__main__":
    root = tk.Tk()
    cb = "#828181"  # Background color
    fillColor = "#000000"  # Fill color
    boundaryColor = "#000000"  # Boundary color
    gui = VektorDraw(root, cb)
    root.mainloop()
