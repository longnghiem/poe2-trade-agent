import { apiFetch } from './client'
import { type Token, tokenSchema, type User, userSchema } from './schemas'

/** Calls `POST /auth/login` with the form FastAPI expects; a wrong password throws a 401. */
export function loginUser(username: string, password: string): Promise<Token> {
  return apiFetch('/auth/login', tokenSchema, {
    method: 'POST',
    body: new URLSearchParams({ username, password }),
  })
}

/**
 * Calls `POST /auth/register` with the token of the human check. It returns the new user, not a
 * token, so log in afterwards.
 */
export function registerUser(
  username: string,
  password: string,
  turnstileToken: string,
): Promise<User> {
  return apiFetch('/auth/register', userSchema, {
    method: 'POST',
    body: JSON.stringify({ username, password, turnstile_token: turnstileToken }),
  })
}

/** Calls `GET /users/current_user`: the user the stored token belongs to. */
export function fetchCurrentUser(): Promise<User> {
  return apiFetch('/users/current_user', userSchema)
}
