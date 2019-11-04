from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views import View
from zerotocareer.database import users

from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes
from zerotocareer.common_classes import JSONOpenAPIRender


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def default_view(request):

    if not request.user.is_authenticated:
        redirect('/accounts/login')

    return HttpResponse(
        'This is the main page. <br>'
        'Login page at /accounts/login <br>'
        'Signup page at /accounts/sign_up <br>'
        'Logout page at /accounts/logout <br>'
        'Swagger page at /swagger <br>'
    )


class MySignUpView(View):
    form_class = UserCreationForm
    template_name = 'accounts/sign_up.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():
            # <process form cleaned data>

            print('Email Is:', request.POST.get('email'))

            users.insert_one({
                'user_id': form.cleaned_data.get('username'),
                'email_id': request.POST.get('email'),
                'flows': [],
            })
            print('Created a new User', form.cleaned_data.get('username'))
            u = User.objects.create_user(
                    form.cleaned_data.get('username'),
                    '',  # request.POST['email'],
                    form.cleaned_data.get('password1'),
                    is_active=True
            )
            return HttpResponseRedirect('/accounts/login/?next=/accounts/profile')

        return render(request, self.template_name, {'form': form})


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def profile(request):

    """

    :param request: django request
    :return:
    """

    if not request.user.is_authenticated:
        return redirect('/accounts/login')

    return redirect('/')
