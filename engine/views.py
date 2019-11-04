from django.shortcuts import redirect, HttpResponse
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes
import os
import json

from zerotocareer.database import active
# Create your views here.


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def start_task(request):

	if not request.user.is_authenticated:
		redirect('/accounts/login')

	# Create user-password

	for user in active.find():

		os.system("echo mayank1 | sudo -S htpasswd /home/git/GitRepos/htpasswd " + str(user['user_id'] + ' ' + str(user['git_password'])))

	# Create Git Repository

	commands = """
		cd /home/git/GitRepos
		echo mayank1 | sudo -S mkdir task.git
		sudo cd task.git
		sudo git --bare init
		sudo git update-server-info
		sudo chown -R root.root .
		sudo chmod -R 755 .
	"""

	os.system(commands)

	return HttpResponse(json.dumps({'status': 'success', 'git_repo_name': 'task.git'}))
