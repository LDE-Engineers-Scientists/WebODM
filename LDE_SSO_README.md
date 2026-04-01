# LDE WebODM Customizations

This fork adds Microsoft Entra ID (Azure AD) SSO authentication, Microsoft Teams
task notifications, and a diagnostic page fix to WebODM.

---

## Quick Start (Local Docker Deployment)

### 1. Prerequisites
- Docker & Docker Compose installed
- Azure Portal access (for Entra ID app registration)
- A Microsoft Teams channel (for webhook notifications)

### 2. Register Entra ID App

1. Go to **Azure Portal** > **Microsoft Entra ID** > **App registrations** > **New registration**
2. Name: `WebODM-LDE`
3. Supported account types: **"Accounts in this organizational directory only"** (single tenant)
4. Redirect URI (Web): `http://localhost:8000/accounts/microsoft/login/callback/`
5. After creation, note your:
   - **Application (client) ID**
   - **Directory (tenant) ID**
6. Go to **Certificates & secrets** > **New client secret** > copy the **Value**
7. API permissions: `Microsoft Graph > User.Read` (should be there by default)

### 3. Configure Settings

Edit `webodm/settings_override.py` and replace the placeholder values:

```python
SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'APPS': [{
            'client_id': '<YOUR_CLIENT_ID>',        # from step 5
            'secret': '<YOUR_CLIENT_SECRET>',         # from step 6
            'settings': {
                'tenant': '<YOUR_TENANT_ID>',         # from step 5
            }
        }],
    }
}
```

**For production/Docker:** You can mount this file externally via `docker-compose.settings.yml`
using the `WO_SETTINGS` environment variable to keep secrets out of the repo.

### 4. Build and Run

```bash
docker compose build
docker compose up -d db broker webapp worker
```

### 5. Run Migrations & Configure Site

```bash
docker compose exec webapp python manage.py migrate

docker compose exec webapp python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'WebODM LDE'})
"
```

### 6. Set Up Teams Webhook

1. In Microsoft Teams, go to the target channel
2. Click **...** > **Workflows** > **"When a Teams webhook request is received"**
3. Choose auth type, add action **"Post card in chat or channel"**
4. Save and copy the webhook URL
5. In WebODM, go to **Teams Notification** in the sidebar menu
6. Paste the webhook URL, select notification events, click **Apply Settings**
7. Click **Send Test Message** to verify

### 7. Enable the Teams Plugin

If not auto-enabled, go to **Administration** > **Plugins** and enable **Teams Notification**.

---

## What Was Changed

### Files Modified from Upstream (4 files)

| File | Change | Lines |
|------|--------|-------|
| `requirements.txt` | Added `django-allauth==0.51.0` | 1 |
| `webodm/urls.py` | Added `url(r'^accounts/', include('allauth.urls'))` | 1 |
| `app/templates/app/registration/login.html` | Added "Sign in with Microsoft" button | ~10 |
| `coreplugins/diagnostic/plugin.py` | Changed `shutil.disk_usage('./')` to `shutil.disk_usage(settings.MEDIA_ROOT)` | 2 |

### Files Added (never conflict with upstream)

| File/Directory | Purpose |
|---------------|---------|
| `webodm/settings_override.py` | Entra ID SSO config (allauth settings, provider credentials) |
| `coreplugins/teamsnotify/` | Teams webhook notification plugin (entire directory) |
| `LDE_SSO_README.md` | This documentation |

---

## Updating from Upstream

When OpenDroneMap releases a new WebODM version:

```bash
# Add upstream remote (first time only)
git remote add upstream https://github.com/OpenDroneMap/WebODM.git

# Fetch and merge
git fetch upstream
git merge upstream/master
```

**Resolve any conflicts** in the 4 modified files. Then:

1. **Verify `INSTALLED_APPS`**: Compare the base list in `webodm/settings.py` with the
   copy in `webodm/settings_override.py`. If upstream added new apps, add them to the
   override file too.

2. **Rebuild and migrate:**
   ```bash
   docker compose build
   docker compose up -d
   docker compose exec webapp python manage.py migrate
   ```

### Generate a Patch (Backup)

To create a standalone patch of the 4 core file changes:

```bash
git diff upstream/master -- requirements.txt webodm/urls.py \
    app/templates/app/registration/login.html \
    coreplugins/diagnostic/plugin.py > lde_core_changes.patch
```

To re-apply on a fresh WebODM checkout:

```bash
git apply lde_core_changes.patch
```

---

## Architecture Notes

- **SSO** uses [django-allauth](https://docs.allauth.org/) with the Microsoft provider.
  Version 0.51.0 is pinned for Django 2.2 compatibility.
- **Settings override** leverages WebODM's built-in `settings_override.py` import at the
  bottom of `settings.py` -- no monkey-patching needed.
- **Teams plugin** follows the same pattern as the built-in `tasknotification` plugin,
  using Django signals (`task_completed`, `task_failed`, `task_removed`) and WebODM's
  `GlobalDataStore` for config persistence.
- **Teams webhook** uses the Power Automate Workflows approach (not the deprecated
  Office 365 Connectors) with Adaptive Cards.
- **Diagnostic fix** changes the disk usage measurement from the container root (`./`)
  to the actual data volume (`settings.MEDIA_ROOT`).
