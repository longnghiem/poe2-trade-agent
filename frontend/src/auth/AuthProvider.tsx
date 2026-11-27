import { useQuery, useQueryClient } from '@tanstack/react-query'
import { type ReactNode, useState } from 'react'
import { fetchCurrentUser } from '../api/auth'
import { TOKEN_KEY } from '../api/client'
import { AuthContext } from './AuthContext'

/** Keeps the login token and the logged-in user, and shares them through {@link AuthContext}. */
export function AuthProvider({ children }: { children: ReactNode }) {
  // Read once at startup. When the token expires, the API client removes it and reloads the
  // page, so this state starts again from localStorage.
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const queryClient = useQueryClient()

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: fetchCurrentUser,
    enabled: token !== null,
  })

  function loginWithToken(newToken: string) {
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    // The next user mustn't see this user's templates or name from the cache.
    queryClient.clear()
    setToken(null)
  }

  return (
    <AuthContext
      value={{
        isLoggedIn: token !== null,
        username: user?.username ?? null,
        loginWithToken,
        logout,
      }}
    >
      {children}
    </AuthContext>
  )
}
