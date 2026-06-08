import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { hasAnyRole } from '@/auth/permissions'
import { FeedbackAlert } from '@components/FeedbackAlert'
import { Spinner } from '@components/Spinner'
import { usePedidos, useCancelarPedido } from '@hooks/usePedidos'
import { useWebSocket, WsMessage } from '@hooks/useWebSocket'
import { useAuthStore } from '@store/authStore'

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREP: 'bg-orange-100 text-orange-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
}

const ESTADO_LABEL: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREP: 'En preparación',
  EN_CAMINO: 'En camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}

const ESTADOS_CANCELABLES = ['PENDIENTE', 'CONFIRMADO']

export const MisPedidosPage: React.FC = () => {
  const [estadoFiltro, setEstadoFiltro] = useState<string | undefined>(undefined)
  const [actionError, setActionError] = useState('')
  const usuario = useAuthStore((state) => state.usuario)
  const { data: pedidos = [], isLoading, error, refetch } = usePedidos({ estado: estadoFiltro })
  const cancelarMutation = useCancelarPedido()

  const handleWsMessage = useCallback((message: WsMessage) => {
    if (message.event === 'WS_CONNECTED' || message.event.startsWith('PEDIDO_')) {
      void refetch()
    }
  }, [refetch])

  const { subscribeToOrder } = useWebSocket({
    enabled: !!usuario && hasAnyRole(usuario.roles, ['CLIENT']),
    onMessage: handleWsMessage,
  })

  useEffect(() => {
    pedidos.forEach((pedido) => subscribeToOrder(pedido.id))
  }, [pedidos, subscribeToOrder])

  const handleCancelar = (id: number) => {
    if (!window.confirm('¿Cancelar este pedido?')) return
    setActionError('')
    cancelarMutation.mutate(
      { id },
      { onError: (err: unknown) => setActionError(err instanceof Error ? err.message : 'Error al cancelar') },
    )
  }

  if (error) {
    return (
        <div className="text-center py-12">
          <p className="text-red-600">{error instanceof Error ? error.message : 'Error cargando pedidos'}</p>
        </div>
      )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Mis pedidos</h1>
        <select
          value={estadoFiltro ?? ''}
          onChange={(e) => setEstadoFiltro(e.target.value || undefined)}
          className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">Todos los estados</option>
          {Object.entries(ESTADO_LABEL).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {actionError && (
        <div className="mb-4">
          <FeedbackAlert title="No se pudo cancelar el pedido">{actionError}</FeedbackAlert>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : pedidos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No tenés pedidos todavía.
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {pedidos.map((pedido) => (
            <div key={pedido.id} className="bg-white rounded-lg shadow p-5 border border-gray-100">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg font-semibold text-gray-800">Pedido #{pedido.id}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${ESTADO_COLORS[pedido.estado_actual] ?? 'bg-gray-100 text-gray-700'}`}>
                      {ESTADO_LABEL[pedido.estado_actual] ?? pedido.estado_actual}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-blue-600 mb-1">${pedido.total.toFixed(2)}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(pedido.created_at).toLocaleString('es-AR')}
                  </p>
                  {pedido.notas && (
                    <p className="text-sm text-gray-600 mt-1 italic">"{pedido.notas}"</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Link
                    to={`/pedidos/${pedido.id}`}
                    className="text-sm bg-blue-50 text-blue-600 border border-blue-200 rounded px-3 py-1 hover:bg-blue-100"
                  >
                    Ver detalle
                  </Link>
                  {ESTADOS_CANCELABLES.includes(pedido.estado_actual) && (
                    <button
                      onClick={() => handleCancelar(pedido.id)}
                      disabled={cancelarMutation.isPending}
                      className="text-sm bg-red-50 text-red-600 border border-red-200 rounded px-3 py-1 hover:bg-red-100 disabled:opacity-50"
                    >
                      Cancelar
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
