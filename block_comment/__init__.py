from django.core.urlresolvers import reverse

from block_comment.models import BlockComment
from block_comment.forms import BlockCommentForm

def get_model():
    return BlockComment

def get_form():
    return BlockCommentForm

def get_form_target():
    return reverse('post_block_comment')