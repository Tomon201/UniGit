from django.contrib import admin
from .models import Repository, Commit, Profile

@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'full_name')
    search_fields = ('name', 'owner__username')

@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ('sha', 'repository', 'message')
    search_fields = ('sha', 'repository__name')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'leetcode_username', 'github_username', 'leetcode_rating', 'problems_solved')
    search_fields = ('user__username', 'leetcode_username', 'github_username')