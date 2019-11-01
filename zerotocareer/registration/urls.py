from django.urls import path
from django.contrib.auth.views import (
	LoginView, LogoutView,
	PasswordChangeView, PasswordChangeDoneView,
	PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from .views import *

app_name = 'login'
urlpatterns = [
	path('sign_up/', MySignUpView.as_view(), name='sign_up'),
	path('login/', LoginView.as_view(), name="login"),
	path('logout/', LogoutView.as_view(), name="logout"),
	path(
		'password_change/', PasswordChangeView.as_view(success_url='accounts/password_change/done/'),
		name="password_change"),
	path('password_change/done/', PasswordChangeDoneView.as_view(), name="password_change_done"),
	path('password_reset/', PasswordResetView.as_view(success_url='done/'), name="password_reset"),
	path('password_reset/done/', PasswordResetDoneView.as_view(), name="password_reset_done"),
	path(
		'reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(success_url='/accounts/reset/done/'),
		name="password_reset_confirm"),
	path('reset/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),
	path('profile/', profile, name="profile"),

	# TODO
	# path('profile/update', CustomProfileEditView.as_view(), name="update_porfile"),
]