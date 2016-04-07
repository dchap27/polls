from django.conf.urls import url

from polls import views

app_name='polls'
urlpatterns = [
    #Account Management
    url(r'^user/edit/$', views.edit_profile, name='edit_profile'),

    # ex: /polls/login/
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',name='logout'),
    url(r'^register/$', views.register_page, name='register'),
    # Password management
    url(r'^password-change/$', 'django.contrib.auth.views.password_change',
        {'post_change_redirect':'/done',
        'template_name':'registration/password_change_form.html'},
         name='password_change'),
    url(r'^password-change/done/$', 'django.contrib.auth.views.password_change_done',
         name='password_change_done'),
    # restore password urls
    url(r'^password-reset/$','django.contrib.auth.views.password_reset',
         {'template_name':'registration/password_reset_form.html',
         'email_template_name':'registration/password_reset_email.html',
         'subject_template_name':'registration/password_reset_subject.txt',
         'post_reset_redirect':'done/'},
         name='password_reset'),
    url(r'^password-reset/done/$','django.contrib.auth.views.password_reset_done',
         {'template_name':'registration/password_reset_done.html'},
         name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
         'django.contrib.auth.views.password_reset_confirm',
         {'template_name':'registration/password_reset_confirm.html',
         'post_reset_redirect':'/polls/password-reset/complete/'},
         name='password_reset_confirm'),
    url(r'^password-reset/complete/$',
         'django.contrib.auth.views.password_reset_complete',
         {'template_name':'registration/password_reset_complete.html'},
         name='password_reset_complete'),

    #Browsing
    # ex: /polls/5/
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^(?P<question_id>[0-9]+)/graph/$', views.result_graph, name='graph'),
    # ex: /polls/5/vote/
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^feat/$', views.features, name='features'),
    url(r'^user/(\w+)/$', views.user_page, name='user_page'),
    url(r'^category/(\w+)/$', views.category_page, name='categories'),
    url(r'^category_graph/$', views.category_count, name='category_graph'),
    url(r'^popular/$', views.popular_polls, name='popular'),
    url(r'^recent/$', views.recent_polls, name='recent'),
    url(r'^action/feeds/$', views.action_feeds, name='action_feeds'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^(\w+)/voted/$', views.voted_polls, name='voted_polls'),
    url(r'^(\w+)/commented/$', views.commented_polls, name='commented_polls'),

    # Content Management
    url(r'^(\w+)/save/$', views.question_save, name='save_page'),
    url(r'^search/$', views.search_page, name='search'),

    # Friends
    url(r'^friends/(\w+)/$', views.friends_page, name='friends'),
    url(r'^friend/follow/$', views.friend_follow, name='friend_follow'),
    url(r'^friend/invite/$', views.friend_invite, name='friend_invite'),
    url(r'^friend/accept/(\w+)/$', views.friend_accept, name='friend_accept'),

    # upcoming
    url(r'^feedback/$', views.feedback_page, name="feedback"),
    url(r'^image-poll/$', views.image_poll, name='image_poll'),

]
