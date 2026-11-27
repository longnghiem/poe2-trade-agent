import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import {
  headerCls,
  headerInnerCls,
  headerTitleCls,
  mainCls,
  mutedTextCls,
  navCls,
  navLinkActiveCls,
  navLinkInactiveCls,
  pageCls,
  secondaryButtonCls,
} from '../styles'
import { Footer } from './Footer'

/** Highlights the link of the page you're on. */
function navLinkClassName({ isActive }: { isActive: boolean }) {
  return isActive ? navLinkActiveCls : navLinkInactiveCls
}

export function Layout({ children }: { children: ReactNode }) {
  const { isLoggedIn, username, logout } = useAuth()

  return (
    <div className={pageCls}>
      <header className={headerCls}>
        <div className={headerInnerCls}>
          <h1 className={headerTitleCls}>PoE2 Trade Agent</h1>
          {isLoggedIn && (
            <>
              <nav className={navCls}>
                <NavLink to="/" className={navLinkClassName}>
                  My templates
                </NavLink>
                <NavLink to="/library" className={navLinkClassName}>
                  Library
                </NavLink>
              </nav>
              <span className={mutedTextCls}>{username}</span>
              <button type="button" className={secondaryButtonCls} onClick={logout}>
                Log out
              </button>
            </>
          )}
        </div>
      </header>
      <main className={mainCls}>{children}</main>
      <Footer />
    </div>
  )
}
