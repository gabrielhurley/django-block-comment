from django.contrib import admin

from .models import BlockComment

class BlockCommentAdmin(admin.ModelAdmin):
    readonly_fields = ('index', 'regarding',)

admin.site.register(BlockComment, BlockCommentAdmin)
