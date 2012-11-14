import simplejson
from telepresence import globalconfig
from django.db import transaction
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.utils.crypto import get_random_string

from telepresence.robotarmy.models import Robot

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


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
        # Append additional data -- move this somewhere else?
        data["robot_join_timeout"] = globalconfig.ROBOT_JOIN_TIMEOUT
        return HttpResponse(simplejson.dumps(data), 'application/javascript')

def robot_session_ended(request):
    """The robot would call this view to tell us that the session ended
    so that we change the state"""
    ip = request.META['REMOTE_ADDR']
    key = request.GET.get('key')
    robot = get_object_or_404(Robot, ip=ip)

    if key != robot.secret_key:
        return HttpResponseUnauthorized()
    robot_updated = Robot.objects.filter(
        ip=ip, state=Robot.STATE_ACTIVE
        ).update(state=Robot.STATE_READY)
    if robot_updated == 0: # Not sure if this is the correct behavior
        response = {"error": True, "message": "Status changed before I could update"}
        return HttpResponseBadRequest(simplejson.dumps(response), 'application/javascript')
    else:
        response = {"error": False, "message": "Status changed successfully"}
        return HttpResponse(simplejson.dumps(response), 'application/javascript')

@transaction.commit_on_success
def robot_heartbeat(request):
    """This comes every globalconfig.HEARTBEAT_INTERVAL, and tells us that
    everything is OK.

    If it is called on an IP for the first time, it creates a robot at that
    IP and creates a key that must be used each time a request originates
    from that IP."""
    ip = request.META['REMOTE_ADDR']

    robot, created = Robot.objects.get_or_create(ip=ip)
    if created:
        key = get_random_string(50)
        robot.secret_key = key
        ## TODO: Add name here?
        robot.save()
        Robot.objects.update_heartbeat_and_state(ip, Robot.STATE_READY)
    else:
        is_active = request.GET.get('active')
        key = request.GET.get('key')
        if key != robot.secret_key:
            return HttpResponseUnauthorized()
        if is_active and int(is_active):
            # This does not need to be safe because it should never actually change
            # The state...do we need a query here?
            # TODO: Can this really happen?
            Robot.objects.update_heartbeat_and_state(ip, Robot.STATE_ACTIVE)
        else:
            Robot.objects.update_heartbeat_and_state(ip, Robot.STATE_READY)
    return HttpResponse(key)
