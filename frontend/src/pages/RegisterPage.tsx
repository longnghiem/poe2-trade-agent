import { useMutation } from '@tanstack/react-query'
import { type SubmitEvent, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { loginUser, registerUser } from '../api/auth'
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

const MIN_PASSWORD_LENGTH = 6

export function RegisterPage() {
  const { isLoggedIn, loginWithToken } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const registerMutation = useMutation({
    mutationFn: async () => {
      await registerUser(username, password)
      const token = await loginUser(username, password)
      loginWithToken(token.access_token)
    },
  })

  // Also reached right after a successful sign-up, which logs in too.
  if (isLoggedIn) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    registerMutation.mutate()
  }

  return (
    <>
      <h2 className={pageTitleCls}>Create an account</h2>
      <form className={formCls} onSubmit={handleSubmit}>
        <label className={labelCls}>
          Username (3 to 30 characters)
          <input
            className={inputCls}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
            minLength={3}
            maxLength={30}
          />
        </label>
        <label className={labelCls}>
          Password (at least {MIN_PASSWORD_LENGTH} characters)
          <input
            className={inputCls}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            required
            minLength={MIN_PASSWORD_LENGTH}
            maxLength={128}
          />
        </label>
        {registerMutation.error && (
          <p className={statusErrorTextCls}>{registerMutation.error.message}</p>
        )}
        <button className={submitButtonCls} type="submit" disabled={registerMutation.isPending}>
          Create account
        </button>
        <p className={mutedTextCls}>
          Already have an account?{' '}
          <Link className={textLinkCls} to="/login">
            Log in
          </Link>
        </p>
      </form>
    </>
  )
}