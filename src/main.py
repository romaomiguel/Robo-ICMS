import os
import sys
import socket
from werkzeug.middleware.proxy_fix import ProxyFix

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.nfe import nfe_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Enable CORS for all routes
CORS(app)

app.register_blueprint(nfe_bp, url_prefix='/api/nfe')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true')

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f" * Running on http://localhost:5000")
    print(f" * Running on http://{hostname}.local:5000")
    print(f" * Running on http://{local_ip}:5000")

    app.run(host='0.0.0.0', port=5000, debug=debug)

