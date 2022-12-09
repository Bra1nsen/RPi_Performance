import numpy as np
import matplotlib.pyplot as plt
import cv2


arr = np.load("cmap.npy")
r = arr[:,:, 0]
g = arr[:,:, 1]
b = arr[:,:, 2]
a = arr[:,:, 3]

plt.imshow(r)
plt.show()
plt.imshow(g)
plt.show()
plt.imshow(b)
plt.show()


'''x=np.load("cmap.npy")

print(x.shape)

print(np.max(x))
print(np.min(x))
print(x)
plt.imshow(x)
plt.legend()
plt.show()









y=np.load("hdr.npy")

print(y.shape)

print(np.max(y))
print(np.min(y))

plt.imshow(y)
plt.show()'''