from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


def has_write_access():
    """Requirements:
        - user must be logged in ('@login_required' from django.contrib.auth.decorators)
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.user.write_access:
                return func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have write access.")

        return inner

    return decorator


class HasWriteAccessMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.write_access:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
