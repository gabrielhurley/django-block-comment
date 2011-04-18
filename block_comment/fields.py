import new

from django.conf import settings
from django.contrib.contenttypes import generic
from django.db.models.fields import TextField
from django.utils.functional import wraps

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules

from block_comment.models import BlockComment

def _update_comments(method):
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        for comment in self.comments.all():
            comment.relink_comment(self.document)
    return wrapper

def _get_orphan_comments(self):
    return getattr(self, self._block_comment_related_field_name).filter(index__isnull=True)

def _get_block_comments(self):
    return getattr(self, self._block_comment_related_field_name).filter(index__isnull=False)

class BlockCommentField(TextField):
    '''
    A TextField subclass which is aware of comments related to it, and attempts
    to preserve their relation to the text within it across edits.
    '''
    def __init__(self, related_name="comments", *args, **kwargs):
        super(BlockCommentField, self).__init__(*args, **kwargs)
        self.related_name = related_name

    def contribute_to_class(self, cls, name):
        '''
        Add a reverse generic relation to our class, then wrap the 
        save method so that we can update the related comments on save.
        '''
        gr = generic.GenericRelation(BlockComment, object_id_field='object_pk')
        setattr(cls, self.related_name, gr)
        cls.comments.contribute_to_class(cls, self.related_name)
        super(BlockCommentField, self).contribute_to_class(cls, name)
        setattr(cls, "get_orphan_comments", new.instancemethod(_get_orphan_comments, None, cls))
        setattr(cls, "get_block_comments", new.instancemethod(_get_block_comments, None, cls))
        self.model.save = _update_comments(self.model.save)
        cls._block_comment_field_name = name
        cls._block_comment_related_field_name = self.related_name

    def formfield(self, **kwargs):
        from block_comment import forms
        defaults = {'form_class': forms.BlockCommentFieldForm}
        defaults.update(kwargs)
        return super(BlockCommentField, self).formfield(**kwargs)

if 'south' in settings.INSTALLED_APPS:
    add_introspection_rules([], ["^block_comment\.fields\.BlockCommentField"])