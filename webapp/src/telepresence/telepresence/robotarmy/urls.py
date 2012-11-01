from django.conf.urls import patterns, url

urlpatterns = patterns('telepresence.robotarmy.views',

    # SEGMENT NODE ASSIGNMENTS
    url(r'^robot-list/$',
        'robot_list', name='robot-list'),
    url(r'^robot-heartbeat/$',
        'robot_heartbeat', name='robot-heartbeat'),
    url(r'^robot-session-ended/$',
        'robot_session_ended', name='robot-session-ended'),
    url(r'^robot-initialize-session/(?P<robot_id>\d+)/$',
        'robot_initialize_session', name='robot-initialize-session'),
)
