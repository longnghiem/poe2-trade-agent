import type { ReactNode } from 'react'
import type { Template } from '../api/schemas'
import {
  cardActionsCls,
  cardCls,
  cardHeaderCls,
  cardTitleCls,
  mutedTextCls,
  publicBadgeCls,
  tagCls,
  tagListCls,
} from '../styles'

/** How many mod names a card shows before "+N more". */
const MAX_MODS_SHOWN = 3

/** One template: its name, what it searches for, and the buttons the page passes as `actions`. */
export function TemplateCard({ template, actions }: { template: Template; actions: ReactNode }) {
  const modLabels = template.stat_groups.flatMap((group) =>
    group.mod_filters.map((filter) => filter.label),
  )
  const hiddenMods = modLabels.length - MAX_MODS_SHOWN

  return (
    <li className={cardCls}>
      <div className={cardHeaderCls}>
        <h4 className={cardTitleCls}>{template.name}</h4>
        {template.is_public && <span className={publicBadgeCls}>Public</span>}
      </div>
      <p className={mutedTextCls}>
        {template.category ?? 'Any item'}
        {template.max_price !== null &&
          ` · up to ${template.max_price} ${template.price_currency ?? ''}`}
      </p>
      {modLabels.length > 0 && (
        <p>
          {modLabels.slice(0, MAX_MODS_SHOWN).join(', ')}
          {hiddenMods > 0 && ` +${hiddenMods} more`}
        </p>
      )}
      {template.tags.length > 0 && (
        <ul className={tagListCls}>
          {template.tags.map((tag) => (
            <li key={tag} className={tagCls}>
              {tag}
            </li>
          ))}
        </ul>
      )}
      <div className={cardActionsCls}>{actions}</div>
    </li>
  )
}