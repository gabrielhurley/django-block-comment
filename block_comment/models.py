'''Custom models for the block_comment app.'''

import difflib

from django.contrib.comments.models import Comment
from django.db import models
from django.utils.translation import ugettext as _

from block_comment.diff_match_patch import diff_match_patch

class BlockComment(Comment):
    '''
    ``BlockComment`` extends Django's comments framework to store information
    about the block of text the comment relates to.
    '''
    
    # Position in the full text that the block the comment relates to begins at
    index = models.PositiveIntegerField(null=True, blank=True, editable=False)

    # The text of the block, used for determining diffs/orphans
    regarding = models.TextField(blank=True, editable=False)

    def get_match_index(self, haystack):
            ''' Returns the index of the closest match to needle within
                the haystack. '''

            def get_block_index(i):
                ''' ``haystack`` and ``blocks`` are accessible by closure. '''
                return haystack.index(blocks[i])

            needle = self.regarding.strip()
            matches = []
            blocks = haystack.split("\n")
            block_index = None

            # Check for an exact match first
            if needle in blocks:
                return get_block_index(blocks.index(needle))

            # If that didn't work, do a basic diff comparison block-by-block
            for p in blocks:
                comp = difflib.SequenceMatcher(None, needle, p)
                if comp.ratio() > .85:
                    matches.append(blocks.index(comp.b))
            if len(matches) == 1:
                block_index = matches.pop()
            elif len(matches) == 0:
                # No matches, can we find a potential match with a smarter
                # matching algorithm?
                matcher = diff_match_patch()
                index = matcher.match_main(haystack, needle, 0)
                if index > -1:
                    return index
            else:
                # We've got multiple options, let's narrow them down with
                # a smarter matching algorithm.
                matcher = diff_match_patch()
                for i in tuple(matches):
                    if matcher.match_main(blocks[i], needle, self.index) < 0:
                        # No match, discard this option
                        matches.remove(i)
                # Unless we've only got one match left, we'll fall through to -1
                if len(matches) == 1:
                    block_index = matches[0]

            if block_index:
                return get_block_index(block_index)

            # If we can't find anything, return -1
            return -1

    def relink_comment(self, haystack, save=True):
        index = self.get_match_index(haystack)
        if index == self.index:
            return None
        elif index > -1:
            self.index = index
        else:
            self.index = None
        if save:
            self.save()