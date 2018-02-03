"""
Definition of urls for MDNLocalLibraryWebsite.
"""

from django.conf.urls import include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
	# Examples:
	# url(r'^$', MDNLocalLibraryWebsite.views.home, name='home'),
	# url(r'^MDNLocalLibraryWebsite/', include('MDNLocalLibraryWebsite.MDNLocalLibraryWebsite.urls')),

	# Redirect any request to the base url to localhost/catalog
	url(r'^$', RedirectView.as_view(url='/catalog/', permanent=True)),

	# Let the Catalog module deal with /catolog/ urls
	url(r'^catalog/', include('catalog.urls')),

	#Add Django site authentication urls (for login, logout, password management)
	url(r'^accounts/', include('django.contrib.auth.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', admin.site.urls),
]

# Serve static files in debug mode only
from django.conf import settings
if settings.DEBUG:
	from django.conf.urls.static import static
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)