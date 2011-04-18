from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),
     url(r'^comments/', include('block_comment.urls')),
     url(r'^$', 'views.index', name='index'),
)
