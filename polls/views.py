# Time
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from polls.models import *
from polls.forms import *
from django.db.models import F  # helps to avoid race conditions
from django.contrib.auth.models import User
from django.conf import settings # used to create user profile
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # to enable use of | OR and & AND
# Applying page numbers
from django.core.paginator import Paginator
# To including message interfaces
from django.contrib import messages
# To create actions for activity streams
from actions.utils import create_action
from actions.models import Action
from django.views.decorators.http import require_POST
import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

#initialize the facecolor for each graph
mpl.rcParams['figure.facecolor']= 'white'
ITEMS_PER_PAGE = 11


def index(request):
    #create list of questions
    questions = Question.objects.order_by('-publish')[:9]
    # Display all actions by default
    # initialize the actions when user not logged in
    actions =""
    if request.user.is_authenticated():  # incase user is not logged in
        actions = Action.objects.all()
        following_ids = request.user.following.values_list('id',flat=True) # check if user follow others
        # following_ids.append(request.user.id)

    # if the user follows others, then
        if following_ids:
            # if user is following others, retrieve only others actions
            actions1 = Q(user_id__in=following_ids)
            actions2 = Q(user_id=request.user.id)
            actions = actions.filter(actions1|actions2)\
                             .select_related('user','user__profile')\
                             .prefetch_related('target')
    if request.user.is_authenticated(): # actions when logged in
        actions = actions

    paginator = Paginator(actions, ITEMS_PER_PAGE)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        actions = paginator.page(1).object_list
    try:
        actions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        actions = paginator.page(paginator.num_pages).object_list
    # The variables to render to the template
    variables = RequestContext(request, {
       'questions': questions,
       'actions': actions,
       #'profile_pic':profile_pic,
       'show_paginator': paginator.num_pages > 1,
       'has_previous': paginator.page(page).has_previous(), # returns True or False
       'has_next': paginator.page(page).has_next(),  # returns True or False
       'page': page,
       'pages': paginator.num_pages,
       'next_page' : page + 1,
       'prev_page' : page - 1,
       'head_title': 'Polls Portal',
       'page_title': 'Welcome to Polls Portal',
       'Welcome_message': 'A place where you can share your views and opinions',
       "show_user": False,
       "show_category":True,
    })
    if request.user.is_authenticated():
        if request.is_ajax():
            return render_to_response('polls/action_feeds_ajax.html',variables)

        return render_to_response('polls/index.html', variables)
    else:
        return render_to_response('polls/index_cover.html',variables)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # if request.user.is_authenticated():
    #     profile = Profile.objects.get(user=request.user)
    #     profile_pic = profile.photo
    # else:
    #     profile_pic = ""
    all_question = Question.objects.all()
    if all_question.count() < 2:
        return render(request, 'polls/detail.html',
                     {
                     'question': question,
                     'head_title': 'Question details',
                     })
    try:
        first_question = Question.objects.get(id=1)
    except:
        messages.error(request,
          "Poll doesn't exist anymore."
        )
        return render(request, 'polls/detail.html',
                     {
                     'question': question,
                     'head_title': 'Question details',
                     })
    last_question = Question.objects.order_by('-id')[:1]
    last_question = last_question[0]
    if question == last_question:
        next_poll=False
        prev_poll=True
        next_question=last_question
        try:
            prev_question = Question.objects.get(pk=question.id-1)
        except:
            messages.warning(request,
              "Note:\n  Poll {} doesn't exist anymore.".format(question.id-1)
            )
            prev_question = get_object_or_404(Question,pk=question.id)
    elif question == first_question:
        prev_poll=False
        next_poll=True
        prev_question = get_object_or_404(Question,pk=question.id)
        try:
            next_question =Question.objects.get(pk=question.id+1)
        except:
            messages.warning(request,
              "Note:  Poll {} doesn't exist anymore.".format(question.id+1)
            )
            next_question = get_object_or_404(Question,pk=question.id)
    else:
        try:
            prev_question = Question.objects.get(pk=question.id-1)
        except:
            messages.warning(request,
              "Note:  Poll {} doesn't exist anymore.".format(question.id-1)
            )
            prev_question = get_object_or_404(Question,pk=question.id)
        try:
            next_question = Question.objects.get(pk=question.id+1)
        except:
            messages.warning(request,
              "Note: Poll {} doesn't exist anymore.".format(question.id+1)
            )
            next_question = get_object_or_404(Question,pk=question.id)
        next_poll=True
        prev_poll=True
    return render(request, 'polls/detail.html',
                 {
                 'question': question,
                 #'profile_pic': profile_pic,
                 'first_question':first_question,
                 'next_question': next_question,
                 'prev_question': prev_question,
                 'last_question': last_question,
                 'next_poll':next_poll,
                 'prev_poll':prev_poll,
                 'head_title': 'Question details',
                 })

# To display results for a particular question
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    tot_votes = (question.total_votes)
    male_votes=0
    female_votes=0
    for choice in question.choice_set.all():
        male_votes += choice.m_votes
        female_votes += choice.f_votes
    # Check if user have voted before viewing results
    if request.user != question.user :
        if not request.user in question.users_voted.all():
            return render(request,'polls/detail.html',{
                'question':question,
                'error_message':"You need to vote on poll question before you can\
                view or comment on results!"
            })
    comments = question.comments.filter(active=True) # filter active comments

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST) # Post a comment
        if comment_form.is_valid():
            # Now create a comment object but not yet saved to database
            new_comment = comment_form.save(commit=False)
            # then assign the current question to the comment
            new_comment.question = question
            new_comment.name = request.user
            # now save the comment to the database
            new_comment.save()
            # To create an action for the addition of comments
            create_action(request.user,
                'commented on poll {}'.format(question.id), new_comment
                )
            comment_form=CommentForm()  # clearing the previous comment from the form
    else:
        comment_form = CommentForm()
    return render(request, 'polls/result.html',
                 {'question':question,
                  'comments': comments,
                  'comment_form': comment_form,
                  'tot_votes':tot_votes,
                  'male_votes':male_votes,
                  'female_votes':female_votes
                 })

#produce the stastical graph of the result
def result_graph(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    tot_votes = float(question.total_votes)
    y = [(choice.votes * 100)/tot_votes for choice in question.choice_set.all()]
    x = [choice.choice_text for choice in question.choice_set.all()]
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.bar(np.arange(0.1,len(y)),y, width=0.6,
          color=['steelblue','seagreen','maroon'])
    ax.set_xticks(np.arange(len(x))+0.4)
    ax.set_xticklabels(x, rotation=45)
    ax.set_ylabel("Votes in percentage, %")
    #canvas = sns.barplot(x,y)
    # x = np.arange(-2,1.5,.01)
    # y = np.sin(np.exp(2*x))
    # ax.plot(x,y)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def index_graph(request):
    top_polls = Question.objects.order_by('-total_votes')[:10]
    y = [question.total_votes for question in top_polls]
    x = ['poll {}'.format(question.id) for question in top_polls]
    fig = Figure(figsize=(6,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.bar(np.arange(0.1,len(y)),y, width=0.6,
          color=['steelblue','#5cb85c','#d9534f','#f0ad4e'])
    ax.set_xticks(np.arange(len(x))+0.4)
    ax.set_xticklabels(x, rotation=45)
    ax.set_ylabel('Total Votes')
    #ax.set_title('Top 10 polls')

    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


@login_required(login_url='polls:login')
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # checking if user has already voted by filtering
    profile = Profile.objects.get(user=request.user)
    if question.eligibility:
        if not profile.gender == question.eligible_gender:
            eligible = question.eligible_gender
            if eligible == "M":
                sex = "Male"
            else:
                sex = "Female"
            return render(request,'polls/detail.html',{
                'question':question,
                'error_message':"You are not eligible to vote on this poll. It is gender related"
            })
    user_voted = question.users_voted.filter(
        username=request.user.username
    )
    if not user_voted:

        try:
            #Now get the particular choice selected
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Now redisplay the question voting form
            return render(request,'polls/detail.html',{
                'question':question,
                'error_message':"You didn't select a choice"
            })

        selected_choice.votes = F('votes') + 1  #allow for database to do the arithmetic
        question.total_votes += 1
        question.users_voted.add(request.user)
        # create action when users voted
        create_action(request.user, 'voted on', question)
        # group choice
        if profile.gender == 'M':
            selected_choice.m_votes = F('m_votes') + 1
        elif profile.gender == 'F':
            selected_choice.f_votes = F('f_votes') + 1
        else:
            pass
        #selected_choice.votes += 1
        selected_choice.save()
        question.save()
        question.refresh_from_db()
        selected_choice.refresh_from_db() # To refresh the database to access the new value

        # Send a notification to the creator of the poll
        try:
            my_settings = AccountSettings.objects.get(user=question.user)
            if my_settings.vote_notify:
                subject = "{} voted on poll you created".format(request.user.username)
                template = get_template("polls/vote_notification.txt")
                context = Context({
                   "question": question,
                   'name' : question.user.username,
                   'voter': request.user.username,
                   'protocol' : "http",
                   'domain':"ahmad27.pythonanywhere.com",
                })
                message = template.render(context)
                send_mail(
                  subject,message,"PollsPortal <notification@pollsportal.com>",[question.user.email]
                )
        except:
            pass
    else:
        return render(request,'polls/detail.html',{
            'question':question,
            'error_message':"Sorry! You can only vote once. Try another poll question!"
        })

    # Then redirect back
    # if request.META.has_key('HTTP_REFERER'): # Redirect back to where it came
    #     return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect(reverse (
     'polls:results', args=(question.id,)
    ))

@login_required(login_url='polls:login')
def user_page(request, username):
    #user = User.objects.get(username=username)
    today = datetime.today()
    yesterday = today - timedelta(1)
    recent = Question.objects.filter(publish__gte=yesterday)
    person = get_object_or_404(User, username=username)
    polls_voted = Question.objects.filter(users_voted=person)
    polls_commented = Question.objects.filter(comments__name__iexact=username)
    # Get the questions created by the user
    questions = person.question_set.order_by('-id')
    paginator = Paginator(questions, ITEMS_PER_PAGE)  # paging the no of items
    if request.user.is_authenticated():
        is_friend = Friendship.objects.filter(
           from_friend=request.user,
           to_friend=person
        )
    else:
        is_friend=False
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        questions = paginator.page(1).object_list
    try:
        questions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        questions = paginator.page(paginator.num_pages).object_list
    # The variables to render to the template
    variables = RequestContext(request, {
       #'profile_pic':profile_pic,
       'questions': questions,
       'recent':recent,
       'polls_voted': polls_voted,
       'polls_commented':polls_commented,
       'user': request.user,
       'username': username,
       'person':person,
       'section':'people',
       'show_paginator': paginator.num_pages > 1,
       'has_previous': paginator.page(page).has_previous(), # returns True or False
       'has_next': paginator.page(page).has_next(),  # returns True or False
       'page': page,
       'pages': paginator.num_pages,
       'next_page' : page + 1,
       'prev_page' : page - 1,
       'show_user':True,
       'show_category':True,
       'is_friend': is_friend,
    })
    return render_to_response('polls/user_page.html', variables)

def action_feeds(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',flat=True) # check if user follow others
    # if the user follows others, then
    if following_ids:
        # if user is following others, retrieve only others actions
        actions = actions.filter(user_id__in=following_ids)\
                             .select_related('user','user__profile')\
                             .prefetch_related('target')
    actions = actions
    paginator = Paginator(actions, ITEMS_PER_PAGE)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        actions = paginator.page(1).object_list
    try:
        actions = paginator.page(page).object_list
    except:
        # if the request is AJAX and the page is out of range
        # return an empty page
        if request.is_ajax():
            return HttpResponse('')
        # if page is out of range, deliver last page of results
        actions = paginator.page(paginator.num_pages).object_list
    variables = RequestContext(request, {
       'actions': actions,
       #'profile_pic':profile_pic,
       'show_paginator': paginator.num_pages > 1,
       'has_previous': paginator.page(page).has_previous(), # returns True or False
       'has_next': paginator.page(page).has_next(),  # returns True or False
       'page': page,
       'pages': paginator.num_pages,
       'next_page' : page + 1,
       'prev_page' : page - 1,
    })
    if request.is_ajax():
        return render_to_response('polls/action_feeds_ajax.html', variables)
    return render_to_response('polls/action_feeds.html', variables)


@login_required(login_url='polls:login')
def dashboard(request):
    #question = get_object_or_404(Question, pk=question_id)
    user = get_object_or_404(User, username=request.user.username)
    mypolls = Question.objects.filter(user=request.user)
    today = datetime.today()
    yesterday = today - timedelta(1)
    myvotes = Question.objects.filter(users_voted=request.user)
    mycomments = Question.objects.filter(comments__name__iexact=request.user.username)
    questions = Question.objects.filter(publish__gte=yesterday)
    return render(request, 'polls/dashboard.html',{
      'questions':questions,
      'user': user,
      'username': user.username,
      'mypolls': mypolls,
      'myvotes': myvotes,
      'mycomments': mycomments,
    })

def voted_polls(request,username):
    user = get_object_or_404(User, username=username)
    questions = Question.objects.filter(users_voted=user)
    paginator = Paginator(questions, ITEMS_PER_PAGE)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        questions = paginator.page(1).object_list
    try:
        questions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        questions = paginator.page(paginator.num_pages).object_list
    if request.is_ajax():
        questions = Question.objects.filter(users_voted=user)
        return render(request,'polls/votes_list_ajax.html',
                     {
                      'questions':questions,
                      'username':user.username,
                      'show_category':False,
                      "show_user":True,
                    #   'show_paginator': paginator.num_pages > 1,
                    #   'has_previous': paginator.page(page).has_previous(), # returns True or False
                    #   'has_next': paginator.page(page).has_next(),  # returns True or False
                    #   'page': page,
                    #   'pages': paginator.num_pages,
                    #   'next_page' : page + 1,
                    #   'prev_page' : page - 1
                     })
    else:
        return render(request,'polls/votes_list.html',
                     {
                      'questions':questions,
                      'username':user.username,
                      'show_category':True,
                      "show_user":True,
                      'show_paginator': paginator.num_pages > 1,
                      'has_previous': paginator.page(page).has_previous(), # returns True or False
                      'has_next': paginator.page(page).has_next(),  # returns True or False
                      'page': page,
                      'pages': paginator.num_pages,
                      'next_page' : page + 1,
                      'prev_page' : page - 1,
                     })

def commented_polls(request,username):
    user = get_object_or_404(User, username=username)
    questions = Question.objects.filter(comments__name__iexact=user.username)
    paginator = Paginator(questions, ITEMS_PER_PAGE)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        questions = paginator.page(1).object_list
    try:
        questions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        questions = paginator.page(paginator.num_pages).object_list
    if request.is_ajax():
        questions = Question.objects.filter(comments__name__iexact=user.username)
        return render(request,'polls/comments_list_ajax.html',
                     {
                      'questions': questions,
                      'username':user.username,
                      'show_category': False,
                      "show_user":True
                     })
    return render(request,'polls/comments_list.html',
                 {
                  'questions': questions,
                  'username':user.username,
                  'show_category': False,
                  "show_user":True,
                  'show_paginator': paginator.num_pages > 1,
                  'has_previous': paginator.page(page).has_previous(), # returns True or False
                  'has_next': paginator.page(page).has_next(),  # returns True or False
                  'page': page,
                  'pages': paginator.num_pages,
                  'next_page' : page + 1,
                  'prev_page' : page - 1,
                 })

def recent_polls(request):
    today = datetime.today()
    yesterday = today - timedelta(1)
    questions = Question.objects.filter(publish__gte=yesterday).order_by('-publish')
    if request.is_ajax():
        if len(questions)> 9:
            more_view = True
        else: more_view = False
        questions = questions[:9]
        return render(request,'polls/recent_polls_ajax.html',{
             'questions':questions,
             'show_user':True,
             'show_category':False,
             'show_publish':False,
             'more_view':more_view,
        })
    return render(request,'polls/recent_polls.html',{
         'questions':questions,
         'show_user':True,
         'show_category':True,
         'show_publish':True,
    })

# @login_required
# def user_list(request):
#     users = User.objects.filter(is_active=True)
#     return render(request,
#                  'polls/user/list.html',
#                  {'section':'people',
#                  'users': users})
#
# @login_required
# def user_detail(request,username):
#     user = get_object_or_404(User,
#                              username=username,
#                              is_active=True)
#     return render(request,
#                  'polls/user/detail.html',
#                  {'section':'people',
#                  'user': user})

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # check if the registration is through invitation
            if 'invitation' in request.session:
                invitation = \
                 Invitation.objects.get(id=request.session['invitation'])
                user = User.objects.create_user(
                  username=form.cleaned_data['username'],
                  first_name=form.cleaned_data['firstname'],
                  last_name=form.cleaned_data['lastname'],
                  password = form.cleaned_data['password2'],
                  email=form.cleaned_data['email']
                )
                # create a profile for the user
                profile = Profile.objects.create(
                   user=user,
                   gender = form.cleaned_data['gender']
                  )

                create_action(user, 'has created an account')
                # Create friendship from user to sender.
                friendship = Friendship(
                  from_friend=user, to_friend=invitation.sender
                )
                friendship.save()
                create_action(user, 'follows', invitation.sender)
                # Create friendship from sender to user.
                friendship = Friendship (
                  from_friend=invitation.sender, to_friend=user
                )
                friendship.save()
                create_action(invitation.sender, 'now follows', user)
                # Delete the invitation from the database and session.
                invitation.delete()
                del request.session['invitation']
                variables = RequestContext(request,{
                  'username': user.username,
                })
                # Sending a welcome message
                subject = "Welcome to PollsPortal"
                template = get_template("polls/welcome_msg.txt")
                context = Context({
                   'name' : user.username,
                   'protocol' : "http",
                   'domain':"ahmad27.pythonanywhere.com",
                })
                message = template.render(context)
                send_mail(
                  subject,message,settings.DEFAULT_FROM_EMAIL,[user.email]
                )
                return render_to_response('registration/register_done.html', variables)
            # create a temporary database for the user
            verification = VerifyRegistration(
              username=form.cleaned_data['username'],
              firstname=form.cleaned_data['firstname'],
              lastname=form.cleaned_data['lastname'],
              gender=form.cleaned_data['gender'],
              email=form.cleaned_data['email'],
              password=form.cleaned_data['password2'],
              verify_code=User.objects.make_random_password(25)
            )
            try:
                verification.send()
                verification.save()
                messages.success(request,
                  'check your email %s to verify your account.' % verification.email
                )
            except:
                messages.error(request,
                  'There was an error creating your account.'
                )
            return HttpResponseRedirect(reverse (
             'polls:reg_incomplete'
            ))

    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('registration/register.html', variables)

def registration_incomplete(request):
    return render(request,'polls/reg_incomplete.html',
       {"content": " "})

def verify_registration(request,code):
    verification = get_object_or_404(VerifyRegistration, verify_code__exact=code)
    # Stores the ID of the object in the user's session
    request.session['verification'] = verification.id
    return HttpResponseRedirect(reverse (
     'polls:complete_register'
    ))

def complete_registration(request):
    try:
        if 'verification' in request.session:
            # Retrieve the verification object.
            verification = \
            VerifyRegistration.objects.get(id=request.session['verification'])
            # Create user account
            user = User.objects.create_user(
              username=verification.username,
              first_name=verification.firstname,
              last_name=verification.lastname,
              password = verification.password,
              email=verification.email,
            )
            # create a profile for the user
            profile = Profile.objects.create(
               user=user,
               gender = verification.gender
              )
            create_action(user, 'has created an account')
            # Delete the verification from the database and session.
            verification.delete()
            del request.session['verification']
            variables = RequestContext(request,{
              'username': user.username,
            })
            # Sending a welcome message
            subject = "Welcome to PollsPortal"
            template = get_template("polls/welcome_msg.txt")
            context = Context({
               'name' : user.username,
               'protocol' : "http",
               'domain':"ahmad27.pythonanywhere.com",
            })
            message = template.render(context)
            send_mail(
              subject,message,settings.DEFAULT_FROM_EMAIL,[user.email]
            )
            return render_to_response('registration/register_done.html', variables)
    except:
        messages.error(request,
         'The verification link has expired'
        )
        return HttpResponseRedirect(reverse (
         'polls:reg_incomplete'
        ))


@login_required(login_url='polls:login')
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    # profile_pic=profile.photo
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                    data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                    data=request.POST,
                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            # since these forms are ModelForm
            user_form.save()
            profile_form.save()
            # create an action for updating profile
            if profile.gender == 'M':
                create_action(request.user, 'updated his profile')
            elif profile.gender == 'F':
                create_action(request.user, 'updated her profile')
            else:
                create_action(request.user, 'updated profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request,
                 'polls/edit_profile.html',
                 {
                 'user_form': user_form,
                 'profile_form': profile_form,
                 #'profile_pic':profile_pic
                 })
    return HttpResponseRedirect(reverse (
     'polls:index',
    ))

def create_anonymous(request):
    if not request.user.is_authenticated():
        user = User.objects.get(username='AnonymousUser')
        if request.method == 'POST':
            form = QuestionSaveForm(request.POST)
            if form.is_valid():
                #create or get question
                question = Question.objects.create(user=user,
                           question_text=form.cleaned_data['question'],
                           category=form.cleaned_data['category_name'],
                           poll_info=form.cleaned_data['info']
                           )
                # create the choices for the question
                choice1 = question.choice_set.create(
                          choice_text=form.cleaned_data['choice1'])
                choice2 = question.choice_set.create(
                          choice_text=form.cleaned_data['choice2']
                )
                if form.cleaned_data['choice3'] != None:
                    choice3 = question.choice_set.create(
                              choice_text=form.cleaned_data['choice3']
                    )
                if form.cleaned_data['choice4'] != None:
                    choice4 = question.choice_set.create(
                              choice_text=form.cleaned_data['choice4']
                    )
                if form.cleaned_data['choice5'] != None:
                    choice5 = question.choice_set.create(
                              choice_text=form.cleaned_data['choice5']
                    )
                if form.cleaned_data['restrict']:
                     question = Question.objects.get(question_text=form.cleaned_data['question'])
                     question.eligibility = form.cleaned_data['restrict']
                     question.eligible_gender = form.cleaned_data['gender']

                question.save()
                messages.success(request,
                  "Thank you for using PollsPortal. Sign up to enjoy more benefits"
                )
                # create an action for creating a poll
                #create_action(request.user, 'created a new poll', question)

                return HttpResponseRedirect(reverse (
                 'index',
                ))
        else:
            form = QuestionSaveForm()
        variables = RequestContext(request, {
            'form': form,
            #'profile_pic':profile_pic
        })
        return render_to_response('polls/question_form.html', variables)


@login_required(login_url='polls:login')
def question_save(request,username):
    # profile = Profile.objects.get(user=request.user)
    # profile_pic=profile.photo
    if request.method == 'POST':
        form = QuestionSaveForm(request.POST)
        if form.is_valid():
            #create or get question
            question = Question.objects.create(user=request.user,
                       question_text=form.cleaned_data['question'],
                       category=form.cleaned_data['category_name'],
                       poll_info=form.cleaned_data['info']
                       )
            # create the choices for the question
            choice1 = question.choice_set.create(
                      choice_text=form.cleaned_data['choice1'])
            choice2 = question.choice_set.create(
                      choice_text=form.cleaned_data['choice2']
            )
            if form.cleaned_data['choice3'] != None:
                choice3 = question.choice_set.create(
                          choice_text=form.cleaned_data['choice3']
                )
            if form.cleaned_data['choice4'] != None:
                choice4 = question.choice_set.create(
                          choice_text=form.cleaned_data['choice4']
                )
            if form.cleaned_data['choice5'] != None:
                choice5 = question.choice_set.create(
                          choice_text=form.cleaned_data['choice5']
                )

            if form.cleaned_data['restrict']:
                 question = Question.objects.get(question_text=form.cleaned_data['question'])
                 question.eligibility = form.cleaned_data['restrict']
                 question.eligible_gender = form.cleaned_data['gender']
            #instruction = form.cleaned_data['instruction']
            #share on the main page if requested
            #if form.cleaned_data['share']:
            #     shared_question, created = SharedQuestion.objects.get_or_create(
            #       question=question
            #     )
            #     if created:
            #         #add current users to list of voters
            #         shared_question.users_voted.add(request.user)
            #         shared_question.save()
            # save question to the database
            question.save()
            messages.success(request,
              "You've successfully created poll no {}".format(question.id)
            )
            # create an action for creating a poll
            create_action(request.user, 'created a new poll', question)

            return HttpResponseRedirect(reverse (
             'polls:user_page', args=(request.user.username,)
            ))
    else:
        form = QuestionSaveForm()
    variables = RequestContext(request, {
        'form': form,
        #'profile_pic':profile_pic
    })
    return render_to_response('polls/question_form.html', variables)

def search_page(request):
    form=SearchForm()
    questions= []
    users=[]
    show_search_results = False
    if request.GET.__contains__('query'):
        show_search_results = True
        query=request.GET['query'].strip()
        if query:
            keywords = query.split()
            q = Q()
            for keyword in keywords:
                q1 = q & Q(question_text__icontains=keyword) # to search by question
                q2 = Q(user__username__icontains=keyword) # To search by username
                q3 = Q(category__icontains=keyword) # To search by category
                q4 = Q(id__iexact=keyword)
                q5 = Q(first_name__icontains=keyword)
                q6 = Q(last_name__icontains=keyword)
                q7 = Q(username__icontains=keyword)
            form = SearchForm({'query':query})
            questions = Question.objects.filter(q1|q2|q3|q4)
            users = User.objects.filter(q5|q6|q7)
    variables = RequestContext(request,{
         'form':form,
         'questions':questions,
         'users':users,
         #'profile_pic':profile_pic,
         'show_search_results':show_search_results,
         'show_user':True,
         'show_category':True,
    })
    if request.GET.__contains__('ajax'):
        if len(questions)> 8:
            more_view = True
        else: more_view = False
        questions = questions[:8]
        return render(request,'polls/search_list_ajax.html',
        {
             'form':form,
             'questions':questions,
             'users':users,
             #'profile_pic':profile_pic,
             'show_search_results':show_search_results,
             'show_user':True,
             'show_category':True,
             'more_view': more_view
        })
    return render_to_response('polls/search.html', variables)

def category_page(request,category_name):
    questions = Question.objects.filter(category__iexact=category_name)

    paginator = Paginator(questions, ITEMS_PER_PAGE)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        questions = paginator.page(1).object_list
    try:
        questions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        questions = paginator.page(paginator.num_pages).object_list
    # The variables to render to the template
    variables = RequestContext(request, {
       'questions': questions,
       #'profile_pic': profile_pic,
       #'username': username,
       'show_paginator': paginator.num_pages > 1,
       'has_previous': paginator.page(page).has_previous(), # returns True or False
       'has_next': paginator.page(page).has_next(),  # returns True or False
       'page': page,
       'pages': paginator.num_pages,
       'next_page' : page + 1,
       'prev_page' : page - 1,
       'category_name':category_name,
       'show_user':True,
       'show_category':False,
    })
    return render_to_response('polls/categories.html', variables)

def category_count(request):
    questions = Question.objects.all()
    gen_count=0
    soc_count=0
    pol_count=0
    rel_count=0
    nut_count=0
    hlt_count=0
    edu_count=0
    category_details={}
    for question in questions:
        if question.category =="General":
            gen_count += 1
            category_details.update({'General':gen_count})
        elif question.category =='Social':
            soc_count += 1
            category_details.update({'Social':soc_count})
        elif question.category =='Politics':
            pol_count += 1
            category_details.update({'Politics':pol_count})
        elif question.category =='Religion':
            rel_count += 1
            category_details.update({'Religion':rel_count})
        elif question.category =='Nutritional':
            nut_count += 1
            category_details.update({'Nutritional':nut_count})
        elif question.category =='Education':
            edu_count += 1
            category_details.update({'Education':edu_count})
        elif question.category =='Health':
            hlt_count += 1
            category_details.update({'Health':hlt_count})
        else:
            pass
    fig = Figure(figsize=(6,6))
    # fig.suptitle('Polls by categories', fontsize=14, fontweight='bold')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    #explode=[0,0.1,0.1,0.1,0.2,0.1,0]
    ax.pie(list(category_details.values()),
           labels=list(category_details.keys()),
           #explode,
           autopct='%1.1f%%'
           )
    # ax.set_xticks(np.arange(len(x))+0.4)
    # ax.set_xticklabels(x, rotation=45)
    # ax.set_ylabel('Total Votes')
    #ax.set_title('Categories of Polls')

    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def features(request):
    return render (request,'polls/features.html',{
        'head_title': "Polls Portal",
    })

def popular_polls(request):
    # if request.user.is_authenticated():
    #     profile = Profile.objects.get(user=request.user)
    #     profile_pic = profile.photo
    # else:
    #     profile_pic = ""
    popular_polls = Question.objects.filter(total_votes__gte=5)
    popular_polls = popular_polls.order_by('-total_votes')
    paginator = Paginator(popular_polls, 5)  # paging the no of items
    try:
        page = int(request.GET['page'])
    except:
        page = 1
        # if page is not an integer, deliver first page
        questions = paginator.page(1).object_list
    try:
        questions = paginator.page(page).object_list
    except:
        # if page is out of range, deliver last page of results
        questions = paginator.page(paginator.num_pages).object_list
    # The variables to render to the template
    variables = RequestContext(request, {
       'questions': questions,
       #'profile_pic':profile_pic,
       #'username': username,
       'show_paginator': paginator.num_pages > 1,
       'has_previous': paginator.page(page).has_previous(), # returns True or False
       'has_next': paginator.page(page).has_next(),  # returns True or False
       'page': page,
       'pages': paginator.num_pages,
       'next_page' : page + 1,
       'prev_page' : page - 1,
       'show_user':True,
       'show_category':True,
    })
    return render_to_response('polls/popular_polls.html', variables)

def friends_page(request,username):
    user = get_object_or_404(User, username=username)

    following = \
        [friendship.to_friend for friendship in user.friend_set.all()]
    # This list questions by users that exists in friends above
    q1 = Q(user__in=following)
    followers = \
        [friendship.from_friend for friendship in user.to_friend_set.all()]
    # This list questions by users that exists in friends above
    q2 = Q(user__in=followers)
    questions = Question.objects.filter(q1 | q2).order_by('-id')[:10]
    variables = RequestContext(request,{
        'username': username,
        #'profile_pic':profile_pic,
        'following': following,
        'followers': followers,
        'questions': questions,
        'show_user': True,
        'show_category': True,
    })
    if request.is_ajax():
        return render_to_response('polls/friends_page_ajax.html', variables)
    return render_to_response('polls/friends_page.html', variables)

@login_required(login_url='polls:login')
def friend_follow(request):
    # user_username = request.POST.get('username')
    #action = request.POST.get('action')
    if request.GET.__contains__('username'):
        try:
            user = get_object_or_404(User, username=request.GET['username'])
            friendship = Friendship(
               from_friend=request.user, to_friend=user)
            friendship.save()
            messages.success(request,
              'You now follow %s.' % user.username
            )
            # create an action after adding a friend
            create_action(request.user, 'is now following', user)
            try:
                my_settings = AccountSettings.objects.get(user=user)
                if my_settings.follow_notify:
                    subject = "{} now follows you".format(request.user.username)
                    template = get_template("polls/follow_notification.txt")
                    context = Context({
                       'name' : user.username,
                       'follower': request.user.username,
                       'protocol' : "http",
                       'domain':"ahmad27.pythonanywhere.com",
                    })
                    message = template.render(context)
                    send_mail(
                      subject,message,"PollsPortal <notification@pollsportal.com>",[user.email]
                    )
            except:
                pass
        except:
            Friendship.objects.filter(
                       from_friend=request.user,
                       to_friend = user).delete()
            messages.error(request,
              "You now unfollow %s " % user.username
            )
        return HttpResponseRedirect(reverse (
         'polls:friends', args=(request.user,)
        ))
    else:
        raise Http404

@login_required(login_url='polls:login')
def friend_invite(request):
    # profile = Profile.objects.get(user=request.user)
    # profile_pic=profile.photo
    if request.method == 'POST':
        form = FriendInviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(
              name=form.cleaned_data['name'],
              email=form.cleaned_data['email'],
              code = User.objects.make_random_password(20),
              sender = request.user
            )
            invitation.save()
            try:
                invitation.send()
                messages.success(request,
                  'An invitation was sent to %s.' % invitation.email
                )
            except:
                icon = "fa fa-warning"
                messages.error(request,
                  'There was an error while sending the invitation.'
                )
            return HttpResponseRedirect(reverse (
             'polls:friend_invite',
            ))
    else:
        form = FriendInviteForm()
    variables = RequestContext(request,{
      'form': form,
      #'profile_pic':profile_pic
    })
    return render_to_response('polls/friend_invite.html', variables)

def friend_accept(request,code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    # Stores the ID of the object in the user's session
    request.session['invitation'] = invitation.id
    return HttpResponseRedirect(reverse (
     'polls:register'
    ))

def image_poll(request):
    return render(request,'polls/image_poll_index.html',{
      'head_title': 'Image Polls',
    })

def feedback_page(request):
    if request.method == 'POST':
        feedback_form = FeedBackForm(data=request.POST) # Post a comment
        if feedback_form.is_valid():
            # Now create a feedback object but not yet saved to database
            new_feedback = feedback_form.save(commit=False)

            new_feedback.user = request.user
            # now save the comment to the database
            new_feedback.save()

            messages.success(request,
              "Message submitted! Thank you."
            )
            return HttpResponseRedirect(reverse (
             'polls:dashboard'
            ))
        else:
            messages.error(request,
              "Please write us a message! You can't submit a blank form"
            )
    else:
        feedback_form = FeedBackForm()
    return render(request, 'polls/feedback.html',
                 {

                  'feedback_form': feedback_form
                 })

def my_settings(request):
    acct_settings = AccountSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        settings_form = AccountSettingsForm(data=request.POST) # Post a comment
        if settings_form.is_valid():
            # Now create a settings object but not yet saved to database
            new_settings = settings_form.save(commit=False)
            new_settings.user = request.user
            # new_settings = AccountSettings.objects.update_or_create(user=request.user,
            #     notify=settings_form.cleaned_data['vote_notification'])
            # new_settings.notify = settings_form.cleaned_data['vote_notification']
            new_settings.save()

            return HttpResponseRedirect(reverse (
             'index'
            ))
    else:
        settings_form = AccountSettingsForm(instance=request.user)
    return render(request, 'polls/settings_form.html',
                 {

                  'settings_form': settings_form
                 })
