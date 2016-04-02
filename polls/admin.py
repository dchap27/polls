from django.contrib import admin
from django.contrib.auth.models import User
from polls.models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','gender','date_of_birth','state_of_origin','photo')


class ChoiceInline(admin.TabularInline):
    model= Choice
    extra=1

class QuestionAdmin(admin.ModelAdmin):
    list_display=('user','question_text','category','total_votes','publish')
    list_filter = ('user','question_text')
    search_fields = ('question_text',)
    inlines = [ChoiceInline]

class FrienshipAdmin(admin.ModelAdmin):
    list_display = ('from_friend','to_friend',)

class InvitationAdmin(admin.ModelAdmin):
     list_display=('sender','email')

class CommentAdmin(admin.ModelAdmin):
    list_display=('name','question','created','active')
    list_filter=('active','created','updated')
    search_fields=('name','body')


admin.site.register(Profile,ProfileAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Friendship,FrienshipAdmin)
admin.site.register(Invitation,InvitationAdmin)
admin.site.register(Comment,CommentAdmin)
