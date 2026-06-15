import { create } from 'zustand'

type WsConnectionStatus = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected' | 'error'

interface WsState {
  status: WsConnectionStatus
  lastEventAt: string | null
  subscribedOrders: number[]
  adminFeedActive: boolean
  setStatus: (status: WsConnectionStatus) => void
  markEvent: () => void
  setOrderSubscribed: (orderId: number) => void
  setOrderUnsubscribed: (orderId: number) => void
  setAdminFeedActive: (active: boolean) => void
  reset: () => void
}

const initialState = {
  status: 'idle' as WsConnectionStatus,
  lastEventAt: null as string | null,
  subscribedOrders: [] as number[],
  adminFeedActive: false,
}

export const useWsStore = create<WsState>((set) => ({
  ...initialState,

  setStatus: (status) => set({ status }),

  markEvent: () => set({ lastEventAt: new Date().toISOString() }),

  setOrderSubscribed: (orderId) =>
    set((state) => ({
      subscribedOrders: state.subscribedOrders.includes(orderId)
        ? state.subscribedOrders
        : [...state.subscribedOrders, orderId],
    })),

  setOrderUnsubscribed: (orderId) =>
    set((state) => ({
      subscribedOrders: state.subscribedOrders.filter((id) => id !== orderId),
    })),

  setAdminFeedActive: (active) => set({ adminFeedActive: active }),

  reset: () => set(initialState),
}))
