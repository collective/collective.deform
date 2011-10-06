import webob

def convert_request(self, request):
    pointer = request.stdin.tell()
    try:
        request.stdin.seek(0)
        body = request.stdin.read()
        return webob.Request.blank('/', POST=body, environ=request.environ)
    finally:
        request.stdin.seek(pointer)

def validate_form(self, form, request):
    return form.validate(convert_request(request))
