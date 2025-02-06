from django.http import HttpResponseForbidden


class CheckUploadPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исключаем админку
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        if request.user.is_authenticated and not request.user.has_perm('app_name.add_image'):
            return HttpResponseForbidden("You don't have permission to upload images.")

        response = self.get_response(request)
        return response