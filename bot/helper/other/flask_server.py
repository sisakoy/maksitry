from threading import Thread
from flask import Flask
from bot import PORT



app = Flask(__name__)


@app.route('/')
def index():
            return 'Bot By Sahil'
    

def run():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
    


def run_flask():
    server = Thread(target=run, daemon=True)
    server.start()