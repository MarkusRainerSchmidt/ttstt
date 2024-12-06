"""TTsTT server"""

from .ttstt import TTSTT

from flask import Flask, request, Response

_HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


ttstt = TTSTT()

@app.route('/', defaults={'path': ''}, methods=_HTTP_METHODS)
@app.route('/<path:path>', methods=_HTTP_METHODS)
def catch_all(path: str) -> Response:
    """Catch-all method which handles all http requests.

    Args:
        path (str): The path string, not used.

    Returns:
        Response: A plain text Response echoing the contents of the user's original request
    """
    
    return Response(ttstt.onRequest(request.data), mimetype='text/plain')


def main() -> None:
    """Main method, invoked if this script is run directly"""
    app.run()


if __name__ == "__main__":
    main()
