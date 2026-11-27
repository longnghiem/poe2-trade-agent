import type { z } from 'zod'
import { createLogger } from '../lib/logger'

const logger = createLogger('api')

const API_PREFIX = '/api/v1'

/** Key under which the login token is kept in localStorage. */
export const TOKEN_KEY = 'poe2.token'

/** Error thrown by {@link apiFetch} for an answer that isn't 2xx; `message` is the backend's `detail`. */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

/**
 * Calls the backend at `/api/v1` + `path`, adds the login token, and checks the JSON answer with
 * `schema`. Pass `null` as `schema` for answers without a body (204).
 */
export async function apiFetch<T>(
  path: string,
  schema: z.ZodType<T>,
  init?: RequestInit,
): Promise<T>
export async function apiFetch(path: string, schema: null, init?: RequestInit): Promise<void>
export async function apiFetch<T>(
  path: string,
  schema: z.ZodType<T> | null,
  init: RequestInit = {},
): Promise<T | void> {
  const method = init.method ?? 'GET'
  const token = localStorage.getItem(TOKEN_KEY)
  const headers = new Headers(init.headers)
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  // A string body is JSON. Other bodies (the login form) set their own Content-Type.
  if (typeof init.body === 'string') {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response
  try {
    response = await fetch(API_PREFIX + path, { ...init, headers })
  } catch (error) {
    logger.error(`${method} ${path} failed: network error`, error)
    throw error
  }

  if (!response.ok) {
    if (response.status >= 500) {
      logger.error(`${method} ${path} → ${response.status}`)
    }
    // A 401 with a token means the login has expired. Without a token it's a wrong password.
    if (response.status === 401 && token) {
      localStorage.removeItem(TOKEN_KEY)
      window.location.assign('/login')
    }
    const body: unknown = await response.json().catch(() => null)
    throw new ApiError(response.status, errorMessage(body, response.status))
  }

  if (schema === null) {
    return
  }
  const result = schema.safeParse(await response.json())
  if (!result.success) {
    logger.error(`${method} ${path}: the answer doesn't match the schema`, result.error.issues)
    throw new ApiError(response.status, "The server sent an answer this page can't read.")
  }
  return result.data
}

/** The backend's `detail` if it's a text; validation errors (a list) get a general message. */
function errorMessage(body: unknown, status: number): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    if (typeof body.detail === 'string') {
      return body.detail
    }
  }
  return `Request failed (${status})`
}
