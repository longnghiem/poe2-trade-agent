import { z } from 'zod'

export const userSchema = z.object({
  id: z.string(),
  username: z.string(),
})
export type User = z.infer<typeof userSchema>

export const tokenSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
})
export type Token = z.infer<typeof tokenSchema>

export const modSchema = z.object({
  id: z.string(),
  text: z.string(),
  source: z.string(),
})
export type Mod = z.infer<typeof modSchema>

export const modFilterSchema = z.object({
  stat_id: z.string(),
  label: z.string(),
  min: z.number().nullable(),
  max: z.number().nullable(),
  weight: z.number().nullable(),
})
export type ModFilter = z.infer<typeof modFilterSchema>

export const statGroupSchema = z.object({
  type: z.enum(['and', 'count', 'weight']),
  min: z.number().nullable(),
  max: z.number().nullable(),
  mod_filters: z.array(modFilterSchema),
})
export type StatGroup = z.infer<typeof statGroupSchema>

export const tradeSearchSchema = z.object({
  category: z.string().nullable(),
  stat_groups: z.array(statGroupSchema),
  status_option: z.enum(['available', 'securable', 'online', 'any']),
  max_price: z.number().nullable(),
  price_currency: z.string().nullable(),
})
export type TradeSearch = z.infer<typeof tradeSearchSchema>

export const templateSchema = tradeSearchSchema.extend({
  id: z.string(),
  owner_id: z.string(),
  name: z.string(),
  folder: z.string().nullable(),
  tags: z.array(z.string()),
  is_public: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type Template = z.infer<typeof templateSchema>

export const libraryTemplateSchema = templateSchema.extend({
  owner_username: z.string(),
  vote_count: z.number(),
  voted_by_me: z.boolean(),
})
export type LibraryTemplate = z.infer<typeof libraryTemplateSchema>

export const tradeLinkSchema = z.object({
  url: z.string(),
})
export type TradeLink = z.infer<typeof tradeLinkSchema>

export const parsedTradeUrlSchema = z.object({
  league: z.string(),
  search: tradeSearchSchema,
})
export type ParsedTradeUrl = z.infer<typeof parsedTradeUrlSchema>

export const leaguesSchema = z.array(z.string())
