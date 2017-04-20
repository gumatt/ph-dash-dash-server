import logging

from flask import Flask


app = Flask(__name__)

@app.route('/')
def hello():
    return "Yo! Hello World"

@app.errorhandler(500)
def server_error(error):
    # Log teh error and stacktrace
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred: {}'.format(error), 500
