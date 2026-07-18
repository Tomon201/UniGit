from apscheduler.schedulers.background import BackgroundScheduler
import requests
from .models import Repository, Commit
from allauth.socialaccount.models import SocialToken


def update_github_data():
    print("--- Запуск обновления ---")
    tokens = SocialToken.objects.filter(account__provider='github')

    for token in tokens:
        user = token.account.user
        access_token = token.token
        headers = {'Authorization': f'token {access_token}'}

        # 1. Получаем репозитории
        response = requests.get('https://api.github.com/user/repos', headers=headers)

        if response.status_code == 200:
            repos = response.json()
            for repo_data in repos:
                repo, _ = Repository.objects.get_or_create(
                    full_name=repo_data['full_name'],
                    owner=user,  # 2. Указываем владельца
                    defaults={'name': repo_data['name']}
                )

                # 2. Получаем коммиты для ЭТОГО репозитория
                commits_url = f"https://api.github.com/repos/{repo_data['full_name']}/commits"
                commits_response = requests.get(commits_url, headers=headers)

                if commits_response.status_code == 200:
                    for c_data in commits_response.json():
                        sha = c_data['sha']
                        message = c_data['commit']['message']
                        # Сохраняем в базу (обновляем если есть, создаем если нет)
                        Commit.objects.update_or_create(
                            sha=sha,
                            defaults={'repository': repo, 'message': message}
                        )
    print("--- Обновление завершено ---")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_github_data, 'interval', hours=3)
    scheduler.start()