import { Link } from 'react-router-dom'
import { linkCls, mutedTextCls, pageTitleCls } from '../styles'

export function NotFoundPage() {
  return (
    <>
      <h2 className={pageTitleCls}>Page not found</h2>
      <p className={mutedTextCls}>
        There's no page at this address.{' '}
        <Link className={linkCls} to="/">
          Go to my templates
        </Link>
      </p>
    </>
  )
}
