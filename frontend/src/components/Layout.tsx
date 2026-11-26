import type { ReactNode } from 'react'
import { headerCls, headerTitleCls, mainCls, pageCls } from '../styles'
import { Footer } from './Footer'

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className={pageCls}>
      <header className={headerCls}>
        <h1 className={headerTitleCls}>PoE2 Trade Agent</h1>
      </header>
      <main className={mainCls}>{children}</main>
      <Footer />
    </div>
  )
}
