import operator
from collections import Counter
import secrets
import os

import PIL.Image
import PIL.ImageOps
import numpy as np
from scipy.spatial import distance
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


def load_image_with_marks(path):
    _image = PIL.Image.open(path).convert('RGB')
    size = _image.size
    pixels = []
    for i in range(size[0]):
        col = []
        for j in range(size[1]):
            col.append([list(_image.getpixel((i, j))), False])
        pixels.append(col)
    return pixels, size[0], size[1]


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


def smooth_contours(path, threshold):
    _image, w, h = load_image_with_marks(path)
    pixel = 0
    visited = 1
    neighbours = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    for i, col in enumerate(_image):
        for j, value in enumerate(col):
            if not value[visited]:
                queue = [((i, j), value)]  # ((row, column), ((r, g, b), visited))
                target = [((i, j), value)]
                border = []

                while len(queue) != 0:
                    current = queue.pop(0)  # ((row, column), ((r, g, b), visited))
                    current[1][visited] = True

                    for neighbour in neighbours:
                        coord = tuple(map(operator.add, neighbour, current[0]))
                        if (-1 < coord[0] < w) and (-1 < coord[1] < h):
                            image_neighbour = _image[coord[0]][coord[1]]
                            if (not image_neighbour[visited]) and (image_neighbour[pixel] == current[1][pixel]):
                                if (coord, image_neighbour) not in target:
                                    queue.append((coord, image_neighbour))
                                    target.append((coord, image_neighbour))
                            if (image_neighbour[pixel] not in border) and (image_neighbour[pixel] != current[1][pixel]):
                                border.append(tuple(image_neighbour[pixel]))

                if len(target) < threshold and len(border) > 0:
                    c = Counter(border)
                    common = c.most_common(1)[0]
                    for p in target:
                        _image[p[0][0]][p[0][1]] = common
    for i, col in enumerate(_image):
        for j, value in enumerate(col):
            if len(_image[i][j]) == 2:
                _image[i][j] = _image[i][j][0]
    return _image


def draw_contours(_image: PIL.Image):
    border_color = (180, 180, 180)
    # default_color = (255, 255, 255)
    dist_threshold = 20
    width, height = _image.size
    for x in range(width - 2):
        for y in range(height - 2):
            if _image.getpixel((x, y)) != border_color:
                if (distance.euclidean(_image.getpixel((x, y)), _image.getpixel((x + 1, y))) >= dist_threshold) or \
                        (distance.euclidean(_image.getpixel((x, y)), _image.getpixel((x, y + 1))) >= dist_threshold):
                    _image.putpixel((x, y), border_color)
                # else:
                #     _image.putpixel((x, y), default_color)
    return _image


def recreate_image(_codebook, _labels, _w, _h, size, contour, smoothing, save_path):
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
    new_image.save(save_path)

    if smoothing != 0 and size == -1:
        new_image = smooth_contours(save_path, smoothing)
        new_image = np.array(new_image, dtype=np.uint8)
        new_image = PIL.ImageOps.mirror(PIL.Image.fromarray(new_image).rotate(-90, expand=True))

        if contour:
            new_image = draw_contours(new_image)
    new_image.save(save_path)


def fit(shape, size):
    return shape[0] % size == 0 and shape[1] % size == 0


def reduce(n, path, centers=None, rubik=False, size=-1, contour=True, smoothing=0, save_path=None):

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
    recreate_image(centers, labels, w, h, size, contour, smoothing, save_path)



def get_hash():
    return secrets.token_hex(nbytes=16)


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


def wrong_parameters(n, size, smoothing, hash_name):
    if n < 2 or n > 128:
        return True

    if size < 1 or size > 100:
        return True

    if smoothing < 0 or smoothing > 100:
        return True

    if hash_name == '' or hash_name is None:
        return True

    return False
