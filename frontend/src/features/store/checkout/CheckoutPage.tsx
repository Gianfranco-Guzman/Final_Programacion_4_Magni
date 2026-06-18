import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CardPayment, initMercadoPago } from '@mercadopago/sdk-react'

import { Spinner } from '@components/Spinner'
import { ItemCarrito } from '@features/store/carrito/ItemCarrito'
import { useCheckout } from '@hooks/useCheckout'
import { useDirecciones } from '@hooks/useDirecciones'
import { useFormasPago } from '@hooks/useFormasPago'
import { useCreatePago } from '@hooks/usePagos'
import { Pedido, Usuario } from '@models/index'
import { useAuthStore } from '@store/authStore'
import { useCartStore, selectCartTotal } from '@store/cartStore'
import { getProductoPrecioFinal, getProductoStockDisponible } from '@/utils/producto'

type MercadoPagoCardFormData = {
  token: string
  payment_method_id: string
  installments?: number | string
  issuer_id?: string
  payer?: {
    email?: string
  }
}

const buildMercadoPagoPayer = (usuario: Usuario | null) => {
  if (!usuario?.email) return undefined
  return { email: usuario.email }
}

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate()
  const usuario = useAuthStore((state) => state.usuario)
  const { items, clearCart } = useCartStore()
  const total = useCartStore(selectCartTotal)
  const checkoutMutation = useCheckout()
  const pagoMutation = useCreatePago()

  const { data: direcciones = [], isLoading: loadingDir } = useDirecciones()
  const { data: formasPago = [], isLoading: loadingFP } = useFormasPago()

  const direccionPrincipal = direcciones.find((d) => d.es_principal)
  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(direccionPrincipal?.id ?? null)
  const [selectedFormaPagoId, setSelectedFormaPagoId] = useState<number | null>(null)
  const [notas, setNotas] = useState('')
  const [error, setError] = useState('')
  const [pedidoCreado, setPedidoCreado] = useState<Pedido | null>(null)

  const hasInvalidStock = items.some((item) => item.cantidad > getProductoStockDisponible(item.producto))

  const formaPagoSeleccionada = useMemo(
    () => formasPago.find((formaPago) => formaPago.id === selectedFormaPagoId) ?? null,
    [formasPago, selectedFormaPagoId],
  )

  const isMercadoPago = (formaPagoSeleccionada?.codigo ?? formaPagoSeleccionada?.nombre) === 'MERCADOPAGO'
  const mercadoPagoPublicKey = import.meta.env.VITE_MP_PUBLIC_KEY

  useEffect(() => {
    if (direccionPrincipal && selectedDireccionId === null) {
      setSelectedDireccionId(direccionPrincipal.id)
    }
  }, [direccionPrincipal, selectedDireccionId])

  useEffect(() => {
    if (formasPago.length > 0 && selectedFormaPagoId === null) {
      setSelectedFormaPagoId(formasPago[0].id)
    }
  }, [formasPago, selectedFormaPagoId])

  useEffect(() => {
    if (mercadoPagoPublicKey) {
      initMercadoPago(mercadoPagoPublicKey, { locale: 'es-AR' })
    }
  }, [mercadoPagoPublicKey])

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <p className="text-gray-500 mb-4">El carrito está vacío.</p>
        <button
          onClick={() => navigate('/catalogo')}
          className="text-blue-600 hover:underline text-sm"
        >
          Volver al catálogo
        </button>
      </div>
    )
  }

  const handleConfirmar = () => {
    setError('')
    if (!selectedDireccionId) return setError('Seleccioná una dirección de entrega.')
    if (!selectedFormaPagoId) return setError('Seleccioná una forma de pago.')
    if (hasInvalidStock) return setError('Hay productos con cantidades mayores al stock disponible.')

    checkoutMutation.mutate(
      {
        direccion_entrega_id: selectedDireccionId,
        forma_pago_id: selectedFormaPagoId,
        items: items.map((item) => ({ producto_id: item.producto.id, cantidad: item.cantidad })),
        notas: notas.trim() || undefined,
      },
      {
        onSuccess: (pedido) => {
          if (isMercadoPago) {
            setPedidoCreado(pedido)
            return
          }

          clearCart()
          navigate(`/pedidos/${pedido.id}`)
        },
        onError: (err: unknown) =>
          setError(err instanceof Error ? err.message : 'Error al confirmar el pedido'),
      },
    )
  }

  const handleMercadoPagoSubmit = async (formData: MercadoPagoCardFormData) => {
    if (!pedidoCreado) {
      setError('Primero debés crear el pedido.')
      return
    }

    setError('')

    try {
      await pagoMutation.mutateAsync({
        pedido_id: pedidoCreado.id,
        token: formData.token,
        payment_method_id: formData.payment_method_id,
        installments: Number(formData.installments ?? 1),
        issuer_id: formData.issuer_id,
        payer_email: formData.payer?.email ?? usuario?.email ?? undefined,
      })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'No se pudo procesar el pago')
      return
    }

    clearCart()
    navigate(`/pedidos/${pedidoCreado.id}`)
  }

  const isLoading = loadingDir || loadingFP
  const isBusy = checkoutMutation.isPending || pagoMutation.isPending

  if (isLoading) return <div className="py-12"><Spinner /></div>

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-blue-600 hover:underline mb-6 inline-block"
      >
        ← Volver
      </button>

      <h1 className="text-3xl font-bold text-gray-800 mb-8">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Dirección de entrega</h2>
            {direcciones.filter((d) => !d.deleted_at).length === 0 ? (
              <div className="text-sm text-gray-500">
                No tenés direcciones guardadas.{` `}
                <button
                  onClick={() => navigate('/direcciones')}
                  className="text-blue-600 hover:underline"
                >
                  Agregar dirección
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {direcciones
                  .filter((d) => !d.deleted_at)
                  .map((d) => (
                    <label
                      key={d.id}
                      className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedDireccionId === d.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="direccion"
                        value={d.id}
                        checked={selectedDireccionId === d.id}
                        onChange={() => setSelectedDireccionId(d.id)}
                        className="mt-0.5 accent-blue-600"
                        disabled={!!pedidoCreado}
                      />
                      <div>
                        <p className="font-medium text-sm text-gray-800">
                          {d.etiqueta || 'Dirección'}{' '}
                          {d.es_principal && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full ml-1">
                              Principal
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500">{d.linea1}, {d.ciudad}</p>
                      </div>
                    </label>
                  ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Forma de pago</h2>
            <div className="flex flex-col gap-3">
              {formasPago.map((fp) => (
                <label
                  key={fp.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedFormaPagoId === fp.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="forma_pago"
                    value={fp.id}
                    checked={selectedFormaPagoId === fp.id}
                    onChange={() => setSelectedFormaPagoId(fp.id)}
                    className="accent-blue-600"
                    disabled={!!pedidoCreado}
                  />
                  <div>
                    <p className="font-medium text-sm text-gray-800">{fp.nombre}</p>
                    {fp.descripcion && <p className="text-xs text-gray-500">{fp.descripcion}</p>}
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Notas (opcional)</h2>
            <textarea
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              rows={3}
              maxLength={500}
              placeholder="Indicaciones especiales, referencias de entrega..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
              disabled={!!pedidoCreado}
            />
          </div>

          {pedidoCreado && isMercadoPago && (
            <div className="bg-white rounded-lg shadow p-5">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Pago con MercadoPago</h2>
              <div className="mb-4 rounded border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-800">
                Pedido #{pedidoCreado.id} creado correctamente. Completá el pago para finalizar.
              </div>

              {mercadoPagoPublicKey ? (
                <CardPayment
                  initialization={{
                    amount: total,
                    payer: buildMercadoPagoPayer(usuario),
                  }}
                  onSubmit={handleMercadoPagoSubmit}
                  onReady={() => undefined}
                  onError={(mpError: { message?: string }) => {
                    setError(mpError?.message || 'No se pudo procesar el formulario de pago')
                  }}
                />
              ) : (
                <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                  Falta configurar <code>VITE_MP_PUBLIC_KEY</code> en el frontend para habilitar MercadoPago.
                </div>
              )}
            </div>
          )}
        </div>

        <div className="lg:col-span-2 lg:self-start lg:sticky lg:top-4">
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Resumen</h2>
              {!pedidoCreado && (
                <button
                  onClick={() => navigate('/catalogo')}
                  className="text-xs text-blue-600 hover:underline"
                >
                  + Agregar productos
                </button>
              )}
            </div>

            <div className="flex flex-col mb-4">
              {pedidoCreado
                ? items.map((item) => (
                    <div key={item.producto.id} className="flex justify-between text-sm py-2 border-b border-gray-100 last:border-0">
                      <span className="text-gray-700 truncate pr-2">
                        {item.producto.nombre} <span className="text-gray-400">x{item.cantidad}</span>
                      </span>
                      <span className="font-medium text-gray-800 flex-shrink-0">
                        ${(getProductoPrecioFinal(item.producto) * item.cantidad).toFixed(2)}
                      </span>
                    </div>
                  ))
                : items.map((item) => <ItemCarrito key={item.producto.id} item={item} />)}
            </div>

            {hasInvalidStock && (
              <div className="mb-4 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                Revisá el carrito: una o más cantidades superan el stock disponible actual.
              </div>
            )}

            <div className="border-t pt-3 flex justify-between font-bold text-lg mb-6">
              <span>Total</span>
              <span className="text-blue-600">${total.toFixed(2)}</span>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2 mb-4">
                {error}
              </div>
            )}

            {!pedidoCreado && (
              <button
                onClick={handleConfirmar}
                disabled={isBusy || hasInvalidStock}
                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {checkoutMutation.isPending
                  ? 'Confirmando...'
                  : isMercadoPago
                    ? 'Continuar al pago'
                    : 'Confirmar pedido'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
