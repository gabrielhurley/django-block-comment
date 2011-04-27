from django.template import RequestContext
from django.shortcuts import render_to_response

from block_comment.tests.models import TestModel

def index(request):
    t = TestModel.objects.all()[0]
    return render_to_response('index.html', {"object": t}, context_instance=RequestContext(request))