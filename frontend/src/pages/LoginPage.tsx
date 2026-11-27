import { useMutation } from '@tanstack/react-query'
import { type SubmitEvent, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { loginUser } from '../api/auth'
import { useAuth } from '../auth/useAuth'
import {
  formCls,
  inputCls,
  labelCls,
  mutedTextCls,
  pageTitleCls,
  statusErrorTextCls,
  submitButtonCls,
  textLinkCls,
} from '../styles'

export function LoginPage() {
  const { isLoggedIn, loginWithToken } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const loginMutation = useMutation({
    mutationFn: async () => {
      const token = await loginUser(username, password)
      loginWithToken(token.access_token)
    },
  })

  // Also reached right after a successful login.
  if (isLoggedIn) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    loginMutation.mutate()
  }

  return (
    <>
      <h2 className={pageTitleCls}>Log in</h2>
      <form className={formCls} onSubmit={handleSubmit}>
        <label className={labelCls}>
          Username
          <input
            className={inputCls}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label className={labelCls}>
          Password
          <input
            className={inputCls}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {loginMutation.error && <p className={statusErrorTextCls}>{loginMutation.error.message}</p>}
        <button className={submitButtonCls} type="submit" disabled={loginMutation.isPending}>
          Log in
        </button>
        <p className={mutedTextCls}>
          No account yet?{' '}
          <Link className={textLinkCls} to="/register">
            Create one
          </Link>
        </p>
      </form>
    </>
  )
}