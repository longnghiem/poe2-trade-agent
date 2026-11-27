import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createTemplate,
  deleteTemplate,
  fetchTemplateById,
  fetchTemplates,
  type TemplateIn,
  updateTemplate,
} from '../api/templates'

/** The cache key of the template list; every change to a template refreshes it. */
const TEMPLATES_QUERY_KEY = ['templates'] as const

export interface UpdateTemplateVariables {
  id: string
  data: TemplateIn
}

/** Your templates, from the cache or the backend. */
export function useTemplates() {
  return useQuery({ queryKey: TEMPLATES_QUERY_KEY, queryFn: fetchTemplates })
}

/** One of your templates. Its key starts with the list's key, so every change refreshes it too. */
export function useTemplate(id: string) {
  return useQuery({ queryKey: [...TEMPLATES_QUERY_KEY, id], queryFn: () => fetchTemplateById(id) })
}

/** Creates a template, then reloads the list. */
export function useCreateTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: TemplateIn) => createTemplate(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TEMPLATES_QUERY_KEY }),
  })
}

/** Replaces a template, then reloads the list. */
export function useUpdateTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: UpdateTemplateVariables) => updateTemplate(id, data),
    onSuccess: (template) => {
      // The editor fills its form from the cache, so it must find the saved template, not the old one.
      queryClient.setQueryData([...TEMPLATES_QUERY_KEY, template.id], template)
      return queryClient.invalidateQueries({ queryKey: TEMPLATES_QUERY_KEY })
    },
  })
}

/** Deletes a template, then reloads the list. */
export function useDeleteTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteTemplate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TEMPLATES_QUERY_KEY }),
  })
}
