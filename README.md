# Moviexpert

Дневник фильмов в духе Letterboxd на Django. Фронтенд — только Django-шаблоны и CSS, без JavaScript.

## Возможности
- Каталог: поиск, фильтр по жанру, сортировка
- Кейс «Случайный фильм»: анимация открытия, редкость зависит от числа голосов на TMDB
- Регистрация, вход, выход
- Личные отметки: избранное, смотреть позже, просмотрено
- Оценка 1–10 и обзор, лайки и комментарии к обзорам
- Пользовательские списки (публичные и личные)
- Импорт фильмов из TMDB, загрузка своих постеров или ссылка на постер
- Публичный профиль: отметки, обзоры, списки
- Страницы «Разработчики» и «Поддержать проект» (донаты через ЮMoney)

## Запуск
```
pip install -r requirements.txt
python manage.py makemigrations main
python manage.py migrate
python manage.py seed             # демо-фильмы (по желанию)
python manage.py import_tmdb --pages 10   # 200 фильмов из TMDB (нужен TMDB_API_KEY)
python manage.py createsuperuser
python manage.py runserver
```

## Настройка (переменные окружения)
| Переменная | Для чего |
|---|---|
| `TMDB_API_KEY` | импорт фильмов из TMDB (ключ API v3 или токен v4): themoviedb.org/settings/api |
| `YOOMONEY_WALLET` | номер кошелька ЮMoney для донатов (11–20 цифр) |

Linux/macOS: `export TMDB_API_KEY=... YOOMONEY_WALLET=...`
Windows (PowerShell): `$env:TMDB_API_KEY="..."; $env:YOOMONEY_WALLET="..."`

