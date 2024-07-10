
from rest_framework.routers import DefaultRouter

class ConditionalRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def register_if_authenticated(self, prefix, viewset, basename=None):
        if self.request.user.is_authenticated:
            self.register(prefix, viewset, basename=basename)
