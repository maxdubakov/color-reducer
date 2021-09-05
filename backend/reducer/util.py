import PIL.Image
import PIL.ImageOps
import numpy as np
from sklearn.utils import shuffle
from sklearn.cluster import KMeans


def crop_image(path, size):
    w, h = get_image_size(path)

    crop_size_x = w % size
    crop_size_y = h % size

    l1 = crop_size_x // 2
    l2 = crop_size_y // 2
    r1 = crop_size_x - l1
    r2 = crop_size_y - l2

    image = PIL.Image.open(path).crop((l1, l2, w-r1, h-r2))
    image.save(path)

def hex_to_rgb(val):
    return list(int(val[i:i + 2], 16) for i in (0, 2, 4))


def get_image_size(path):
    _image = PIL.Image.open(path).convert('RGB')
    return _image.size


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


def add_colors(c1, c2):
    if len(c1) != len(c2):
        return
    _sum = []
    for i, j in zip(c1, c2):
        _sum.append(i + j)
    return _sum


def get_avg_colors(_image, size: int):
    _w, _h, _d = _image.shape
    avg_colored_image = np.zeros((_w, _h, _d), dtype=np.uint8)

    for i in range(0, _w, size):
        for j in range(0, _h, size):
            avg_color = [0, 0, 0]
            no_of_colors = 0

            for ik in range(i, i + size):
                for jk in range(j, j + size):
                    avg_color = add_colors(avg_color, list(_image[ik][jk]))
                    no_of_colors += 1
            avg_color = tuple([i / no_of_colors for i in avg_color])
            for ik in range(i, i + size):
                for jk in range(j, j + size):
                    avg_colored_image[ik][jk] = avg_color
    return avg_colored_image


def get_labels(n, image, centers):
    w, h, d = tuple(image.shape)

    image_array = np.reshape(image, (w * h, d))
    image_array_sample = shuffle(image_array)[:10000]

    kmeans = KMeans(n_clusters=n).fit(image_array_sample)
    if centers is not None:
        kmeans.cluster_centers_ = centers

    labels = kmeans.predict(image_array)
    return kmeans.cluster_centers_, labels, w, h


def recreate_image(_codebook, _labels, _w, _h, size, contour, name):
    _d = _codebook.shape[1]
    _image = np.zeros((_w, _h, _d), dtype=np.uint8)
    label_idx = 0
    for i in range(_w):
        for j in range(_h):
            if contour and size != -1 and (i % size == 0 or j % size == 0):
                _image[i][j] = [0, 0, 0]
            else:
                _image[i][j] = [int(c) for c in _codebook[_labels[label_idx]]]
            label_idx += 1

    new_image = PIL.ImageOps.mirror(PIL.Image.fromarray(_image).rotate(-90, expand=True))
    new_image.save(f'/Users/max/Documents/Programming/web_development/Projects/ColorReducer/backend/temp/{name}.png')


def fit(shape, size):
    return shape[0] % size == 0 and shape[1] % size == 0


def reduce(n, path, centers=None, rubik=False, size=-1, contour=True, name='converted'):
    if rubik:
        crop_image(path, size)

    image = load_image(path)

    if rubik and (not fit(image.shape, size)):
        print('Bad params')
        return

    if rubik:
        image = get_avg_colors(image, size)
    else:
        size = -1

    if centers is not None:
        n = len(centers)
        centers = np.array(centers, dtype=np.float)

    centers, labels, w, h = get_labels(n, image, centers)
    recreate_image(centers, labels, w, h, size, contour, name)
