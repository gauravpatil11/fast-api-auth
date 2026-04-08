# FastAPI Auth Service

Run the app with:

```powershell
uvicorn src.app:app --reload
```

Authentication flow:

- `POST /auth/register` accepts JSON with `username`, `email`, and `password`.
- `POST /auth/login` accepts JSON with `email` and `password`.
- `POST /auth/forgot-password` accepts JSON with `email`, then sends a password reset OTP.
- `POST /auth/reset-password` accepts JSON with `email`, `otp`, and `new_password`.
- `GET /user/profile` returns the authenticated user profile.
- `PUT /user/profile` updates the authenticated user's `username` and/or `email`.
- `POST /user/change-password` accepts JSON with `current_password` and `new_password`.
- `GET /user/userlist` is accessible only to admin users.
- Protected routes expect `Authorization: Bearer <access_token>`.
