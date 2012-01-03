import webob
import deform

def convert_request(request):
    pointer = request.stdin.tell()
    try:
        request.stdin.seek(0)
        body = request.stdin.read()
        return webob.Request.blank('/', POST=body, environ=request.environ)
    finally:
        request.stdin.seek(pointer)
