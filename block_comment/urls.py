from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('block_comment.views',
    url(r'^post_comment$', 'post_block_comment', name='post_block_comment'),
)

urlpatterns += patterns('',
    url(r'', include('django.contrib.comments.urls')),
)
