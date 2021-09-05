import copy
import operator
from datetime import datetime
import pickle

import PIL.Image
import PIL.ImageOps
import numpy as np
from sklearn.utils import shuffle
from sklearn.cluster import KMeans


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


def get_labels(n, image):
    w, h, d = tuple(image.shape)

    image_array = np.reshape(image, (w * h, d))
    image_array_sample = shuffle(image_array)[:10000]

    kmeans = KMeans(n_clusters=n).fit(image_array_sample)
    labels = kmeans.predict(image_array)
    return kmeans.cluster_centers_, labels, w, h


""" NEW """
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


def smooth_contours(path):
    _image, w, h = load_image_with_marks(path)
    pixel = 0
    visited = 1
    neighbours = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    processed = 0
    threshold = 50
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
                            if not image_neighbour[visited]:
                                if image_neighbour[pixel] == current[1][pixel]:
                                    if (coord, image_neighbour) not in target:
                                        queue.append((coord, image_neighbour))
                                        target.append((coord, image_neighbour))
                                else:
                                    border.append((coord, image_neighbour))

                # if len(target) < threshold and len(border) > 0:
                print('Replacing!')
                for p in border:
                    _image[p[0][0]][p[0][1]] = [0, 0, 0]
                target_image = copy.deepcopy(_image)
                for p in target:
                    target_image[p[0][0]][p[0][1]] = [0, 0, 0]
                for i, col in enumerate(_image):
                    for j, value in enumerate(col):
                        if len(_image[i][j]) == 2:
                            _image[i][j] = _image[i][j][0]
                        if len(target_image[i][j]) == 2:
                            target_image[i][j] = target_image[i][j][0]
                return _image, target_image
    #         processed += 1
    #         print(f'Processed: {processed}/{w*h}')
    # for i, col in enumerate(_image):
    #     for j, value in enumerate(col):
    #         if len(_image[i][j]) == 2:
    #             _image[i][j] = _image[i][j][0]
    # return _image


def recreate_image(_codebook, _labels, _w, _h):
    _d = _codebook.shape[1]
    _image = np.zeros((_w, _h, _d), dtype=np.uint8)
    label_idx = 0
    for i in range(_w):
        for j in range(_h):
            _image[i][j] = [int(c) for c in _codebook[_labels[label_idx]]]
            label_idx += 1

    new_image = PIL.ImageOps.mirror(PIL.Image.fromarray(_image).rotate(-90, expand=True))
    new_image.save(f'/Users/max/Documents/Programming/web_development/Projects/ColorReducer/backend/temp/converted.png')


def reduce(n, path):
    image = load_image(path)
    centers, labels, w, h = get_labels(n, image)
    recreate_image(centers, labels, w, h)

before = datetime.now()
border_image, target_image = np.array(smooth_contours('../temp/test.png'), dtype=np.uint8)
after = datetime.now()
print(f'Overall Time: {(after - before).total_seconds()}s')

# with open('./pickled.pkl', 'rb') as f:
#     image = pickle.load(f)

border_image = np.array(border_image, dtype=np.uint8)
border_image = PIL.ImageOps.mirror(PIL.Image.fromarray(border_image).rotate(-90, expand=True))
border_image.save(f'/Users/max/Documents/Programming/web_development/Projects/ColorReducer/backend/temp/border.png')

target_image = np.array(target_image, dtype=np.uint8)

target_image = PIL.ImageOps.mirror(PIL.Image.fromarray(target_image).rotate(-90, expand=True))
target_image.save(f'/Users/max/Documents/Programming/web_development/Projects/ColorReducer/backend/temp/target.png')

