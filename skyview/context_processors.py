from .utils import is_skyview_owner


def owner_context(request):
    is_owner = False
    if hasattr(request, 'user') and request.user.is_authenticated:
        is_owner = is_skyview_owner(request.user)
    return {'is_owner': is_owner}
