import json
import os
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from .models import Repository, Commit, Profile
from .updater import update_github_data
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Count
from allauth.socialaccount.models import SocialAccount
load_dotenv()
CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')


def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql/"
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    count
                }
            }
        }
    }
    """
    variables = {"username": username}
    response = requests.post(url, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        data = response.json()
        try:
            # Считаем задачи (обычно это второй элемент в списке - All)
            count = data['data']['matchedUser']['submitStats']['acSubmissionNum'][0]['count']
            return count
        except:
            return None
    return None

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
    profiles = Profile.objects.all()
    sort_by = request.GET.get('sort', 'unigit') # Дефолтная сортировка

    if sort_by == 'repos':
        profiles = profiles.annotate(repo_count=Count('user__repositories')).order_by('-repo_count')
    elif sort_by == 'lc':
        profiles = profiles.order_by('-leetcode_rating')
    else: # unigit
        profiles = profiles.order_by('-unigit_rating')

    return render(request, 'index.html', {'profiles': profiles})


# Новая функция для детальной страницы
def user_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    github_account = SocialAccount.objects.filter(user=profile.user, provider='github').first()

    github_url = None
    if github_account:
        github_url = github_account.extra_data.get('html_url')

    return render(request, 'user_detail.html', {
        'profile': profile,
        'github_url': github_url,
    })


@csrf_exempt
def github_webhook(request):
    if request.method != 'POST':
        return HttpResponse("Only POST allowed", status=405)

    data = json.loads(request.body)

    if 'repository' not in data:
        return HttpResponse("No repository data", status=200)

    repo_owner_login = data['repository']['owner']['login']
    repo_name = data['repository']['name']
    repo_full_name = data['repository']['full_name']

    # Пытаемся найти профиль. Если не нашли — выходим сразу!
    try:
        profile = Profile.objects.get(github_username=repo_owner_login)
        user = profile.user
    except Profile.DoesNotExist:
        # Юзера нет, игнорируем запрос (но возвращаем 200, чтобы GitHub не спамил ошибками)
        return HttpResponse("User not registered in UniGit, ignoring", status=200)

    # Если мы дошли сюда, значит пользователь найден. Работаем дальше:
    repo, created = Repository.objects.get_or_create(
        full_name=repo_full_name,
        defaults={'name': repo_name, 'owner': user}
    )

    if 'commits' in data:
        for commit_data in data['commits']:
            message = commit_data.get('message', 'No message')
            sha = commit_data.get('id')

            Commit.objects.get_or_create(
                repository=repo,
                sha=sha,
                defaults={'message': message}
            )

    return HttpResponse("Data saved!", status=200)


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    # 1. Обработка смены ника LeetCode
    if request.method == 'POST':
        username = request.POST.get('leetcode_username', '').strip()
        profile.leetcode_username = username if username else None
        profile.save()
        messages.success(request, "Данные обновлены!")
        return redirect('profile')

    # 2. Сбор статистики
    repo_count = Repository.objects.filter(owner=request.user).count()
    commit_count = Commit.objects.filter(repository__owner=request.user).count()

    lc_solved = 0
    if profile.leetcode_username:
        lc_solved = get_leetcode_stats(profile.leetcode_username) or 0
        profile.problems_solved = lc_solved

    # 3. Расчет и сохранение рейтингов
    profile.unigit_rating = int((repo_count * 5) + (commit_count * 0.5))
    profile.leetcode_rating = int(lc_solved * 3)
    profile.save()

    return render(request, 'profile.html', {
        'profile': profile,
        'stats': {
            'github_repos': repo_count,
            'github_commits': commit_count,
            'lc_solved': lc_solved
        }
    })