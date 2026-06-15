import { useQuery } from '@tanstack/react-query'

import { estadisticasApi } from '@api/estadisticasApi'

const today = new Date()
const monthAgo = new Date()
monthAgo.setDate(today.getDate() - 30)

const toDate = (value: Date) => value.toISOString().slice(0, 10)

export const useResumenStats = () => {
  return useQuery({
    queryKey: ['estadisticas', 'resumen'],
    queryFn: estadisticasApi.getResumen,
  })
}

export const useVentasStats = (agrupacion: 'day' | 'week' | 'month' = 'day') => {
  return useQuery({
    queryKey: ['estadisticas', 'ventas', agrupacion],
    queryFn: () =>
      estadisticasApi.getVentas({
        desde: toDate(monthAgo),
        hasta: toDate(today),
        agrupacion,
      }),
  })
}

export const useProductosTopStats = (limit = 10) => {
  return useQuery({
    queryKey: ['estadisticas', 'productos-top', limit],
    queryFn: () => estadisticasApi.getProductosTop(limit),
  })
}

export const usePedidosPorEstadoStats = () => {
  return useQuery({
    queryKey: ['estadisticas', 'pedidos-por-estado'],
    queryFn: estadisticasApi.getPedidosPorEstado,
  })
}

export const useIngresosFormaPagoStats = () => {
  return useQuery({
    queryKey: ['estadisticas', 'ingresos'],
    queryFn: () =>
      estadisticasApi.getIngresos({
        desde: toDate(monthAgo),
        hasta: toDate(today),
      }),
  })
}
