import matplotlib.pyplot as plt
import numpy as np

def boundary_fill(x, y, fill_color, boundary_color):
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if img[y, x] != boundary_color and img[y, x] != fill_color:
            img[y, x] = fill_color
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

# Ukuran gambar
width = 20
height = 20

# Inisialisasi gambar dengan warna putih (255) pada setiap piksel
img = 255 * np.ones((height, width), dtype=np.uint8)

# Koordinat kotak
x1, y1 = 5, 5
x2, y2 = 15, 15

# Menggambar kotak (garis tepi)
plt.plot([x1, x2], [y1, y1], color='yellow')
plt.plot([x2, x2], [y1, y2], color='yellow')
plt.plot([x1, x2], [y2, y2], color='yellow')
plt.plot([x1, x1], [y1, y2], color='yellow')

# Mengisi area kotak dengan algoritma boundary-fill
boundary_fill(x1 + 1, y1 + 1, fill_color=200, boundary_color=255)  # Mengubah fill_color menjadi 200

# Menampilkan gambar
plt.imshow(img, cmap='gray', origin='lower')
plt.title('Kotak dengan Algoritma Boundary Fill (Warna Kuning)')
plt.show()
