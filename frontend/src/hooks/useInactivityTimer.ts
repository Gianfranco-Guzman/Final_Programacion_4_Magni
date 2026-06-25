import { useEffect, useRef } from 'react'

const INACTIVITY_MS = 30 * 60 * 1000

const EVENTS = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'] as const

export const useInactivityTimer = (onInactive: () => void, enabled: boolean) => {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const callbackRef = useRef(onInactive)

  useEffect(() => {
    callbackRef.current = onInactive
  }, [onInactive])

  useEffect(() => {
    if (!enabled) return

    const reset = () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => callbackRef.current(), INACTIVITY_MS)
    }

    reset()
    EVENTS.forEach((e) => window.addEventListener(e, reset, { passive: true }))

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      EVENTS.forEach((e) => window.removeEventListener(e, reset))
    }
  }, [enabled])
}
