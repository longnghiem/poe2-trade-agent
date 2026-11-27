import { z } from 'zod'
import { apiFetch } from './client'
import { type Template, templateSchema } from './schemas'

/** What the client sends to create or replace a template: a {@link Template} without the fields the backend sets. */
export type TemplateIn = Omit<Template, 'id' | 'owner_id' | 'created_at' | 'updated_at'>

/** Calls `GET /templates`: your templates, the last changed first. */
export function fetchTemplates(): Promise<Template[]> {
  return apiFetch('/templates', z.array(templateSchema))
}

/** Calls `PUT /templates/{id}`, which replaces every field, so send the whole template. */
export function updateTemplate(id: string, data: TemplateIn): Promise<Template> {
  return apiFetch(`/templates/${id}`, templateSchema, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/** Calls `DELETE /templates/{id}`. */
export function deleteTemplate(id: string): Promise<void> {
  return apiFetch(`/templates/${id}`, null, { method: 'DELETE' })
}
