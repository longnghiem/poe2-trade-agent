import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { Template } from '../api/schemas'
import { TemplateCard } from '../components/TemplateCard'
import { useDeleteTemplate, useTemplates, useUpdateTemplate } from '../hooks/useTemplates'
import {
  cardListCls,
  chipActiveCls,
  chipCls,
  chipListCls,
  folderTitleCls,
  mutedTextCls,
  pageHeaderCls,
  pageTitleCls,
  secondaryButtonCls,
  statusErrorTextCls,
  submitButtonCls,
  textLinkCls,
} from '../styles'

/** The group name of templates without a folder; it's listed last. */
const NO_FOLDER = 'No folder'

/** Groups templates by folder, sorted by folder name, with "No folder" last. */
function groupByFolder(templates: Template[]): [string, Template[]][] {
  const groups = new Map<string, Template[]>()
  for (const template of templates) {
    const folder = template.folder ?? NO_FOLDER
    groups.set(folder, [...(groups.get(folder) ?? []), template])
  }
  return [...groups].sort(([a], [b]) =>
    a === NO_FOLDER ? 1 : b === NO_FOLDER ? -1 : a.localeCompare(b),
  )
}

export function MyTemplatesPage() {
  const { data: templates, error, isPending } = useTemplates()
  const updateMutation = useUpdateTemplate()
  const deleteMutation = useDeleteTemplate()
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  const handleDelete = (template: Template) => {
    if (window.confirm(`Delete "${template.name}"?`)) {
      deleteMutation.mutate(template.id)
    }
  }

  const handleTogglePublic = (template: Template) => {
    updateMutation.mutate({
      id: template.id,
      data: { ...template, is_public: !template.is_public },
    })
  }

  const header = (
    <div className={pageHeaderCls}>
      <h2 className={pageTitleCls}>My templates</h2>
      <Link className={submitButtonCls} to="/templates/new">
        New template
      </Link>
    </div>
  )

  if (isPending) {
    return (
      <>
        {header}
        <p className={mutedTextCls}>Loading...</p>
      </>
    )
  }
  if (error) {
    return (
      <>
        {header}
        <p className={statusErrorTextCls}>{error.message}</p>
      </>
    )
  }
  if (templates.length === 0) {
    return (
      <>
        {header}
        <p className={mutedTextCls}>
          No templates yet.{' '}
          <Link className={textLinkCls} to="/templates/new">
            Create one
          </Link>{' '}
          or copy one from the{' '}
          <Link className={textLinkCls} to="/library">
            Library
          </Link>
          .
        </p>
      </>
    )
  }

  const allTags = [...new Set(templates.flatMap((template) => template.tags))].sort()
  const shownTemplates = selectedTag
    ? templates.filter((template) => template.tags.includes(selectedTag))
    : templates
  const actionError = updateMutation.error ?? deleteMutation.error

  return (
    <>
      {header}
      {actionError && <p className={statusErrorTextCls}>{actionError.message}</p>}
      {allTags.length > 0 && (
        <div className={chipListCls}>
          {allTags.map((tag) => (
            <button
              key={tag}
              type="button"
              aria-pressed={tag === selectedTag}
              className={tag === selectedTag ? chipActiveCls : chipCls}
              onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      )}
      {groupByFolder(shownTemplates).map(([folder, folderTemplates]) => (
        <section key={folder}>
          <h3 className={folderTitleCls}>{folder}</h3>
          <ul className={cardListCls}>
            {folderTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                actions={
                  <>
                    <Link className={secondaryButtonCls} to={`/templates/${template.id}/edit`}>
                      Edit
                    </Link>
                    <button
                      type="button"
                      className={secondaryButtonCls}
                      onClick={() => handleTogglePublic(template)}
                    >
                      {template.is_public ? 'Unpublish' : 'Publish'}
                    </button>
                    <button
                      type="button"
                      className={secondaryButtonCls}
                      onClick={() => handleDelete(template)}
                    >
                      Delete
                    </button>
                  </>
                }
              />
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}
