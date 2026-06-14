import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { hasAnyRole } from '@/auth/permissions'
import { FeedbackAlert } from '@components/FeedbackAlert'
import { Spinner } from '@components/Spinner'
import { usePedido, useCancelarPedido } from '@hooks/usePedidos'
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

export const PedidoDetallePage: React.FC = () => {
  const { pedidoId } = useParams<{ pedidoId: string }>()
  const pedidoIdNumber = Number(pedidoId)
  const navigate = useNavigate()
  const usuario = useAuthStore((state) => state.usuario)
  const { data: pedido, isLoading, error, refetch } = usePedido(pedidoIdNumber)
  const cancelarMutation = useCancelarPedido()
  const [actionError, setActionError] = React.useState('')

  const handleWsMessage = React.useCallback((message: WsMessage) => {
    if (
      message.event === 'WS_CONNECTED' ||
      ['pedido_creado', 'estado_cambiado', 'pedido_cancelado', 'pago_confirmado'].includes(message.event)
    ) {
      void refetch()
    }
  }, [refetch])

  const { subscribeToOrder } = useWebSocket({
    enabled: !!usuario && hasAnyRole(usuario.roles, ['CLIENT', 'PEDIDOS', 'ADMIN']),
    onMessage: handleWsMessage,
  })

  React.useEffect(() => {
    if (pedidoIdNumber > 0) {
      subscribeToOrder(pedidoIdNumber)
    }
  }, [pedidoIdNumber, subscribeToOrder])

  const handleCancelar = () => {
    if (!window.confirm('¿Cancelar este pedido?')) return
    const observacion = window.prompt('Ingresá el motivo de cancelación:')?.trim()
    if (!observacion) {
      setActionError('Debés ingresar un motivo para cancelar el pedido.')
      return
    }
    setActionError('')
    cancelarMutation.mutate(
      { id: pedido!.id, observacion },
      {
        onSuccess: () => navigate('/pedidos'),
        onError: (err: unknown) => setActionError(err instanceof Error ? err.message : 'Error al cancelar'),
      },
    )
  }

  if (isLoading) return <div className="py-12"><Spinner /></div>

  if (error || !pedido) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error instanceof Error ? error.message : 'Pedido no encontrado'}</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-blue-600 hover:underline text-sm">
          Volver
        </button>
      </div>
    )
  }

  const estadoColor = ESTADO_COLORS[pedido.estado_actual] ?? 'bg-gray-100 text-gray-700'
  const estadoLabel = ESTADO_LABEL[pedido.estado_actual] ?? pedido.estado_actual
  const puedeCancel = ['PENDIENTE', 'CONFIRMADO'].includes(pedido.estado_actual)

  return (
    <div className="max-w-3xl mx-auto">
      <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        ← Volver a mis pedidos
      </button>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        {actionError && (
          <div className="mb-4">
            <FeedbackAlert title="No se pudo cancelar el pedido">{actionError}</FeedbackAlert>
          </div>
        )}
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-800">Pedido #{pedido.id}</h1>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${estadoColor}`}>
            {estadoLabel}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
          <div>
            <p className="font-medium text-gray-700">Total</p>
            <p className="text-2xl font-bold text-blue-600">${pedido.total.toFixed(2)}</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Fecha</p>
            <p>{new Date(pedido.created_at).toLocaleString('es-AR')}</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Dirección ID</p>
            <p>#{pedido.direccion_entrega_id}</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Forma de pago ID</p>
            <p>#{pedido.forma_pago_id}</p>
          </div>
        </div>

        {pedido.notas && (
          <div className="bg-gray-50 rounded p-3 text-sm text-gray-600 italic mb-4">
            Nota: "{pedido.notas}"
          </div>
        )}

        {puedeCancel && (
          <button
            onClick={handleCancelar}
            disabled={cancelarMutation.isPending}
            className="text-sm bg-red-50 text-red-600 border border-red-200 rounded px-4 py-2 hover:bg-red-100 disabled:opacity-50"
          >
            {cancelarMutation.isPending ? 'Cancelando...' : 'Cancelar pedido'}
          </button>
        )}
      </div>

      {pedido.detalles && pedido.detalles.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Ítems del pedido</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-2">Producto</th>
                <th className="pb-2 text-center">Cant.</th>
                <th className="pb-2 text-right">Precio unit.</th>
                <th className="pb-2 text-right">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {pedido.detalles.map((d) => (
                <tr key={d.id} className="border-b last:border-0">
                  <td className="py-2 font-medium text-gray-800">{d.nombre_producto_snapshot}</td>
                  <td className="py-2 text-center text-gray-600">{d.cantidad}</td>
                  <td className="py-2 text-right text-gray-600">${d.precio_unitario_snapshot.toFixed(2)}</td>
                  <td className="py-2 text-right font-semibold text-blue-700">${d.subtotal.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={3} className="pt-3 text-right font-semibold text-gray-700">Total:</td>
                <td className="pt-3 text-right font-bold text-blue-700 text-lg">${pedido.total.toFixed(2)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {pedido.historial && pedido.historial.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Historial de estados</h2>
          <div className="flex flex-col gap-3">
            {pedido.historial.map((h) => (
              <div key={h.id} className="flex items-start gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-gray-800">
                    {h.estado_anterior ? `${ESTADO_LABEL[h.estado_anterior] ?? h.estado_anterior} → ` : ''}
                    {ESTADO_LABEL[h.estado_nuevo] ?? h.estado_nuevo}
                  </p>
                  <p className="text-gray-500 text-xs">{new Date(h.fecha).toLocaleString('es-AR')}</p>
                  {h.observacion && <p className="text-gray-600 italic text-xs mt-0.5">"{h.observacion}"</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
