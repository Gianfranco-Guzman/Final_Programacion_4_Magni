import { useCallback, useEffect, useRef } from 'react'
import { API_BASE_URL } from '@api/axiosClient'
import { useWsStore } from '@store/wsStore'

export interface WsMessage {
  event: string
  data: unknown
}

interface UseWebSocketOptions {
  enabled?: boolean
  onMessage?: (message: WsMessage) => void
  adminFeed?: boolean
}

const buildWsUrl = () => {
  const apiUrl = new URL(API_BASE_URL, window.location.origin)
  const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
  const path = apiUrl.pathname.replace(/\/$/, '')
  return `${protocol}//${apiUrl.host}${path}/pedidos/ws`
}

export const useWebSocket = ({ enabled = true, onMessage, adminFeed = false }: UseWebSocketOptions = {}) => {
  const wsRef = useRef<WebSocket | null>(null)
  const onMessageRef = useRef(onMessage)
  const subscribedOrdersRef = useRef<Set<number>>(new Set())
  const setStatus = useWsStore((state) => state.setStatus)

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    if (!enabled) {
      setStatus('idle')
      return
    }

    let cancelled = false
    let retryCount = 0
    let retryTimer: ReturnType<typeof setTimeout> | null = null
    let currentSocket: WebSocket | null = null

    const replaySubscriptions = (socket: WebSocket) => {
      if (adminFeed) {
        socket.send(JSON.stringify({ action: 'subscribe-admin-feed' }))
      }
      subscribedOrdersRef.current.forEach((orderId) => {
        socket.send(JSON.stringify({ action: 'subscribe-order', order_id: orderId }))
      })
    }

    const closeCleanly = (socket: WebSocket) => {
      if (socket.readyState === WebSocket.CONNECTING) {
        socket.addEventListener('open', () => socket.close(1000), { once: true })
      } else if (socket.readyState === WebSocket.OPEN) {
        socket.close(1000)
      }
    }

    const connect = () => {
      if (cancelled) return

      setStatus(retryCount > 0 ? 'reconnecting' : 'connecting')

      const socket = new WebSocket(buildWsUrl())
      currentSocket = socket
      wsRef.current = socket

      socket.onopen = () => {
        if (cancelled) {
          socket.close(1000)
          return
        }
        retryCount = 0
        replaySubscriptions(socket)
        setStatus('connected')
        onMessageRef.current?.({ event: 'WS_CONNECTED', data: null })
      }

      socket.onmessage = (event) => {
        if (cancelled) return
        try {
          onMessageRef.current?.(JSON.parse(event.data) as WsMessage)
        } catch {
          // noop
        }
      }

      socket.onclose = (event) => {
        if (wsRef.current === socket) {
          wsRef.current = null
        }
        currentSocket = null

        const shouldReconnect = !cancelled && event.code !== 1000 && event.code !== 1008
        if (!shouldReconnect) {
          setStatus(event.code === 1008 ? 'error' : 'disconnected')
          return
        }

        retryCount += 1
        const delay = Math.min(1000 * 2 ** retryCount, 30_000)
        retryTimer = setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      cancelled = true
      if (retryTimer) clearTimeout(retryTimer)
      if (currentSocket) closeCleanly(currentSocket)
      setStatus('disconnected')
      wsRef.current = null
    }
  }, [adminFeed, enabled, setStatus])

  const subscribeToOrder = useCallback((orderId: number) => {
    subscribedOrdersRef.current.add(orderId)
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe-order', order_id: orderId }))
    }
  }, [])

  const unsubscribeFromOrder = useCallback((orderId: number) => {
    subscribedOrdersRef.current.delete(orderId)
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe-order', order_id: orderId }))
    }
  }, [])

  return { subscribeToOrder, unsubscribeFromOrder }
}
