from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('block_comment.views',
    url(r'^post_comment$', 'post_block_comment', name='post_block_comment'),
)