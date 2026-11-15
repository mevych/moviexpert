# 🍿 Moviexpert 🎥

Moviexpert is an online social cataloging service for film. It allows members to log, rate, review films, keep a diary of films watched, maintain watchlists, make curated lists.

## ✨ Features ✨ 
- Catalog: search, filter by genre, sort
- Random Movie Case
- Check-in, login, exit
- Personal Marks: Favorites, Watch Later, Viewed
- Rating 1-10 and review, likes and comments on reviews
- Custom lists (public and private)
- Public profile: marks, reviews, lists
- 🛠️ Work in Progress 🛠️ 
## 📋 Plans for the Future 📋
- Add a recommendation system
### 📷 Preview 📷
_Main Page_:
<img width="2556" height="1267" alt="Screenshot_1" src="https://github.com/user-attachments/assets/9b5654d3-9d8f-426e-a5a3-39f7a0c8636b" />
_Page with random films_:
<img width="2557" height="1269" alt="Screenshot_2" src="https://github.com/user-attachments/assets/f5e5d9c9-da76-4066-ae1c-224c0236f3b3" />
_Movie Page_:
<img width="1280" height="636" alt="image" src="https://github.com/user-attachments/assets/9a1b121b-9c7f-4ba4-85b6-ed70f1291732" />


#### LocalHost
```
pip install -r requirements.txt
python manage.py makemigrations main
python manage.py migrate
python manage.py seed             # demo movies
python manage.py import_tmdb --pages 10   # 200 films from TMDB (need a TMDB_API_KEY)
python manage.py createsuperuser
python manage.py runserver
```

#### Setup (environment variables)
| Variable | For what |
|---|---|
| `TMDB_API_KEY` | import movies from TMDB (API key v3 or token v4): themoviedb.org/settings/api |
| `YOOMONEY_WALLET` | YooMoney wallet number for donations (11–20 digits) |

- Linux/macOS: `export TMDB_API_KEY=... YOOMONEY_WALLET=...`
- Windows (PowerShell): `$env:TMDB_API_KEY="..."; $env:YOOMONEY_WALLET="..."`


