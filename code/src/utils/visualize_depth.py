import cv2
import matplotlib.pyplot as plt
import numpy as np

img_bgr = cv2.imread(r"C:\Users\EMC\Downloads\JackJackL515Bag\color\00438.jpg")

depth = cv2.imread(r"C:\Users\EMC\Downloads\JackJackL515Bag\depth\00438.png", cv2.IMREAD_UNCHANGED)

depth_vis = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
depth_vis = np.uint8(depth_vis)

colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_INFERNO)
cv2.imwrite("depth_colormapped.png", colored)

print("Min:", depth_vis.min(), "Max:", depth_vis.max())

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Imagem BGR")
plt.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Imagem de Profundidade")
plt.imshow(depth_vis)  # Ou 'gray', 'plasma', etc
plt.axis("off")

plt.tight_layout()
plt.show()
