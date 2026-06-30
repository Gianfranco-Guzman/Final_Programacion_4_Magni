import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { hasAnyRole } from '@/auth/permissions'
import { FeedbackAlert } from '@components/FeedbackAlert'
import { Spinner } from '@components/Spinner'
import { usePedidos, useAvanzarEstado, useCancelarPedido } from '@hooks/usePedidos'
import { useFormasPago } from '@hooks/useFormasPago'
import { useWebSocket, WsMessage } from '@hooks/useWebSocket'
import { useAuthStore } from '@store/authStore'
import { FormaPago, Pedido } from '@models/index'

const ESTADOS_ACTIVOS = ['PENDIENTE', 'CONFIRMADO', 'EN_PREP', 'EN_CAMINO'] as const
const ESTADOS_HISTORICOS = ['ENTREGADO', 'CANCELADO'] as const

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'border-t-yellow-400 bg-yellow-50',
  CONFIRMADO: 'border-t-blue-400 bg-blue-50',
  EN_PREP: 'border-t-orange-400 bg-orange-50',
  EN_CAMINO: 'border-t-purple-400 bg-purple-50',
}

const ESTADO_BADGE: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREP: 'bg-orange-100 text-orange-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
}

const ESTADO_FILA_HISTORICO: Record<string, string> = {
  ENTREGADO: 'text-green-700',
  CANCELADO: 'text-red-600',
}

const ESTADO_LABEL: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREP: 'En preparación',
  EN_CAMINO: 'En camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}

const getEstadoLabel = (estado: string, tipoEntrega?: string): string => {
  if (estado === 'EN_CAMINO' && tipoEntrega === 'sucursal') return 'Listo para retirar'
  if (estado === 'ENTREGADO' && tipoEntrega === 'sucursal') return 'Retirado'
  return ESTADO_LABEL[estado] ?? estado
}

const NEXT_LABEL_DOMICILIO: Record<string, string> = {
  PENDIENTE: 'Confirmar',
  CONFIRMADO: 'Iniciar preparación',
  EN_PREP: 'Enviar',
  EN_CAMINO: 'Marcar entregado',
}

const NEXT_LABEL_SUCURSAL: Record<string, string> = {
  PENDIENTE: 'Confirmar',
  CONFIRMADO: 'Iniciar preparación',
  EN_PREP: 'Marcar listo para retirar',
  EN_CAMINO: 'Confirmar retiro',
}

const getNextLabel = (estado: string, tipoEntrega?: string): string | undefined => {
  const map = tipoEntrega === 'sucursal' ? NEXT_LABEL_SUCURSAL : NEXT_LABEL_DOMICILIO
  return map[estado]
}


const PAGO_BADGE: Record<string, string> = {
  MERCADOPAGO: 'bg-blue-100 text-blue-700',
  EFECTIVO: 'bg-green-100 text-green-700',
  TRANSFERENCIA: 'bg-purple-100 text-purple-700',
}

const PAGO_HINT: Record<string, Record<string, string>> = {
  PENDIENTE: {
    MERCADOPAGO: 'Esperando pago online',
    EFECTIVO: 'Cobrar al retirar',
    TRANSFERENCIA: 'Verificar transferencia',
  },
}

interface KanbanCardProps {
  pedido: Pedido
  formaPago: FormaPago | undefined
  onAvanzar: (id: number) => void
  onCancelar: (id: number) => void
  isBusy: boolean
}

function KanbanCard({ pedido, formaPago, onAvanzar, onCancelar, isBusy }: KanbanCardProps) {
  const nextLabel = getNextLabel(pedido.estado_actual, pedido.tipo_entrega)
  const puedeCancel = ['PENDIENTE', 'CONFIRMADO'].includes(pedido.estado_actual)
  const codigo = (formaPago?.codigo ?? formaPago?.nombre ?? '').toUpperCase()
  const hint = PAGO_HINT[pedido.estado_actual]?.[codigo]
  const isEsperandoMP = pedido.estado_actual === 'PENDIENTE' && codigo === 'MERCADOPAGO'

  return (
    <div className={`rounded-lg border border-t-4 bg-white shadow-sm p-3 ${ESTADO_COLORS[pedido.estado_actual] ?? 'border-t-gray-300 bg-white'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-bold text-gray-800 text-sm">#{pedido.id}</span>
        <Link to={`/pedidos/${pedido.id}`} className="text-xs text-blue-600 hover:underline">
          Ver
        </Link>
      </div>

      <p className="text-xs text-gray-500 mb-1">
        {new Date(pedido.created_at).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })}
      </p>

      <p className="text-base font-bold text-blue-700 mb-2">${pedido.total.toFixed(2)}</p>

      <div className="flex gap-1 flex-wrap mb-2">
        <span className="text-xs bg-gray-100 text-gray-600 rounded-full px-2 py-0.5">
          {pedido.tipo_entrega === 'sucursal' ? 'Retiro' : 'Domicilio'}
        </span>
        {formaPago && (
          <span className={`text-xs rounded-full px-2 py-0.5 font-medium ${PAGO_BADGE[codigo] ?? 'bg-gray-100 text-gray-600'}`}>
            {formaPago.nombre}
          </span>
        )}
      </div>

      {hint && (
        <p className={`text-xs mb-2 font-medium ${isEsperandoMP ? 'text-amber-600' : 'text-gray-500'}`}>
          {hint}
        </p>
      )}

      {pedido.notas && (
        <p className="text-xs text-gray-500 italic mb-2 line-clamp-2">"{pedido.notas}"</p>
      )}

      <div className="flex flex-col gap-1">
        {nextLabel && (
          <button
            onClick={() => onAvanzar(pedido.id)}
            disabled={isBusy}
            className={`w-full text-xs rounded px-2 py-1.5 disabled:opacity-50 font-medium ${
              isEsperandoMP
                ? 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isEsperandoMP ? 'Confirmar manualmente' : nextLabel}
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
  const [mostrarSubir, setMostrarSubir] = useState(false)
  const historialRef = useRef<HTMLDivElement>(null)
  const usuario = useAuthStore((state) => state.usuario)
  const { data: pedidos = [], isLoading, error, refetch } = usePedidos({ size: 100 })
  const { data: formasPago = [] } = useFormasPago()
  const formasPagoMap = useMemo(
    () => Object.fromEntries(formasPago.map((fp) => [fp.id, fp])),
    [formasPago],
  )
  const avanzarMutation = useAvanzarEstado()
  const cancelarMutation = useCancelarPedido()

  useEffect(() => {
    const onScroll = () => setMostrarSubir(window.scrollY > 300)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

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

  const { activos, historicos } = useMemo(() => {
    const grupos: Record<string, Pedido[]> = {}
    ;[...ESTADOS_ACTIVOS, ...ESTADOS_HISTORICOS].forEach((e) => { grupos[e] = [] })
    pedidos.forEach((p) => {
      if (grupos[p.estado_actual] !== undefined) grupos[p.estado_actual].push(p)
    })
    ESTADOS_ACTIVOS.forEach((e) => {
      grupos[e].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    })
    const hist = [...(grupos['ENTREGADO'] ?? []), ...(grupos['CANCELADO'] ?? [])]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    return { activos: grupos, historicos: hist }
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
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Panel cajero</h1>
        </div>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => historialRef.current?.scrollIntoView({ behavior: 'smooth' })}
            className="text-sm text-blue-600 border border-blue-200 bg-blue-50 rounded px-4 py-2 hover:bg-blue-100"
          >
            Ver historial
          </button>
          <button
            onClick={() => refetch()}
            className="text-sm border border-gray-300 rounded px-3 py-2 hover:bg-gray-50"
          >
            Actualizar
          </button>
        </div>
      </div>

      {actionError && (
        <div>
          <FeedbackAlert title="No se pudo completar la acción">{actionError}</FeedbackAlert>
        </div>
      )}

      {isLoading ? (
        <div className="py-12"><Spinner /></div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pb-4">
          {ESTADOS_ACTIVOS.map((estado) => {
            const lista = activos[estado] ?? []
            return (
              <div key={estado} className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${ESTADO_BADGE[estado]}`}>
                    {ESTADO_LABEL[estado]}
                  </span>
                  <span className="text-xs text-gray-400 font-medium">{lista.length}</span>
                </div>
                <div className="flex flex-col gap-2 overflow-y-auto max-h-[70vh] pr-0.5">
                  {lista.length === 0 ? (
                    <div className="rounded-lg border border-dashed border-gray-200 p-4 text-center text-xs text-gray-400">
                      Sin pedidos
                    </div>
                  ) : (
                    lista.map((pedido) => (
                      <KanbanCard
                        key={pedido.id}
                        pedido={pedido}
                        formaPago={formasPagoMap[pedido.forma_pago_id]}
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

      <div ref={historialRef}>
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Historial de pedidos</h2>
        {historicos.length === 0 ? (
          <p className="text-sm text-gray-400">No hay pedidos entregados ni cancelados todavía.</p>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notas</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {historicos.map((pedido) => (
                  <tr key={pedido.id} className="hover:bg-gray-50">
                    <td className="px-5 py-3 text-sm font-medium text-gray-800">#{pedido.id}</td>
                    <td className="px-5 py-3 text-sm text-gray-500 whitespace-nowrap">
                      {new Date(pedido.created_at).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="px-5 py-3 text-sm font-semibold text-gray-800">${pedido.total.toFixed(2)}</td>
                    <td className={`px-5 py-3 text-sm text-center font-semibold ${ESTADO_BADGE[pedido.estado_actual]}`}>
                      {getEstadoLabel(pedido.estado_actual, pedido.tipo_entrega)}
                    </td>
                    <td className={`px-5 py-3 text-xs max-w-xs truncate ${ESTADO_FILA_HISTORICO[pedido.estado_actual] ?? 'text-gray-500'}`}>
                      {pedido.notas ?? '—'}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <Link
                        to={`/pedidos/${pedido.id}`}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Ver detalle
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {mostrarSubir && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="fixed bottom-6 right-6 bg-white border border-gray-300 text-gray-600 rounded-full w-10 h-10 flex items-center justify-center shadow-md hover:bg-gray-50"
          aria-label="Volver arriba"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
        </button>
      )}
    </div>
  )
}
