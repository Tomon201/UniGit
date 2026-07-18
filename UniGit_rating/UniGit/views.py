import json
import os
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from .models import Repository, Commit
from .updater import update_github_data

load_dotenv()
CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


def github_login(request):
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return redirect(url)


def github_callback(request):
    code = request.GET.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code
    }
    headers = {'Accept': 'application/json'}
    response = requests.post("https://github.com/login/oauth/access_token", data=data, headers=headers)
    token = response.json().get('access_token')

    return HttpResponse(f"Успех! Твой токен: {token}")

def show_rating(request):
    # Теперь берем из модели Commit
    update_github_data()
    commits = Commit.objects.all().order_by('-id')[:20]
    return render(request, 'index.html', {'commits': commits})


@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if 'commits' in data:
            repo_full_name = data['repository']['full_name']
            repo_name = data['repository']['name']

            repo, created = Repository.objects.get_or_create(
                full_name=repo_full_name,
                defaults={'name': repo_name}
            )

            for commit_data in data['commits']:
                message = commit_data.get('message', 'No message')

                Commit.objects.create(
                    repository=repo,
                    message=message
                )

        return HttpResponse("Data saved!", status=200)

    return HttpResponse("Only POST requests are allowed.", status=405)

