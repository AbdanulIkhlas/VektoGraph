import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import ImageGrab
import math
from queue import Queue


class CanvasEventsDemo:
    def __init__(self, root, cb, parent=None):
        self.canvas = tk.Canvas(root, height=600, width=800, bg=cb)
        self.canvas.grid(row=2, column=0, columnspan=2000)
        self.cl = "black"
        self.current_algorithm = None
        self.temp_shape = None
        self.start = None
        self.triangle_points = []
        self.transform_item = None

        # Menu
        menu = tk.Menu(root)
        root.config(menu=menu)

        shape_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Shapes", menu=shape_menu)
        shape_menu.add_command(label="Bresenham Line", command=self.line_bresenham_mode)
        shape_menu.add_command(label="DDA Line", command=self.line_dda_mode)
        shape_menu.add_command(label="Midpoint Circle", command=self.circle_midpoint_mode)
        shape_menu.add_command(label="Midpoint Ellipse", command=self.ellipse_midpoint_mode)
        shape_menu.add_command(label="Triangle", command=self.triangle_mode)

        color_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Color", menu=color_menu)
        color_menu.add_command(label="Choose Color", command=self.choose_color)
        color_menu.add_command(label="Background", command=self.choose_bg_color)

        save_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Save", menu=save_menu)
        save_menu.add_command(label="Save Image", command=self.save_image)

        transform_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Transform", menu=transform_menu)
        transform_menu.add_command(label="Translate", command=self.translate_mode)
        transform_menu.add_command(label="Rotate", command=self.rotate_mode)
        transform_menu.add_command(label="Scale", command=self.scale_mode)
        transform_menu.add_command(label="Reflect", command=self.reflect_mode)

        fill_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Fill", menu=fill_menu)
        fill_menu.add_command(label="Boundary Fill", command=self.onFillStart)

        self.drawn = None
        self.root = root

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

    def circle_midpoint_mode(self):
        self.current_algorithm = "circle_midpoint"
        self.bind_canvas_events()

    def ellipse_midpoint_mode(self):
        self.current_algorithm = "ellipse_midpoint"
        self.bind_canvas_events()

    def line_dda_mode(self):
        self.current_algorithm = "line_dda"
        self.bind_canvas_events()

    def triangle_mode(self):
        self.current_algorithm = "triangle"
        self.canvas.bind('<ButtonPress-1>', self.onTriangleClick)

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
            line_bresenham(self.start[0], self.start[1], event.x, event.y, self.canvas, self.cl)
        elif self.current_algorithm == "line_dda":
            line_dda(self.start[0], self.start[1], event.x, event.y, self.canvas, self.cl)
        elif self.current_algorithm == "circle_midpoint":
            radius = int(((self.start[0] - event.x) ** 2 + (self.start[1] - event.y) ** 2) ** 0.5)
            circle_midpoint(self.start[0], self.start[1], radius, self.canvas, self.cl)
        elif self.current_algorithm == "ellipse_midpoint":
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

    def onFillStart(self, event=None):  # Menambahkan argumen event=None
        self.canvas.unbind('<Motion>')
        boundary_color = "#000000"  # Ganti dengan warna batas yang sesuai
        boundary_fill(self.canvas, event.x, event.y, self.cl, boundary_color)

    def translate_mode(self):
        self.current_algorithm = "translate"
        self.canvas.bind('<ButtonPress-1>', self.onTranslate)

    def rotate_mode(self):
        self.current_algorithm = "rotate"
        self.canvas.bind('<ButtonPress-1>', self.onRotate)

    def scale_mode(self):
        self.current_algorithm = "scale"
        self.canvas.bind('<ButtonPress-1>', self.onScale)

    def reflect_mode(self):
        self.current_algorithm = "reflect"
        self.canvas.bind('<ButtonPress-1>', self.onReflect)

    def onTranslate(self, event):
        dx = simpledialog.askinteger("Input", "Enter translation distance for X:")
        dy = simpledialog.askinteger("Input", "Enter translation distance for Y:")
        if dx is not None and dy is not None:
            self.canvas.move("all", dx, dy)
    
    def boundary_fill_mode(self):
        self.current_algorithm = "boundary_fill"
        self.canvas.bind('<ButtonPress-1>', self.onFillStart)

    def onRotate(self, event):
        item = self.get_item_at(event.x, event.y)
        if item:
            angle = simpledialog.askinteger("Input", "Enter rotation angle:")
            if angle is not None:
                self.rotate(item, angle)

    def onScale(self, event):
        item = self.get_item_at(event.x, event.y)
        if item:
            sx = simpledialog.askfloat("Input", "Enter scale factor for X:")
            sy = simpledialog.askfloat("Input", "Enter scale factor for Y:")
            if sx is not None and sy is not None:
                self.scale(item, sx, sy)

    def onReflect(self, event):
        item = self.get_item_at(event.x, event.y)
        if item:
            axis = simpledialog.askstring("Input", "Enter reflection axis (x or y):")
            if axis in ('x', 'y'):
                self.reflect(item, axis)

    def get_item_at(self, x, y):
        items = self.canvas.find_closest(x, y)
        return items[0] if items else None

    def rotate(self, item, angle):
        angle = math.radians(angle)
        coords = self.canvas.coords(item)
        cx, cy = self.get_center(coords)
        new_coords = []
        for i in range(0, len(coords), 2):
            x = coords[i] - cx
            y = coords[i + 1] - cy
            new_x = cx + (x * math.cos(angle) - y * math.sin(angle))
            new_y = cy + (x * math.sin(angle) + y * math.cos(angle))
            new_coords.extend([new_x, new_y])
        self.canvas.coords(item, *new_coords)

    def scale(self, item, sx, sy):
        coords = self.canvas.coords(item)
        cx, cy = self.get_center(coords)
        new_coords = []
        for i in range(0, len(coords), 2):
            x = coords[i] - cx
            y = coords[i + 1] - cy
            new_x = cx + (x * sx)
            new_y = cy + (y * sy)
            new_coords.extend([new_x, new_y])
        self.canvas.coords(item, *new_coords)

    def reflect(self, item, axis):
        coords = self.canvas.coords(item)
        cx, cy = self.get_center(coords)
        new_coords = []
        for i in range(0, len(coords), 2):
            x = coords[i] - cx
            y = coords[i + 1] - cy
            if axis == 'x':
                new_x = cx + x
                new_y = cy - y
            elif axis == 'y':
                new_x = cx - x
                new_y = cy + y
            new_coords.extend([new_x, new_y])
        self.canvas.coords(item, *new_coords)

    def get_center(self, coords):
        x_coords = coords[::2]
        y_coords = coords[1::2]
        cx = sum(x_coords) / len(x_coords)
        cy = sum(y_coords) / len(y_coords)
        return cx, cy


def line_bresenham(xa, ya, xb, yb, canvas, color):
    dx = abs(xb - xa)
    dy = abs(yb - ya)
    sx = 1 if xa < xb else -1
    sy = 1 if ya < yb else -1
    err = dx - dy
    while True:
        canvas.create_line(xa, ya, xa + 1, ya, fill=color)
        if xa == xb and ya == yb:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            xa += sx
        if e2 < dx:
            err += dx
            ya += sy


def line_dda(x1, y1, x2, y2, canvas, color):
    dx = x2 - x1
    dy = y2 - y1
    steps = abs(dx) if abs(dx) > abs(dy) else abs(dy)
    x_inc = dx / float(steps)
    y_inc = dy / float(steps)
    x = x1
    y = y1
    for _ in range(steps):
        canvas.create_line(round(x), round(y), round(x) + 1, round(y), fill=color)
        x += x_inc
        y += y_inc


def circle_midpoint(x_center, y_center, radius, canvas, color):
    x = 0
    y = radius
    p = 1 - radius

    def plot_circle_points(xc, yc, x, y):
        points = [
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ]
        for point in points:
            canvas.create_line(point[0], point[1], point[0] + 1, point[1], fill=color)

    plot_circle_points(x_center, y_center, x, y)
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        plot_circle_points(x_center, y_center, x, y)


def ellipse_midpoint(x_center, y_center, rx, ry, canvas, color):
    x = 0
    y = ry
    rx_sq = rx * rx
    ry_sq = ry * ry

    two_rx_sq = 2 * rx_sq
    two_ry_sq = 2 * ry_sq
    px = 0
    py = two_rx_sq * y

    def plot_ellipse_points(xc, yc, x, y):
        points = [
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y)
        ]
        for point in points:
            canvas.create_line(point[0], point[1], point[0] + 1, point[1], fill=color)

    p1 = ry_sq - (rx_sq * ry) + (0.25 * rx_sq)
    plot_ellipse_points(x_center, y_center, x, y)
    while px < py:
        x += 1
        px += two_ry_sq
        if p1 < 0:
            p1 += ry_sq + px
        else:
            y -= 1
            py -= two_rx_sq
            p1 += ry_sq + px - py
        plot_ellipse_points(x_center, y_center, x, y)

    p2 = (ry_sq * (x + 0.5) ** 2) + (rx_sq * (y - 1) ** 2) - (rx_sq * ry_sq)
    while y > 0:
        y -= 1
        py -= two_rx_sq
        if p2 > 0:
            p2 += rx_sq - py
        else:
            x += 1
            px += two_ry_sq
            p2 += rx_sq - py + px
        plot_ellipse_points(x_center, y_center, x, y)


def boundary_fill(canvas, x, y, fill_color, boundary_color):
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    def get_pixel_color(x, y):
        x_root = canvas.winfo_rootx() + x
        y_root = canvas.winfo_rooty() + y
        image = ImageGrab.grab((x_root, y_root, x_root + 1, y_root + 1))
        rgb = image.getpixel((0, 0))
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def set_pixel_color(x, y, color):
        if 0 <= x < width and 0 <= y < height:
            canvas.create_line(x, y, x + 1, y, fill=color)

    def is_boundary_color(x, y):
        return get_pixel_color(x, y) == boundary_color

    def is_fill_color(x, y):
        return get_pixel_color(x, y) == fill_color

    def boundary_fill_util(x, y):
        if not is_boundary_color(x, y) and not is_fill_color(x, y):
            set_pixel_color(x, y, fill_color)
            boundary_fill_util(x + 1, y)
            boundary_fill_util(x - 1, y)
            boundary_fill_util(x, y + 1)
            boundary_fill_util(x, y - 1)

    boundary_fill_util(x, y)


if __name__ == "__main__":
    r = tk.Tk()
    cb = "white"
    app = CanvasEventsDemo(r, cb)
    r.title("VEKTOR DRAW")
    r.mainloop()

