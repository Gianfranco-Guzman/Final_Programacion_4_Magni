import axiosClient from './axiosClient'

export interface ResumenStats {
  ventas_hoy: number
  ticket_promedio: number
  pedidos_activos: number
  ingresos_mes_actual: number
}

export interface VentaPeriodoItem {
  periodo: string
  total_ventas: number
  cantidad_pedidos: number
}

export interface ProductoTopItem {
  producto_id: number
  nombre: string
  cantidad_vendida: number
  ingresos: number
}

export interface PedidoEstadoItem {
  estado_codigo: string
  cantidad: number
}

export interface IngresoFormaPagoItem {
  forma_pago_codigo: string
  total: number
  cantidad: number
}

export const estadisticasApi = {
  getResumen: async (): Promise<ResumenStats> => {
    const response = await axiosClient.get<ResumenStats>('/estadisticas/resumen')
    return response.data
  },

  getVentas: async (params?: { desde?: string; hasta?: string; agrupacion?: 'day' | 'week' | 'month' }): Promise<VentaPeriodoItem[]> => {
    const response = await axiosClient.get<VentaPeriodoItem[]>('/estadisticas/ventas', { params })
    return response.data
  },

  getProductosTop: async (limit = 10): Promise<ProductoTopItem[]> => {
    const response = await axiosClient.get<ProductoTopItem[]>('/estadisticas/productos-top', { params: { limit } })
    return response.data
  },

  getPedidosPorEstado: async (): Promise<PedidoEstadoItem[]> => {
    const response = await axiosClient.get<PedidoEstadoItem[]>('/estadisticas/pedidos-por-estado')
    return response.data
  },

  getIngresos: async (params?: { desde?: string; hasta?: string }): Promise<IngresoFormaPagoItem[]> => {
    const response = await axiosClient.get<IngresoFormaPagoItem[]>('/estadisticas/ingresos', { params })
    return response.data
  },
}
