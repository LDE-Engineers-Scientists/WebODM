from django.contrib.sites.models import Site
site, created = Site.objects.update_or_create(
    id=1,
    defaults={'domain': 'localhost:8000', 'name': 'WebODM LDE'}
)
print("Site configured:", site.domain)
