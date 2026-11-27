/** Log functions for one part of the app; each line starts with the scope, e.g. `[api]`. */
export interface Logger {
  debug: (message: string, ...context: unknown[]) => void
  info: (message: string, ...context: unknown[]) => void
  warn: (message: string, ...context: unknown[]) => void
  error: (message: string, ...context: unknown[]) => void
}

/**
 * Creates a {@link Logger} whose lines start with `[scope]`. This is the only place that may use
 * `console`; the lint rule `no-console` blocks it everywhere else.
 */
export function createLogger(scope: string): Logger {
  const prefix = `[${scope}]`
  /* oxlint-disable no-console */
  return {
    debug: (message, ...context) => console.debug(prefix, message, ...context),
    info: (message, ...context) => console.info(prefix, message, ...context),
    warn: (message, ...context) => console.warn(prefix, message, ...context),
    error: (message, ...context) => console.error(prefix, message, ...context),
  }
  /* oxlint-enable no-console */
}
