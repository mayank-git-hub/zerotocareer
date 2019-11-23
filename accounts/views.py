from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.decorators import login_required

from zerotocareer.database import users, accounts

from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes
from zerotocareer.common_classes import JSONOpenAPIRender


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def default_view(request):

    return render(request, 'temporary/mainpage.html')


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


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def profile(request):

    """
    Temporary! Always redirects to the base page
    :param request: django request
    :return:
    """

    return redirect('/')


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def profile_results(request):

    """
    Temporary! Shows the results for the task_id
    :param request: django request
    :return:
    """
    task_id = request.GET.get('task_id')
    score = accounts.find_one({'user_id': request.user.username})['tasks'][task_id]

    return render(request, 'accounts/profile/results.html', {'task_id': task_id, 'score': score})
