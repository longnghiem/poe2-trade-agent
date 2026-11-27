import type { TradeSearch } from '../api/schemas'

/** One choice in a dropdown: `value` is what the trade site expects, `label` is what the user sees. */
export interface Option<T extends string = string> {
  value: T
  label: string
}

/** Item categories of the trade site; the empty value means any item. */
export const CATEGORY_OPTIONS: Option[] = [
  { value: '', label: 'Any item' },
  { value: 'armour.helmet', label: 'Helmet' },
  { value: 'armour.chest', label: 'Body Armour' },
  { value: 'armour.gloves', label: 'Gloves' },
  { value: 'armour.boots', label: 'Boots' },
  { value: 'armour.shield', label: 'Shield' },
  { value: 'armour.buckler', label: 'Buckler' },
  { value: 'armour.focus', label: 'Focus' },
  { value: 'armour.quiver', label: 'Quiver' },
  { value: 'accessory.amulet', label: 'Amulet' },
  { value: 'accessory.ring', label: 'Ring' },
  { value: 'accessory.belt', label: 'Belt' },
  { value: 'jewel', label: 'Jewel' },
  { value: 'flask', label: 'Flask' },
  { value: 'flask.charm', label: 'Charm' },
  { value: 'weapon.bow', label: 'Bow' },
  { value: 'weapon.crossbow', label: 'Crossbow' },
  { value: 'weapon.wand', label: 'Wand' },
  { value: 'weapon.staff', label: 'Staff' },
  { value: 'weapon.warstaff', label: 'Quarterstaff' },
  { value: 'weapon.sceptre', label: 'Sceptre' },
  { value: 'weapon.spear', label: 'Spear' },
  { value: 'weapon.flail', label: 'Flail' },
  { value: 'weapon.talisman', label: 'Talisman' },
  { value: 'weapon.onemace', label: 'One Hand Mace' },
  { value: 'weapon.twomace', label: 'Two Hand Mace' },
  { value: 'weapon.oneaxe', label: 'One Hand Axe' },
  { value: 'weapon.twoaxe', label: 'Two Hand Axe' },
  { value: 'weapon.onesword', label: 'One Hand Sword' },
  { value: 'weapon.twosword', label: 'Two Hand Sword' },
  { value: 'weapon.dagger', label: 'Dagger' },
  { value: 'weapon.claw', label: 'Claw' },
  { value: 'map.waystone', label: 'Waystone' },
  { value: 'map.tablet', label: 'Tablet' },
]

/** Which sellers to show on the trade site, as it labels them; only the three this app needs. */
export const STATUS_OPTIONS: Option<TradeSearch['status_option']>[] = [
  { value: 'available', label: 'Instant Buyout and In Person' },
  { value: 'securable', label: 'Instant Buyout' },
  { value: 'any', label: 'Any' },
]

/** The currencies a max price can be in, as on the trade site; the empty value compares prices in Exalted Orb equivalents. */
export const CURRENCY_OPTIONS: Option[] = [
  { value: '', label: 'Exalted Orb Equivalent' },
  { value: 'exalted_divine', label: 'Exalted or Divine Orbs' },
  { value: 'aug', label: 'Orb of Augmentation' },
  { value: 'transmute', label: 'Orb of Transmutation' },
  { value: 'exalted', label: 'Exalted Orb' },
  { value: 'regal', label: 'Regal Orb' },
  { value: 'chaos', label: 'Chaos Orb' },
  { value: 'vaal', label: 'Vaal Orb' },
  { value: 'alch', label: 'Orb of Alchemy' },
  { value: 'divine', label: 'Divine Orb' },
  { value: 'annul', label: 'Orb of Annulment' },
  { value: 'mirror', label: 'Mirror of Kalandra' },
]

/** The label of the option with this value; `null` finds the empty option, and an unknown value is shown as it is. */
function optionLabel(options: Option[], value: string | null): string {
  return options.find((option) => option.value === (value ?? ''))?.label ?? value ?? ''
}

/** The readable name of a category, e.g. "Boots" for `armour.boots`. */
export function categoryLabel(category: string | null): string {
  return optionLabel(CATEGORY_OPTIONS, category)
}

/** The readable name of a currency, e.g. "Divine Orb" for `divine`. */
export function currencyLabel(currency: string | null): string {
  return optionLabel(CURRENCY_OPTIONS, currency)
}
