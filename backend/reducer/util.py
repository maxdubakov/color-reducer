import PIL.Image
import PIL.ImageOps
import numpy as np
from sklearn.utils import shuffle
from sklearn.cluster import KMeans


def hex_to_rgb(val):
    return list(int(val[i:i+2], 16) for i in (0, 2, 4))


def load_image(path):
    _image = PIL.Image.open(path).convert('RGB')
    size = _image.size
    pixels = []
    for i in range(size[0]):
        row = []
        for j in range(size[1]):
            row.append(list(_image.getpixel((i, j))))
        pixels.append(row)
    return np.array(pixels)


def get_labels(n, image, centers):
    w, h, d = tuple(image.shape)

    image_array = np.reshape(image, (w * h, d))
    image_array_sample = shuffle(image_array)[:10000]

    kmeans = KMeans(n_clusters=n).fit(image_array_sample)
    if centers is not None:
        kmeans.cluster_centers_ = centers

    labels = kmeans.predict(image_array)
    return kmeans.cluster_centers_, labels, w, h

def recreate_image(_codebook, _labels, _w, _h):
    _d = _codebook.shape[1]
    _image = np.zeros((_w, _h, _d), dtype=np.uint8)
    label_idx = 0
    for i in range(_w):
        for j in range(_h):
            _image[i][j] = [int(c) for c in _codebook[_labels[label_idx]]]
            label_idx += 1

    new_image = PIL.ImageOps.mirror(PIL.Image.fromarray(_image).rotate(-90, expand=True))
    new_image.save('temp/converted.png')


def reduce(n, path, centers=None):
    image = load_image(path)
    if centers is not None:
        n = len(centers)
        centers = np.array(centers, dtype=np.float)
    centers, labels, w, h = get_labels(n, image, centers)
    recreate_image(centers, labels, w, h)
