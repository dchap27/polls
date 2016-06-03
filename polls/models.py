from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings # used to create user profile
# To enable sending of email Invitation
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse # use for get_absolute_url


class Profile(models.Model):
    STATE_OF_ORIGIN=(
      (None,'Select a State'),
      ('Abuja','FCT'),('Abia','Abia'),('Adamawa','Adamawa'),('Akwa ibom','Akwa Ibom'),
      ('Anambra','Anambra'),('Bauchi','Bauchi'),('Bayelsa','Bayelsa'),
      ('Benue','Benue'),('Borno','Borno'),('Cross River','Cross River'),
      ('Delta','Delta'),('Ebonyi','Ebonyi'),('Edo','Edo'),('Ekiti','Ekiti'),
      ('Enugu','Enugu'),('Gombe','Gombe'),('Imo','Imo'),('Jigawa','Jigawa'),
      ('Kaduna','Kaduna'),('Kano','Kano'),('Katsina','Katsina'),('Kebbi','Kebbi'),
      ('Kogi','Kogi'),('Kwara','Kwara'),('Lagos','Lagos'),('Nasarawa','Nasarawa'),
      ('Niger','Niger'),('Ogun','Ogun'),('Ondo','Ondo'),('Osun','Osun'),
      ('Oyo','Oyo'),('Plateau','Plateau'),('Rivers','Rivers'),('Sokoto','Sokoto'),
      ('Taraba','Taraba'),('Yobe','Yobe'),('Zamfara','Zamfara')
    )
    CITY = (
         (None,'Select a city'),('Abuja','Abuja'),('Abeokuta','Abeokuta'),
         ('Akure','Akure'),('Benin','Benin'),('Calabar','Calabar'),('Enugu','Enugu'),
         ('Ibadan','Ibadan'),('Ife','Ife'),('Ilorin','Ilorin'),('Jos','Jos'),
         ('Kaduna','Kaduna'),('Kano','Kano'),('Katsina','Katsina'),('Lagos','Lagos'),
         ('Maiduguri','Maiduguri'),('Makurdi','Makurdi'),('Minna','Minna'),
         ('Onitsha','Onitsha'),('Port Harcourt','Port Harcourt'),('Sokoto','Sokoto'),
         ('Warri','Warri'),('Zaria','Zaria'),('Other','Other')
    )
    GENDER = (
      (None,'Select gender'),
      ('M','Male'),
      ('F','Female')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,primary_key=True)
    date_of_birth = models.DateField(blank=True, null=True)
    state_of_origin = models.CharField(max_length=15,choices=STATE_OF_ORIGIN,
                      blank=True,null=True)
    state_of_residence = models.CharField(max_length=15,choices=STATE_OF_ORIGIN,
                      blank=True,null=True)
    city_of_residence = models.CharField(max_length=15, choices=CITY,null=True,
                      blank=True)
    gender = models.CharField(max_length=6,choices=GENDER,
                      blank=True,null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return 'Profile for {}'.format(self.user.username)

    def set_photo(self):
        _photo = self.photo
        if not _photo:
            self.photo="/static/polls/images/profile_pix/2.jpg"
        return self.photo

class Question(models.Model):
    user = models.ForeignKey(User,null=True)
    question_text = models.CharField(max_length=160)
    category = models.CharField(max_length=22,default='General')
    total_votes = models.IntegerField(default=0)
    users_voted= models.ManyToManyField(User,null=True,blank=True, related_name='voters')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    poll_info = models.CharField(max_length=200,null=True,blank=True)
    eligibility=models.BooleanField(default=False)
    eligible_gender = models.CharField(max_length=10,null=True,blank=True)

    def __str__(self):
        return "{}".format(self.question_text)

    def was_published_recently(self):
        return self.publish >= timezone.now() - timedelta(days=1)

    def get_absolute_url(self):
        return reverse('polls:detail', args=[self.id])

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=160)
    votes=models.IntegerField(default=0)
    m_votes=models.IntegerField(default=0)
    f_votes=models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Friendship(models.Model):
    from_friend = models.ForeignKey(User,
        related_name='friend_set'   #  this is like Following
        )
    to_friend = models.ForeignKey(User,
        related_name ='to_friend_set'  #this refer to followers
        )
    created = models.DateTimeField(default=timezone.now,db_index=True,)

    def __str__(self):
        return "{} follows {}".format(
        self.from_friend.username,self.to_friend.username
        )
    class Meta:
        unique_together = (('to_friend', 'from_friend'),)
        #ordering = ('-created',)

class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    sender = models.ForeignKey(User)

    def __str__(self):
        return "{}, {}".format(self.sender.username,self.email)

    def send(self):
        subject = 'Invitation to join PollsPortal'
        link = 'http://{}/polls/friend/accept/{}/'.format(settings.SITE_HOST,
                                            self.code,
        )
        template = get_template("polls/invitation_email.txt")
        context = Context({
           'name' : self.name,
           'link' : link,
           'sender': self.sender.username,
        })
        message = template.render(context)
        send_mail(
          subject, message,settings.DEFAULT_FROM_EMAIL, [self.email]
        )

class VerifyRegistration(models.Model):
    username = models.CharField(max_length=30)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    gender = models.CharField(max_length=6)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    verify_code=models.CharField(max_length=25)

    def __str__(self):
        return "{}, {}".format(self.username,self.email)

    def send(self):
        subject = 'Confirm your email'
        link = 'http://{}/polls/verify/email/{}/ok'.format(settings.SITE_HOST,
                                            self.verify_code,
        )
        home='http://ahmad27.pythonanywhere.com/'
        template = get_template("polls/verify_reg_email.html")
        context = Context({
           'link' : link,
           'home': home
        })
        message = template.render(context)
        send_mail(
          subject, message,settings.DEFAULT_FROM_EMAIL, [self.email]
        )

class Comment(models.Model):
    question = models.ForeignKey(Question, related_name='comments')
    name = models.CharField(max_length=25)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return '{}'.format(self.question)

    def get_absolute_url(self):
        return reverse('polls:results', args=[self.question.id])

# Add the following to User class model dynamically ( but this is not a recommended way to add field to model class)
User.add_to_class('following', models.ManyToManyField('self',
                                                      through=Friendship,
                                                      related_name='followers',
                                                      symmetrical=False))

class FeedBack(models.Model):
    user=models.ForeignKey(User)
    feedback_text=models.TextField()
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.feedback_text)

class AccountSettings(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    vote_notify = models.BooleanField(default=True)
    follow_notify = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Account settin" # To display plural of category


# class Category(models.Model):
#     question = models.ForeignKey(Question,null=True, on_delete=models.CASCADE)
#     category = models.CharField(max_length=22,
#                              primary_key=True)
#                              #The primary_key was set to True for easy referencing
#                              #otherwise id will be used
#     class Meta:
#         verbose_name_plural = "Categories" # To display plural of category
#
#     def __str__(self):
#         return self.category
