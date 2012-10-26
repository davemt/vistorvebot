import simplejson
from telepresence import globalconfig
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse

from telepresence.robotarmy.models import Robot

@login_required
def robot_list(request):
    return render_to_response(
        'robot-list.html', {'robots': Robot.objects.all(),
                            'hangout_url': globalconfig.HANGOUT_JOIN_URL
                            }, context_instance=RequestContext(request)
        )

def robot_initialize_session(request, robot_id):
    if not request.is_ajax():
        raise Http404
    else:
        robot = get_object_or_404(Robot, pk=robot_id)
        data = robot.initialize_session()
        # Render the button template (hangout.html) to text and add it to the json
        # Add the URL
        # Add the javascrip to call this and render the button
        return HttpResponse(simplejson.dumps(data), 'application/javascript')
