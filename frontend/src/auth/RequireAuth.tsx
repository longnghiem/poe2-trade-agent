import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './useAuth'

/** Shows the routes inside it when logged in; otherwise goes to `/login`. */
export function RequireAuth() {
  const { isLoggedIn } = useAuth()
  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />
}