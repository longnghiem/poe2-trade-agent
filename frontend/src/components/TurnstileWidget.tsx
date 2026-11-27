import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { createLogger } from '../lib/logger'
import { statusErrorTextCls } from '../styles'

const logger = createLogger('turnstile')

/** The part of Cloudflare's Turnstile script API this app uses. */
interface TurnstileApi {
  /** Draws a widget into `container` and returns its id. */
  render(container: HTMLElement, options: TurnstileOptions): string
  /** Takes the widget out of the page. */
  remove(widgetId: string): void
}

interface TurnstileOptions {
  sitekey: string
  /** Called with a token when the visitor passed the check. */
  callback: (token: string) => void
  /** Called with Cloudflare's error code when the widget fails. */
  'error-callback': (code: string) => void
  theme: 'light' | 'dark'
}

declare global {
  interface Window {
    turnstile?: TurnstileApi
  }
}

/** The public site key of the Turnstile widget (Cloudflare dashboard), set at build time. */
const SITE_KEY: string | undefined = import.meta.env.VITE_TURNSTILE_SITE_KEY

/** `render=explicit`: the script only loads the API; {@link TurnstileWidget} draws the widget. */
const SCRIPT_URL = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'

let scriptLoading: Promise<TurnstileApi> | null = null

/**
 * Loads Cloudflare's script once per page load and resolves with its API. A failed load (offline,
 * a content blocker) can be tried again.
 */
function loadTurnstile(): Promise<TurnstileApi> {
  if (window.turnstile) return Promise.resolve(window.turnstile)
  scriptLoading ??= new Promise<TurnstileApi>((resolve, reject) => {
    const script = document.createElement('script')
    script.src = SCRIPT_URL
    script.async = true
    script.onload = () =>
      window.turnstile ? resolve(window.turnstile) : reject(new Error('Turnstile API missing'))
    script.onerror = () => {
      script.remove()
      scriptLoading = null
      reject(new Error('Turnstile script failed to load'))
    }
    document.head.appendChild(script)
  })
  return scriptLoading
}

/**
 * Cloudflare's "are you human?" check (Turnstile). When the visitor passes, `onToken` gets a
 * one-time token. The backend uses a token up, so after each try the parent draws a new widget by
 * changing its `key`.
 *
 * The widget is drawn in an effect: Turnstile is an outside system that owns its `<div>`, and the
 * effect's cleanup removes it again.
 */
export function TurnstileWidget({ onToken }: { onToken: (token: string) => void }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loadFailed, setLoadFailed] = useState(false)
  const [widgetFailed, setWidgetFailed] = useState(false)

  // An Effect Event: Turnstile's callback always sees the latest `onToken`, without drawing the
  // widget again when `onToken` changes.
  const handleToken = useEffectEvent((token: string) => onToken(token))

  useEffect(() => {
    if (!SITE_KEY) {
      logger.error('VITE_TURNSTILE_SITE_KEY is not set, so nobody can sign up')
      return
    }
    let cancelled = false
    let widgetId: string | null = null
    loadTurnstile()
      .then((turnstile) => {
        if (cancelled || containerRef.current === null) return
        widgetId = turnstile.render(containerRef.current, {
          sitekey: SITE_KEY,
          callback: (token) => handleToken(token),
          'error-callback': (code) => {
            logger.warn('Turnstile widget error', code)
            setWidgetFailed(true)
          },
          theme: 'dark',
        })
      })
      .catch((error: unknown) => {
        logger.error('Could not load the Turnstile script', error)
        if (!cancelled) setLoadFailed(true)
      })
    return () => {
      cancelled = true
      if (widgetId !== null) window.turnstile?.remove(widgetId)
    }
  }, [])

  if (!SITE_KEY) {
    return <p className={statusErrorTextCls}>Sign-up is off: the human check isn't set up.</p>
  }
  if (loadFailed) {
    return (
      <p className={statusErrorTextCls}>
        The human check couldn't load. Turn off content blockers for this site and reload the page.
      </p>
    )
  }
  return (
    <>
      <div ref={containerRef} className="min-h-[65px]" />
      {widgetFailed && (
        <p className={statusErrorTextCls}>The human check failed. Reload the page to try again.</p>
      )}
    </>
  )
}