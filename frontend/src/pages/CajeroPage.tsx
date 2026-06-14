import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import { hasAnyRole } from '@/auth/permissions'
import { FeedbackAlert } from '@components/FeedbackAlert'
import { Spinner } from '@components/Spinner'
import { usePedidos, useAvanzarEstado, useCancelarPedido } from '@hooks/usePedidos'
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

const NEXT_LABEL: Record<string, string> = {
  PENDIENTE: 'Confirmar',
  CONFIRMADO: 'Iniciar preparación',
  EN_PREP: 'Enviar',
  EN_CAMINO: 'Marcar entregado',
}

const ESTADOS_ACTIVOS = ['PENDIENTE', 'CONFIRMADO', 'EN_PREP', 'EN_CAMINO']

export const CajeroPage: React.FC = () => {
  const [estadoFiltro, setEstadoFiltro] = useState<string | undefined>(undefined)
  const [actionError, setActionError] = useState('')
  const usuario = useAuthStore((state) => state.usuario)
  const { data: pedidos = [], isLoading, error, refetch } = usePedidos({ estado: estadoFiltro, size: 50 })
  const avanzarMutation = useAvanzarEstado()
  const cancelarMutation = useCancelarPedido()

  const handleWsMessage = useCallback((message: WsMessage) => {
    if (message.event === 'WS_CONNECTED' || message.event.startsWith('PEDIDO_')) {
      void refetch()
    }
  }, [refetch])

  useWebSocket({
    enabled: !!usuario && hasAnyRole(usuario.roles, ['PEDIDOS', 'ADMIN']),
    onMessage: handleWsMessage,
  })

  const pedidosActivos = estadoFiltro
    ? pedidos
    : pedidos.filter((p) => ESTADOS_ACTIVOS.includes(p.estado_actual))

  const handleAvanzar = (id: number) => {
    setActionError('')
    avanzarMutation.mutate(
      { id },
      { onError: (err: unknown) => setActionError(err instanceof Error ? err.message : 'Error al avanzar estado') },
    )
  }

  const handleCancelar = (id: number) => {
    if (!window.confirm('¿Cancelar este pedido?')) return
    const observacion = window.prompt('Ingresá el motivo de cancelación:')?.trim()
    if (!observacion) {
      setActionError('Debés ingresar un motivo para cancelar el pedido.')
      return
    }
    setActionError('')
    cancelarMutation.mutate(
      { id, observacion },
      { onError: (err: unknown) => setActionError(err instanceof Error ? err.message : 'Error al cancelar') },
    )
  }

  if (error) {
    return (
        <div className="text-center py-12">
        <p className="text-red-600">{error instanceof Error ? error.message : 'Error cargando pedidos'}</p>
        <button onClick={() => refetch()} className="mt-4 text-blue-600 hover:underline text-sm">
          Reintentar
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Panel cajero</h1>
          <p className="text-gray-500 text-sm mt-1">
            {pedidosActivos.length} pedido(s) {estadoFiltro ? `en estado ${ESTADO_LABEL[estadoFiltro]}` : 'activos'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={estadoFiltro ?? ''}
            onChange={(e) => setEstadoFiltro(e.target.value || undefined)}
            className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">Activos</option>
            {Object.entries(ESTADO_LABEL).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <button
            onClick={() => refetch()}
            className="text-sm border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
          >
            Actualizar
          </button>
        </div>
      </div>

      {actionError && (
        <div className="mb-4">
          <FeedbackAlert title="No se pudo completar la acción">{actionError}</FeedbackAlert>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : pedidosActivos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No hay pedidos {estadoFiltro ? `en estado ${ESTADO_LABEL[estadoFiltro]}` : 'activos'}.
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {pedidosActivos.map((pedido) => {
            const nextLabel = NEXT_LABEL[pedido.estado_actual]
            const puedeCancel = ['PENDIENTE', 'CONFIRMADO'].includes(pedido.estado_actual)
            const isBusy = avanzarMutation.isPending || cancelarMutation.isPending

            return (
              <div key={pedido.id} className="bg-white rounded-lg shadow p-5 border border-gray-100">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-bold text-gray-800 text-lg">Pedido #{pedido.id}</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${ESTADO_COLORS[pedido.estado_actual] ?? 'bg-gray-100 text-gray-700'}`}>
                        {ESTADO_LABEL[pedido.estado_actual] ?? pedido.estado_actual}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-1">
                      Cliente ID: {pedido.usuario_id} · {new Date(pedido.created_at).toLocaleString('es-AR')}
                    </p>
                    <p className="text-xl font-bold text-blue-600">${pedido.total.toFixed(2)}</p>
                    {pedido.notas && (
                      <p className="text-xs text-gray-500 mt-1 italic">"{pedido.notas}"</p>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <Link
                      to={`/pedidos/${pedido.id}`}
                      className="text-xs border border-gray-200 text-gray-600 rounded px-3 py-1 hover:bg-gray-50"
                    >
                      Ver detalle
                    </Link>

                    {nextLabel && (
                      <button
                        onClick={() => handleAvanzar(pedido.id)}
                        disabled={isBusy}
                        className="text-sm bg-blue-600 text-white rounded px-3 py-1.5 hover:bg-blue-700 disabled:opacity-50 font-medium"
                      >
                        {nextLabel}
                      </button>
                    )}

                    {puedeCancel && (
                      <button
                        onClick={() => handleCancelar(pedido.id)}
                        disabled={isBusy}
                        className="text-xs bg-red-50 text-red-600 border border-red-200 rounded px-3 py-1 hover:bg-red-100 disabled:opacity-50"
                      >
                        Cancelar
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
