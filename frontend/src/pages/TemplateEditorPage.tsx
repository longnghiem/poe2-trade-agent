import { useParams } from 'react-router-dom'
import { mutedTextCls, pageTitleCls } from '../styles'

export function TemplateEditorPage() {
  // Set on /templates/:id/edit; missing on /templates/new.
  const { id } = useParams()
  return (
    <>
      <h2 className={pageTitleCls}>{id ? 'Edit template' : 'New template'}</h2>
      <p className={mutedTextCls}>The template form comes here.</p>
    </>
  )
}
