import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteTemplate, fetchTemplates, type TemplateIn, updateTemplate } from '../api/templates'

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

/** Replaces a template, then reloads the list. */
export function useUpdateTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: UpdateTemplateVariables) => updateTemplate(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TEMPLATES_QUERY_KEY }),
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
