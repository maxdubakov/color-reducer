from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from reducer.util import reduce as reduction_func, hex_to_rgb

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


def store_file(file, _format):
    with open(f'temp/image.{_format}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    with open(f'temp/.meta', 'w+') as meta:
        meta.write(_format)


@csrf_exempt
def upload(request):
    file = request.FILES['image']


    _format = str(file).split('.')[-1]
    store_file(file, _format)
    resp = HttpResponse()
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def reduce(request):
    n = int(request.GET.get('n'))
    centers = get_centers(request)

    with open('temp/.meta', 'r') as meta:
        _format = str(meta.read()).replace('\n', '')

    reduction_func(n, f'temp/image.{_format}', centers)

    with open(f'temp/converted.png', 'rb') as root:
        file_data = root.read()

    response = HttpResponse(file_data, content_type='application/image/png')
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Disposition'] = 'attachment; filename="converted.png"'
    return response