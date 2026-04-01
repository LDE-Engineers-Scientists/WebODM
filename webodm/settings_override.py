# =============================================================
# LDE Entra ID SSO Configuration
# This file is auto-imported by settings.py via:
#   from .settings_override import *
#
# All secrets are read from environment variables.
# Set these in your .env file (never commit .env to git).
# =============================================================

import os

# Extend INSTALLED_APPS with allauth
# NOTE: After upstream WebODM updates, verify this list matches
# the base INSTALLED_APPS in settings.py plus our additions.
INSTALLED_APPS = [
    # --- Original WebODM apps (keep in sync with settings.py) ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django_filters',
    'guardian',
    'rest_framework',
    'rest_framework_nested',
    'drf_yasg',
    'webpack_loader',
    'corsheaders',
    'colorfield',
    'imagekit',
    'codemirror2',
    'app',
    'nodeodm',
    # --- LDE SSO additions ---
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Allauth behavior
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# Microsoft Entra ID — tenant config only.
# Credentials (client_id, secret) are stored in the database via the
# SocialApp model (set up by setup_socialapp.py on first deploy).
# The tenant restricts logins to LDE's organisation only.
SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'TENANT': os.environ.get('ENTRA_TENANT_ID', 'organizations'),
    }
}
