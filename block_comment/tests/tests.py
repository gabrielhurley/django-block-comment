import time

from django.conf import settings
from django.contrib.comments.forms import CommentSecurityForm
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from block_comment.forms import BlockCommentForm
from block_comment.models import BlockComment
from block_comment.tests.models import TestModel
from block_comment.tests.test_content import *

class BlockCommentTests(TestCase):
    urls = 'block_comment.tests.urls'

    def _construct_form_data(self):
        form = CommentSecurityForm(self.obj)
        timestamp = int(time.time())
        security_hash = form.initial_security_hash(timestamp)
        self.data["content_type"] = ".".join((self.ct.app_label, self.ct.model))
        self.data["timestamp"] = str(timestamp)
        self.data["security_hash"] = str(security_hash)
        self.data["next"] = "/next"

    def setUp(self):
        self.c = Client()
        self.ct = ContentType.objects.get_for_model(TestModel)
        self.obj = TestModel.objects.create(document=FULL_TEXT)
        self.original_COMMENTS_APP = getattr(settings, "COMMENTS_APP", None)
        settings.COMMENTS_APP = "block_comment"
        self.data = dict(
            name = "Gabriel Hurley",
            email = "gabriel@example.com",
            url = "example.com",
            comment = "This section needs to be cleaned up.",
            index = "368",
            regarding = ORIGINAL_TEXT,
            content_type = str(self.ct),
            object_pk = str(self.obj.id),
            site_id = "1",
        )

    def tearDown(self):
        settings.COMMENTS_APP = self.original_COMMENTS_APP

    def test_comment_view(self):
        post_url = reverse('post_block_comment')
        self._construct_form_data()

        # GET disallowed
        response = self.c.get(post_url)
        self.assertEqual(405, response.status_code)

        #POST successful w/ valid data
        response = self.c.post(post_url, self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        comment = response.context["comment"]
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.data["regarding"], comment.regarding)
        self.assertEqual(int(self.data["index"]), comment.index)
        self.assertTemplateUsed(response, 'block_comment/comment.html')

    def test_field_methods(self):
        bc = BlockComment.objects.create(**self.data)
        self.data["index"] = None
        self.data["comment"] = "This is a second comment."
        bc = BlockComment.objects.create(**self.data)
        self.assertQuerysetEqual(self.obj.get_block_comments(), [
            '<BlockComment: Gabriel Hurley: This section needs to be cleaned up....>',
        ])
        self.assertQuerysetEqual(self.obj.get_orphan_comments(), [
            '<BlockComment: Gabriel Hurley: This is a second comment....>',
        ])

    def test_field_save(self):
        bc = BlockComment.objects.create(**self.data)
        self.obj.document = TEXT_START + LONG_SENTENCE + ONE_SENTENCE + TEXT_END
        self.obj.save()
        bc = BlockComment.objects.get(id=bc.id)
        self.assertEqual(648, bc.index)

    def test_regarding_validation(self):
        self._construct_form_data()
        form = BlockCommentForm(self.obj, data=self.data)
        self.assertTrue(form.is_valid())
        self.data["regarding"] = ONE_CHARACTER
        form = BlockCommentForm(self.obj, data=self.data)
        self.assertFalse(form.is_valid())

    def test_relink_comment(self):
        bc = BlockComment(index=368, regarding=ORIGINAL_TEXT)
        bc.relink_comment(TEXT_START + EXTRA_P + LONG_SENTENCE + TEXT_END, save=False)
        self.assertEqual(579, bc.index)

    def test_text_changes(self):
        bc = BlockComment(index=368, regarding=ORIGINAL_TEXT)
        # Test basic matching tolerance
        self.assertEqual(368, bc.get_match_index(FULL_TEXT))
        self.assertEqual(368, bc.get_match_index(TEXT_START + ONE_CHARACTER + TEXT_END))
        self.assertEqual(368, bc.get_match_index(TEXT_START + ONE_WORD + TEXT_END))
        self.assertEqual(368, bc.get_match_index(TEXT_START + TWO_WORDS + TEXT_END))
        self.assertEqual(368, bc.get_match_index(TEXT_START + ONE_SENTENCE + TEXT_END))
        self.assertEqual(759, bc.get_match_index(TEXT_START + ONE_SENTENCE + ORIGINAL_TEXT + TEXT_END))
        # Expected failure, too similar
        self.assertEqual(-1, bc.get_match_index(TEXT_START + ONE_SENTENCE + ONE_CHARACTER + TEXT_END))
        self.assertEqual(368, bc.get_match_index(TEXT_START + ONE_SENTENCE + LONG_SENTENCE + TEXT_END))
        self.assertEqual(648, bc.get_match_index(TEXT_START + LONG_SENTENCE + ONE_SENTENCE + TEXT_END))
        self.assertEqual(368, bc.get_match_index(TEXT_START + LONG_SENTENCE + TEXT_END))
        # Expected failure, too different
        self.assertEqual(-1, bc.get_match_index(TEXT_START + MULTIPLE_SENTENCES + TEXT_END))
        
        # Test adding blocks in ahead of the match
        self.assertEqual(579, bc.get_match_index(TEXT_START + EXTRA_P + ORIGINAL_TEXT + TEXT_END))
        self.assertEqual(579, bc.get_match_index(TEXT_START + EXTRA_P + ONE_SENTENCE + TEXT_END))
        self.assertEqual(579, bc.get_match_index(TEXT_START + EXTRA_P + LONG_SENTENCE + TEXT_END))
        # Expected failure, too different
        self.assertEqual(-1, bc.get_match_index(TEXT_START + EXTRA_P + MULTIPLE_SENTENCES + TEXT_END))
