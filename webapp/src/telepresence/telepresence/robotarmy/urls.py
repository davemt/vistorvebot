from django.conf.urls import patterns, url

urlpatterns = patterns('telepresence.robotarmy.views',

    # SEGMENT NODE ASSIGNMENTS
    url(r'^robot-list/$',
        'robot_list', name='robot-list'),
    url(r'^robot-initialize-session/(?P<robot_id>\d+)/$',
        'robot_initialize_session', name='robot-initialize-session'),
)
