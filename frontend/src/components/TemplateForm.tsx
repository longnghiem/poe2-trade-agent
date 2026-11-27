import { type SubmitEvent, useState } from 'react'
import { Link } from 'react-router-dom'
import { tradeSearchSchema } from '../api/schemas'
import type { TemplateIn } from '../api/templates'
import { CATEGORY_OPTIONS, CURRENCY_OPTIONS, STATUS_OPTIONS } from '../lib/tradeOptions'
import {
  checkboxLabelCls,
  formActionsCls,
  formRowCls,
  hintTextCls,
  inputCls,
  labelCls,
  secondaryButtonCls,
  statusErrorTextCls,
  submitButtonCls,
  templateFormCls,
} from '../styles'

interface TemplateFormProps {
  /** The values the form starts with; a later change doesn't reach the form. */
  initialValues: TemplateIn
  onSubmit: (data: TemplateIn) => void
  isPending: boolean
  error: Error | null
}

/** Splits "leveling, boots" into `['leveling', 'boots']`: no spaces around a tag, no empty or repeated tags. */
function parseTags(text: string): string[] {
  const tags = text.split(',').map((tag) => tag.trim())
  return [...new Set(tags.filter((tag) => tag !== ''))]
}

/** The form for a template's name, folder, tags and search settings. Stat groups are kept as they are. */
export function TemplateForm({ initialValues, onSubmit, isPending, error }: TemplateFormProps) {
  const [name, setName] = useState(initialValues.name)
  const [folder, setFolder] = useState(initialValues.folder ?? '')
  const [tagsText, setTagsText] = useState(initialValues.tags.join(', '))
  const [category, setCategory] = useState(initialValues.category ?? '')
  const [statusOption, setStatusOption] = useState(initialValues.status_option)
  const [maxPrice, setMaxPrice] = useState(initialValues.max_price?.toString() ?? '')
  const [priceCurrency, setPriceCurrency] = useState(initialValues.price_currency ?? '')
  const [isPublic, setIsPublic] = useState(initialValues.is_public)

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    // Empty fields are sent as null, which the backend reads as "not set".
    onSubmit({
      name: name.trim(),
      folder: folder.trim() || null,
      tags: parseTags(tagsText),
      category: category || null,
      stat_groups: initialValues.stat_groups,
      status_option: statusOption,
      max_price: maxPrice === '' ? null : Number(maxPrice),
      price_currency: priceCurrency || null,
      is_public: isPublic,
    })
  }

  return (
    <form className={templateFormCls} onSubmit={handleSubmit}>
      <label className={labelCls}>
        Name
        <input
          className={inputCls}
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          required
        />
      </label>
      <label className={labelCls}>
        Folder
        <input
          className={inputCls}
          value={folder}
          onChange={(e) => setFolder(e.target.value)}
          maxLength={50}
          placeholder="e.g. Boots"
        />
      </label>
      <label className={labelCls}>
        Tags
        <input
          className={inputCls}
          value={tagsText}
          onChange={(e) => setTagsText(e.target.value)}
          placeholder="e.g. leveling, cheap"
        />
        <span className={hintTextCls}>Separate tags with commas.</span>
      </label>
      <label className={labelCls}>
        Item category
        <select className={inputCls} value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        Listing status
        <select
          className={inputCls}
          value={statusOption}
          onChange={(e) =>
            setStatusOption(tradeSearchSchema.shape.status_option.parse(e.target.value))
          }
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <div className={formRowCls}>
        <label className={labelCls}>
          Max price
          <input
            className={inputCls}
            type="number"
            min={0}
            step="any"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
          />
        </label>
        <label className={labelCls}>
          Currency
          <select
            className={inputCls}
            value={priceCurrency}
            onChange={(e) => setPriceCurrency(e.target.value)}
          >
            {CURRENCY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className={checkboxLabelCls}>
        <input type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)} />
        Public
      </label>
      <p className={hintTextCls}>Everyone using the app can see and copy public templates.</p>
      {error && <p className={statusErrorTextCls}>{error.message}</p>}
      <div className={formActionsCls}>
        <button className={submitButtonCls} type="submit" disabled={isPending}>
          Save
        </button>
        <Link className={secondaryButtonCls} to="/">
          Cancel
        </Link>
      </div>
    </form>
  )
}
