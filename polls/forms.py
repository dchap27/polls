import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from polls.models import Question
from polls.models import Profile
from polls.models import Comment, FeedBack


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    firstname = forms.CharField(label='Firstname',max_length=20)
    lastname = forms.CharField(label='Lastname',max_length=20)
    gender = forms.ChoiceField(label='gender',choices=Profile.GENDER)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(
      label='Password',
      min_length=6,
      widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
    label='Password (Again)',
    widget=forms.PasswordInput()
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain \
            alphanumeric characters and the underscore.'
        )
        # To restrict username i.e reserved names!!
        if username in ['naijapolls',"Naija",'Naijapolls','pollsnaija']:
            raise forms.ValidationError('Username is already taken')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return email
        raise forms.ValidationError('Email is already registered.')

    # def clean_password1(self):
    #     password1 = self.cleaned_data['password1']
    #     if len(password1) < 6:
    #         raise forms.ValidationError('password must be at least 6 characters')
    #     return password1

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender','date_of_birth',
                 'state_of_origin','state_of_residence',
                 'city_of_residence'
                 )

class QuestionSaveForm(forms.Form):
    political = 'Politics'
    religion ='Religion'
    social = 'Social'
    educational ='Education'
    health = 'Health'
    nutrition = 'Nutritional'
    general = 'General'
    CATEGORY_OF_POLLS = (
      (None,'Select a category'),
      (political,'Politics'),
      (religion, 'Religion'),
      (social, 'Social'),
      (educational,'Education'),
      (health, 'Health/Medical'),
      (nutrition, 'Nutritional'),
      (general, 'General discussion'),
    )
    question = forms.CharField(max_length=160,label= 'Poll Question')
    # import the choice field created in the models.py
    category_name = forms.ChoiceField(label="category",choices = CATEGORY_OF_POLLS)
    choice1 = forms.CharField(max_length=60,label='option 1')
    choice2 = forms.CharField(max_length=60,label='option 2')
    choice3 = forms.CharField(max_length=60,label='option 3 (optional)',
                    required=False)
    info = forms.CharField(label='Additional poll info (optional)',
                    required=False,
                    widget=forms.Textarea)
    # share = forms.BooleanField(label='Enable eligibilty',
    #                        required=False)
    # gender = forms.ChoiceField(label="Gender",choices=Profile.GENDER)

    class Media:
        css = {
             'all': ('polls/style.css')
        }

    def clean_question(self):
        question = self.cleaned_data['question']
        try:
            Question.objects.get(question_text=question)
        except ObjectDoesNotExist:
            return question
        raise forms.ValidationError("Sorry! Poll question already created!!")

    def clean_choice3(self):
        choice3 = self.cleaned_data['choice3']
        if len(choice3) == 0:
            choice3 = 'undecided'
        return choice3

class SearchForm(forms.Form):
    query = forms.CharField(
           label='Enter a keyword to search for',
           widget=forms.TextInput(attrs={'size': 32})
    )

class FriendInviteForm(forms.Form):
    name = forms.CharField(label="Friend's name")
    email = forms.EmailField(label="Friend's Email")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return email
        raise forms.ValidationError(
            '{} is already a registered user.'.format(email))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class FeedBackForm(forms.ModelForm):
    class Meta:
        model= FeedBack
        fields = ('feedback_text',)
