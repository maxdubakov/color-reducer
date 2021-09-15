from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from reducer.util import reduce as reduction_func, hex_to_rgb
from reducer.util import get_hash, wrong_parameters


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
    with open(f'uploads/images/{hash_name}.{_format}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    with open(f'uploads/images/{hash_name}_copy.{_format}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    with open(f'uploads/images/.{hash_name}', 'w+') as meta:
        meta.write(_format)

    return hash_name

@csrf_exempt
def upload(request):
    file = request.FILES['image']

    _format = str(file).split('.')[-1]
    hash_name = store_file(file, _format)
    response = JsonResponse({'hash_name': hash_name})
    response['Access-Control-Allow-Origin'] = '*'
    return response


def reduce(request):
    try:
        n = int(request.GET.get('n'))
        rubik = get_bool(request.GET.get('rubik'))
        size = int(request.GET.get('size'))
        contour = get_bool(request.GET.get('contour'))
        smoothing = int(request.GET.get('smoothing'))
        hash_name = str(request.GET.get('image'))
        centers = get_centers(request)
    except Exception:
        response = HttpResponseBadRequest('Some parameters are not correct')
        response['Access-Control-Allow-Origin'] = '*'
        return response

    if wrong_parameters(n, size, smoothing, hash_name):
        response = HttpResponseBadRequest('Some parameters are not correct')
        response['Access-Control-Allow-Origin'] = '*'
        return response

    try:
        meta_path = f'uploads/images/.{hash_name}'

        with open(meta_path, 'r') as meta:
            _format = str(meta.read()).replace('\n', '')

        file_path = f'uploads/images/{hash_name}_copy.{_format}'
        save_path = f'uploads/images/{hash_name}_converted.png'

        reduction_func(n, file_path, centers, rubik, size, contour, smoothing, save_path)

        with open(save_path, 'rb') as root:
            file_data = root.read()

        # remove_file(meta_path)
        # remove_file(file_path)
        # remove_file(save_path)

        response = HttpResponse(file_data, content_type='application/image/png')
        response['Content-Disposition'] = 'attachment; filename="converted.png"'
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except:
        response = HttpResponseBadRequest('Something went wrong')
        response['Access-Control-Allow-Origin'] = '*'
        return response



def csrf(request):
    response = HttpResponse('{}')
    response['Access-Control-Allow-Origin'] = '*'
    return response
