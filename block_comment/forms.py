from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from block_comment.models import BlockComment

class BlockCommentForm(CommentForm):
    index = forms.IntegerField(min_value=0, required=False, widget=forms.HiddenInput())
    regarding = forms.CharField(required=False, widget=forms.HiddenInput())
    url = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_regarding(self):
        '''
        Verify that the regarding text is actually in the original text in
        order to eliminate malicious alterations of the posted data.
        '''
        text = self.cleaned_data.get("regarding", '')
        if text:
            target = self.target_object
            field_name = getattr(target, '_block_comment_field_name', '')
            orig_text = getattr(target, field_name, '')
            if text not in orig_text:
                text = strip_tags(text)
                if text not in orig_text:
                    raise forms.ValidationError("Could not find the selected text block in the full text.")
        return text

    def get_comment_model(self):
        return BlockComment

    def get_comment_create_data(self):
        data = super(BlockCommentForm, self).get_comment_create_data()
        data.update({
            "index": self.cleaned_data["index"],
            "regarding": self.cleaned_data["regarding"],
        })
        return data

    class Meta:
        exclude = ('index', 'regarding')


class BlockCommentFieldForm(forms.CharField):
    pass
