# Server Installation

    sudo apt-get install mongodb-server
    pip install -r requirements.txt

# Git Installation

Refer to https://www.techrepublic.com/article/how-to-install-http-git-server-on-ubuntu-18-04/

Some changes done in the nginx config file - 

	Added SSL certificate
	Changed server name
	Changed location
    
# Run

## One Time

	python manage.py migrate
	
## Everytime

	python manage.py runserver <ip>:<port>

