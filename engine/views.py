from django.shortcuts import render, HttpResponse
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes
# Create your views here.


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def api(request):

	return HttpResponse('asdf')
