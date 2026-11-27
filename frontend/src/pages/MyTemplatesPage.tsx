import { mutedTextCls, pageTitleCls } from '../styles'

export function MyTemplatesPage() {
  return (
    <>
      <h2 className={pageTitleCls}>My templates</h2>
      <p className={mutedTextCls}>Your saved trade searches come here.</p>
    </>
  )
}
