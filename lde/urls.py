"""
LDE extended URL configuration.
Imports everything from WebODM's original urls.py and adds allauth.
ROOT_URLCONF in settings_override.py points here instead of webodm.urls.
When WebODM updates urls.py, this file picks up those changes automatically.
"""
from webodm.urls import urlpatterns, schema_view  # noqa: F401
from django.conf.urls import url, include

# Append allauth OAuth routes to WebODM's existing URL patterns
urlpatterns = list(urlpatterns) + [
    url(r'^accounts/', include('allauth.urls')),
]
