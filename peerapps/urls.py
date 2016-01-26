from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    url(r'^setup.html$', "setup.views.setup"),
    url(r'^peercoin_minting.html$', "minting.views.peercoin_minting"),
    url(r'^peerblog.html$', "peerblog.views.peerblog"),
    
    url(r'^admin/', include(admin.site.urls)),

    url(r'^peermarket/', include('peermarket.urls')),
    url(r'^peercoin_minting/', include('minting.urls')),

    url(r'^', include('setup.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
