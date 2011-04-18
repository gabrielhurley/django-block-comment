from django.db import models

from block_comment.fields import BlockCommentField

class TestModel(models.Model):
    document = BlockCommentField()
