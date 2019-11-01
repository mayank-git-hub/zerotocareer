from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views import View
from zerotocareer.database import users_history, user_info

import datetime

from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes


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

            user_info.insert_one({
                'username': form.cleaned_data.get('username'),
                'flows': [],
            })
            users_history.insert_one({
                'username': form.cleaned_data.get('username'),
                'click_history': ['login/sign_up'],
                'click_time_history': [str(datetime.datetime.now())],
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


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def profile(request):

    if not request.user.is_authenticated:
        return redirect(request, '/accounts/login')

    return redirect('/')
