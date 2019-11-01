# Installation

    pip install -r requirements.txt
    sudo apt-get install mongodb-server
    
# Run

## One Time

	python manage.py migrate
	
## Everytime

	python manage.py runserver <ip>:<port>