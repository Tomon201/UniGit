from apscheduler.schedulers.background import BackgroundScheduler
import requests
from .models import Repository, Commit, Profile
from allauth.socialaccount.models import SocialToken


def update_github_data():
    print("--- Запуск обновления ---")
    tokens = SocialToken.objects.filter(account__provider='github')

    for token in tokens:
        user = token.account.user

        # 1. Синхронизируем никнейм из GitHub
        profile, created = Profile.objects.get_or_create(user=user)
        if not profile.github_username:
            github_login = token.account.extra_data.get('login')
            if github_login:
                profile.github_username = github_login
                profile.save()

        # 2. Получаем репозитории
        access_token = token.token
        headers = {'Authorization': f'token {access_token}'}
        response = requests.get('https://api.github.com/user/repos', headers=headers)

        if response.status_code == 200:
            repos = response.json()
            fetched_full_names = []  # Список для отслеживания существующих репо

            for repo_data in repos:
                repo, _ = Repository.objects.get_or_create(
                    full_name=repo_data['full_name'],
                    defaults={'name': repo_data['name'], 'owner': user}
                )
                fetched_full_names.append(repo_data['full_name'])

                # 3. Получаем коммиты для ЭТОГО репозитория
                commits_url = f"https://api.github.com/repos/{repo_data['full_name']}/commits"
                commits_response = requests.get(commits_url, headers=headers)

                if commits_response.status_code == 200:
                    for c_data in commits_response.json():
                        sha = c_data.get('sha')
                        message = c_data.get('commit', {}).get('message', 'No message')

                        Commit.objects.update_or_create(
                            sha=sha,
                            defaults={'repository': repo, 'message': message}
                        )

            # 4. ОЧИСТКА: Удаляем репозитории, которые больше не существуют на GitHub
            # Оставляем только те, что есть в fetched_full_names
            Repository.objects.filter(owner=user).exclude(full_name__in=fetched_full_names).delete()

    print("--- Обновление завершено ---")


def start():
    scheduler = BackgroundScheduler()
    # Запускаем обновление (сейчас стоит 30 секунд для тестов)
    scheduler.add_job(update_github_data, 'interval', seconds=10)
    scheduler.start()