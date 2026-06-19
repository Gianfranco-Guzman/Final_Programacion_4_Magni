import { create } from 'zustand'

type WsConnectionStatus = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected' | 'error'

interface WsState {
  status: WsConnectionStatus
  setStatus: (status: WsConnectionStatus) => void
  reset: () => void
}

const initialState = {
  status: 'idle' as WsConnectionStatus,
}

export const useWsStore = create<WsState>((set) => ({
  ...initialState,

  setStatus: (status) => set({ status }),

  reset: () => set(initialState),
}))
