from __init__ import create_app
from rest_controller import *

app = create_app()

if __name__ == '__main__':
	app.run(host='localhost', port=8000, debug=True)
	