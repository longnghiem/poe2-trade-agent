import { useContext } from 'react'
import { AuthContext, type AuthContextType } from './AuthContext'

/** The login state and actions from {@link AuthContext}. Throws when used outside its provider. */
export function useAuth(): AuthContextType {
  const value = useContext(AuthContext)
  if (value === null) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return value
}
