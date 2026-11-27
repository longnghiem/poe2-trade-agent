import { createContext } from 'react'

/** The login state and actions that every component can read. */
export interface AuthContextType {
  /** True when a login token is stored. */
  isLoggedIn: boolean
  /** The logged-in user's name from the backend; `null` while it loads and when logged out. */
  username: string | null
  /** Stores the token that the login endpoint returned. */
  loginWithToken: (token: string) => void
  /** Forgets the token and all cached data. The protected pages then go to `/login`. */
  logout: () => void
}

/** The shared login state; `null` outside its provider. */
export const AuthContext = createContext<AuthContextType | null>(null)
