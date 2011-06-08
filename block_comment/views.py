from django.contrib.comments.views.comments import CommentPostBadRequest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils.html import escape
from django.utils import simplejson as json
from django.views.decorators.http import require_POST

from .forms import BlockCommentForm
from .models import BlockComment

@require_POST
def post_block_comment(request, using=None):
    data = request.POST.copy() # Copy, otherwise QueryDict is immutable

    # Fill out some initial data fields from an authenticated user, if present
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # ContentType validation
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))

    next = data.get('next')
    if not next and hasattr(target, "get_absolute_url"):
        next = target.get_absolute_url()

    # Back to the actual comment
    form = BlockCommentForm(target, data=data)
    if form.is_valid():
        comment = form.get_comment_object()
        if request.user.is_authenticated():
            comment.user = request.user
        comment.save()
        d = {"comment": comment}
        if request.is_ajax():
            template_list = [
                "block_comment/comment.html",
                "comments/%s/%s/comment.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s/comment.html" % model._meta.app_label,
                "comments/comment.html",
            ]
            return render_to_response(template_list, d, RequestContext(request))
        else:
            if not next:
                raise ValueError("You must either pass a 'next' parameter in via POST or define a 'get_absolute_url' method on your model")
            return redirect(next)
    else:
        if request.is_ajax():
            # Send back a JSON dump of the errors to be handled by the frontend.
            content = {
                "errors": form.errors,
                "status": 500,
            }
            return HttpResponse(json.dumps(content), content_type="application/json")
        else:
            # Fall back to built-in contrib.comments mechanism to handle
            # non-ajax posts with errors.
            template_list = [
                "block_comment/preview.html",
                "comments/%s/%s/preview.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s/preview.html" % model._meta.app_label,
                "comments/preview.html",
            ]
            d = {
                "comment": form.data.get("comment", ""),
                "form": form,
                "next": next,
            }
            return render_to_response(template_list, d, RequestContext(request))
