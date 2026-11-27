import { mutedTextCls, pageTitleCls } from '../styles'

export function LibraryPage() {
  return (
    <>
      <h2 className={pageTitleCls}>Library</h2>
      <p className={mutedTextCls}>Public templates from everyone come here.</p>
    </>
  )
}
