import datetime
import simplejson
from telepresence import globalconfig
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseBadRequest

from telepresence.robotarmy.models import Robot

@login_required
def robot_list(request):
    robots = Robot.objects.all()
    for bot in robots:
        bot.refresh_state()
    return render_to_response(
        'robot-list.html', {'robots': robots,
                            'hangout_url': globalconfig.HANGOUT_JOIN_URL
                            }, context_instance=RequestContext(request)
        )

def robot_initialize_session(request, robot_id):
    if not request.is_ajax():
        raise Http404
    else:
        robot = get_object_or_404(Robot, pk=robot_id)
        data = robot.initialize_session()
        return HttpResponse(simplejson.dumps(data), 'application/javascript')

def robot_session_ended(request):
    """The robot would call this view to tell us that the session ended
    so that we change the state"""
    ip = request.GET.get('ip')
    robot_updated = Robot.objects.filter(
        ip=ip, state=Robot.STATE_ACTIVE
        ).update(state=Robot.READY)
    if robot_updated == 0: # Not sure if this is the correct behavior
        response = {"error": True, "message": "Status changed before I could update"}
        return HttpResponseBadRequest(simplejson.dumps(response), 'application/javascript')
    else:
        response = {"error": False, "message": "Status changed successfully"}
        return HttpResponse(simplejson.dumps(response), 'application/javascript')

def robot_heartbeat(request):
    """This comes every globalconfig.HEARTBEAT_INTERVAL, and tells us that
    everything is OK"""
    ip = request.GET.get('ip')
    is_active = request.GET.get('active')
    if is_active and int(is_active):
        # This does not need to be safe because it should never actually change
        # The state...do we need a query here?
        Robot.objects.filter(ip=ip).update(
            state=Robot.STATE_ACTIVE, last_heartbeat=datetime.datetime.now()
        )
    else:
        # This does not need to be safe because it should never actually change
        # The state...do we need a query here?
        Robot.objects.filter(ip=ip).update(
            state=Robot.READY, last_heartbeat=datetime.datetime.now()
        )
    return HttpResponse('')
