import React, { useCallback, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { hasAnyRole } from '@/auth/permissions'
import { FeedbackAlert } from '@components/FeedbackAlert'
import { Spinner } from '@components/Spinner'
import { usePedidos, useAvanzarEstado, useCancelarPedido } from '@hooks/usePedidos'
import { useWebSocket, WsMessage } from '@hooks/useWebSocket'
import { useAuthStore } from '@store/authStore'
import { Pedido } from '@models/index'

const ORDEN_ESTADOS = ['PENDIENTE', 'CONFIRMADO', 'EN_PREP', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO'] as const

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'border-t-yellow-400 bg-yellow-50',
  CONFIRMADO: 'border-t-blue-400 bg-blue-50',
  EN_PREP: 'border-t-orange-400 bg-orange-50',
  EN_CAMINO: 'border-t-purple-400 bg-purple-50',
  ENTREGADO: 'border-t-green-400 bg-green-50',
  CANCELADO: 'border-t-red-400 bg-red-50',
}

const ESTADO_BADGE: Record<string, string> = {
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

const ESTADOS_HISTORICOS = ['ENTREGADO', 'CANCELADO']
const MAX_HISTORICOS = 10

interface KanbanCardProps {
  pedido: Pedido
  onAvanzar: (id: number) => void
  onCancelar: (id: number) => void
  isBusy: boolean
}

function KanbanCard({ pedido, onAvanzar, onCancelar, isBusy }: KanbanCardProps) {
  const nextLabel = NEXT_LABEL[pedido.estado_actual]
  const puedeCancel = ['PENDIENTE', 'CONFIRMADO'].includes(pedido.estado_actual)

  return (
    <div className={`rounded-lg border border-t-4 bg-white shadow-sm p-3 ${ESTADO_COLORS[pedido.estado_actual] ?? 'border-t-gray-300 bg-white'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-bold text-gray-800 text-sm">#{pedido.id}</span>
        <Link
          to={`/pedidos/${pedido.id}`}
          className="text-xs text-blue-600 hover:underline"
        >
          Ver
        </Link>
      </div>
      <p className="text-xs text-gray-500 mb-1">
        {new Date(pedido.created_at).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })}
      </p>
      <p className="text-base font-bold text-blue-700 mb-2">${pedido.total.toFixed(2)}</p>
      {pedido.notas && (
        <p className="text-xs text-gray-500 italic mb-2 line-clamp-2">"{pedido.notas}"</p>
      )}
      <div className="flex flex-col gap-1">
        {nextLabel && (
          <button
            onClick={() => onAvanzar(pedido.id)}
            disabled={isBusy}
            className="w-full text-xs bg-blue-600 text-white rounded px-2 py-1.5 hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {nextLabel}
          </button>
        )}
        {puedeCancel && (
          <button
            onClick={() => onCancelar(pedido.id)}
            disabled={isBusy}
            className="w-full text-xs bg-red-50 text-red-600 border border-red-200 rounded px-2 py-1 hover:bg-red-100 disabled:opacity-50"
          >
            Cancelar
          </button>
        )}
      </div>
    </div>
  )
}

export const CajeroPage: React.FC = () => {
  const [actionError, setActionError] = useState('')
  const usuario = useAuthStore((state) => state.usuario)
  const { data: pedidos = [], isLoading, error, refetch } = usePedidos({ size: 100 })
  const avanzarMutation = useAvanzarEstado()
  const cancelarMutation = useCancelarPedido()

  const handleWsMessage = useCallback((message: WsMessage) => {
    if (
      message.event === 'WS_CONNECTED' ||
      ['pedido_creado', 'estado_cambiado', 'pedido_cancelado', 'pago_confirmado'].includes(message.event)
    ) {
      void refetch()
    }
  }, [refetch])

  useWebSocket({
    enabled: !!usuario && hasAnyRole(usuario.roles, ['PEDIDOS', 'ADMIN']),
    adminFeed: true,
    onMessage: handleWsMessage,
  })

  const pedidosByEstado = useMemo(() => {
    const groups: Record<string, Pedido[]> = {}
    ORDEN_ESTADOS.forEach((e) => { groups[e] = [] })
    pedidos.forEach((p) => {
      if (groups[p.estado_actual] !== undefined) {
        groups[p.estado_actual].push(p)
      }
    })
    ORDEN_ESTADOS.forEach((e) => {
      groups[e].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    })
    return groups
  }, [pedidos])

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

  const isBusy = avanzarMutation.isPending || cancelarMutation.isPending

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
          <p className="text-gray-500 text-sm mt-1">{pedidos.length} pedido(s) cargados</p>
        </div>
        <button
          onClick={() => refetch()}
          className="text-sm border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
        >
          Actualizar
        </button>
      </div>

      {actionError && (
        <div className="mb-4">
          <FeedbackAlert title="No se pudo completar la acción">{actionError}</FeedbackAlert>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-4">
          {ORDEN_ESTADOS.map((estado) => {
            const lista = pedidosByEstado[estado] ?? []
            const esHistorico = ESTADOS_HISTORICOS.includes(estado)
            const visible = esHistorico ? lista.slice(-MAX_HISTORICOS) : lista
            const ocultos = esHistorico ? Math.max(0, lista.length - MAX_HISTORICOS) : 0

            return (
              <div key={estado} className="flex-shrink-0 w-52 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${ESTADO_BADGE[estado] ?? 'bg-gray-100 text-gray-700'}`}>
                    {ESTADO_LABEL[estado]}
                  </span>
                  <span className="text-xs text-gray-400 font-medium">{lista.length}</span>
                </div>

                <div className="flex flex-col gap-2 min-h-[4rem]">
                  {ocultos > 0 && (
                    <p className="text-xs text-gray-400 text-center py-1">+{ocultos} anteriores</p>
                  )}
                  {visible.length === 0 ? (
                    <div className="rounded-lg border border-dashed border-gray-200 p-4 text-center text-xs text-gray-400">
                      Sin pedidos
                    </div>
                  ) : (
                    visible.map((pedido) => (
                      <KanbanCard
                        key={pedido.id}
                        pedido={pedido}
                        onAvanzar={handleAvanzar}
                        onCancelar={handleCancelar}
                        isBusy={isBusy}
                      />
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
