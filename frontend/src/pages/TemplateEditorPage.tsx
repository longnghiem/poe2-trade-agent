import { useNavigate, useParams } from 'react-router-dom'
import type { TemplateIn } from '../api/templates'
import { TemplateForm } from '../components/TemplateForm'
import { useCreateTemplate, useTemplate, useUpdateTemplate } from '../hooks/useTemplates'
import { mutedTextCls, pageTitleCls, statusErrorTextCls } from '../styles'

/** The values a new template starts with. */
const EMPTY_TEMPLATE: TemplateIn = {
  name: '',
  folder: null,
  tags: [],
  category: null,
  stat_groups: [],
  status_option: 'securable',
  max_price: null,
  price_currency: null,
  is_public: false,
}

export function TemplateEditorPage() {
  // Set on /templates/:id/edit; missing on /templates/new.
  const { id } = useParams()
  return (
    <>
      <h2 className={pageTitleCls}>{id ? 'Edit template' : 'New template'}</h2>
      {id ? <EditTemplate id={id} /> : <NewTemplate />}
    </>
  )
}

/** The empty form; saving creates the template and goes back to the list. */
function NewTemplate() {
  const navigate = useNavigate()
  const createMutation = useCreateTemplate()
  return (
    <TemplateForm
      initialValues={EMPTY_TEMPLATE}
      onSubmit={(data) => createMutation.mutate(data, { onSuccess: () => navigate('/') })}
      isPending={createMutation.isPending}
      error={createMutation.error}
    />
  )
}

/** Loads the template, then shows the form with its values; saving replaces it. */
function EditTemplate({ id }: { id: string }) {
  const navigate = useNavigate()
  const { data: template, error, isPending } = useTemplate(id)
  const updateMutation = useUpdateTemplate()

  if (isPending) {
    return <p className={mutedTextCls}>Loading...</p>
  }
  if (error) {
    return <p className={statusErrorTextCls}>{error.message}</p>
  }
  return (
    <TemplateForm
      initialValues={template}
      onSubmit={(data) => updateMutation.mutate({ id, data }, { onSuccess: () => navigate('/') })}
      isPending={updateMutation.isPending}
      error={updateMutation.error}
    />
  )
}
