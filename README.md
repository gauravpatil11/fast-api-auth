# FastAPI Auth Service

Run the app with:

```powershell
uvicorn src.app:app --reload
```

Authentication flow:

- `POST /auth/register` accepts JSON with `username`, `email`, and `password`.
- `POST /auth/login` accepts either JSON or OAuth2 password form fields with `username` and `password`.
- Protected routes expect `Authorization: Bearer <access_token>`.
