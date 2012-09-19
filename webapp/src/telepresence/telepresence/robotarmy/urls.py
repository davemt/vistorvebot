from django.conf.urls import patterns, url

urlpatterns = patterns('telepresence.robotarmy.views',

    # SEGMENT NODE ASSIGNMENTS
    url(r'^robot-list/$',
        'robot_list', name='robot-list'),

)
