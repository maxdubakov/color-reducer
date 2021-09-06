from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from reducer.util import reduce as reduction_func, hex_to_rgb
from reducer.util import get_hash, remove_file


# Create your views here.


def get_centers(request):
    raw_centers = request.GET.getlist('centers', None)
    centers = None
    for color in raw_centers:
        if centers is None:
            centers = []
        color = str(color).replace('#', '')
        if len(color) == 3:
            color *= 2
        centers.append(hex_to_rgb(color))
    return centers


def get_bool(value):
    return False if value == 'false' else True


def store_file(file, _format):
    hash_name = get_hash()
    with open(f'images/{hash_name}.{_format}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    with open(f'images/{hash_name}_copy.{_format}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    with open(f'images/.{hash_name}', 'w+') as meta:
        meta.write(_format)

    return hash_name


def upload(request):
    file = request.FILES['image']

    _format = str(file).split('.')[-1]
    hash_name = store_file(file, _format)
    resp = JsonResponse({'hash_name': hash_name})
    return resp


def reduce(request):
    n = int(request.GET.get('n'))
    rubik = get_bool(request.GET.get('rubik'))
    size = int(request.GET.get('size'))
    contour = get_bool(request.GET.get('contour'))
    smoothing = int(request.GET.get('smoothing'))
    hash_name = str(request.GET.get('image'))
    centers = get_centers(request)

    meta_path = f'images/.{hash_name}'

    with open(meta_path, 'r') as meta:
        _format = str(meta.read()).replace('\n', '')

    file_path = f'images/{hash_name}_copy.{_format}'
    save_path = f'images/{hash_name}_converted.png'

    reduction_func(n, file_path, centers, rubik, size, contour, smoothing, save_path)

    with open(save_path, 'rb') as root:
        file_data = root.read()

    # remove_file(meta_path)
    # remove_file(file_path)
    # remove_file(save_path)

    response = HttpResponse(file_data, content_type='application/image/png')
    response['Content-Disposition'] = 'attachment; filename="converted.png"'
    return response


def csrf(request):
    return JsonResponse({})
