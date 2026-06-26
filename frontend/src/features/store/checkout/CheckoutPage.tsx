import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CardPayment, initMercadoPago } from '@mercadopago/sdk-react'

import { Spinner } from '@components/Spinner'
import { ItemCarrito } from '@features/store/carrito/ItemCarrito'
import { useCheckout } from '@hooks/useCheckout'
import { useDirecciones } from '@hooks/useDirecciones'
import { useFormasPago } from '@hooks/useFormasPago'
import { useCreatePago } from '@hooks/usePagos'
import { Pedido, TipoEntrega, Usuario } from '@models/index'
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

const EFECTIVO_CODE = 'EFECTIVO'

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate()
  const usuario = useAuthStore((state) => state.usuario)
  const { items, clearCart } = useCartStore()
  const total = useCartStore(selectCartTotal)
  const checkoutMutation = useCheckout()
  const pagoMutation = useCreatePago()

  const { data: direcciones = [], isLoading: loadingDir } = useDirecciones()
  const { data: rawFormasPago = [], isLoading: loadingFP } = useFormasPago()

  const [tipoEntrega, setTipoEntrega] = useState<TipoEntrega>('domicilio')
  const direccionPrincipal = direcciones.find((d) => d.es_principal)
  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(null)
  const [selectedFormaPagoId, setSelectedFormaPagoId] = useState<number | null>(null)
  const [notas, setNotas] = useState('')
  const [error, setError] = useState('')
  const [mpError, setMpError] = useState('')
  const [pedidoCreado, setPedidoCreado] = useState<Pedido | null>(null)
  const [mpCardReady, setMpCardReady] = useState(false)

  const mpSectionRef = useRef<HTMLDivElement>(null)

  const hasInvalidStock = items.some((item) => item.cantidad > getProductoStockDisponible(item.producto))

  const formasPagoDisponibles = useMemo(() => {
    if (tipoEntrega === 'sucursal') return rawFormasPago
    return rawFormasPago.filter((fp) => (fp.codigo ?? fp.nombre) !== EFECTIVO_CODE)
  }, [rawFormasPago, tipoEntrega])

  const formaPagoSeleccionada = useMemo(
    () => formasPagoDisponibles.find((fp) => fp.id === selectedFormaPagoId) ?? null,
    [formasPagoDisponibles, selectedFormaPagoId],
  )

  const isMercadoPago = (formaPagoSeleccionada?.codigo ?? formaPagoSeleccionada?.nombre) === 'MERCADOPAGO'
  const mercadoPagoPublicKey = import.meta.env.VITE_MP_PUBLIC_KEY

  useEffect(() => {
    if (direccionPrincipal && selectedDireccionId === null) {
      setSelectedDireccionId(direccionPrincipal.id)
    }
  }, [direccionPrincipal, selectedDireccionId])

  useEffect(() => {
    if (formasPagoDisponibles.length > 0) {
      const seleccionadaAunDisponible = formasPagoDisponibles.some((fp) => fp.id === selectedFormaPagoId)
      if (!seleccionadaAunDisponible) {
        setSelectedFormaPagoId(formasPagoDisponibles[0].id)
      }
    }
  }, [formasPagoDisponibles, selectedFormaPagoId])

  useEffect(() => {
    if (mercadoPagoPublicKey) {
      initMercadoPago(mercadoPagoPublicKey, { locale: 'es-AR' })
    }
  }, [mercadoPagoPublicKey])

  const handleMpReady = () => {
    setMpCardReady(true)
    setTimeout(() => {
      if (mpSectionRef.current) {
        const el = mpSectionRef.current
        const top = el.getBoundingClientRect().top + window.scrollY - 80
        window.scrollTo({ top, behavior: 'smooth' })
      }
    }, 600)
  }

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <p className="text-gray-500 mb-4">El carrito está vacío.</p>
        <button onClick={() => navigate('/catalogo')} className="text-blue-600 hover:underline text-sm">
          Volver al catálogo
        </button>
      </div>
    )
  }

  const handleTipoEntregaChange = (tipo: TipoEntrega) => {
    setTipoEntrega(tipo)
  }

  const handleConfirmar = () => {
    setError('')
    if (tipoEntrega === 'domicilio' && !selectedDireccionId) {
      return setError('Seleccioná una dirección de entrega.')
    }
    if (!selectedFormaPagoId) return setError('Seleccioná una forma de pago.')
    if (hasInvalidStock) return setError('Hay productos con cantidades mayores al stock disponible.')

    checkoutMutation.mutate(
      {
        tipo_entrega: tipoEntrega,
        direccion_entrega_id: tipoEntrega === 'domicilio' ? selectedDireccionId! : null,
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
    setMpError('')
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
      setMpError(err instanceof Error ? err.message : 'No se pudo procesar el pago. Verificá los datos e intentá de nuevo.')
      return
    }
    clearCart()
    navigate(`/pedidos/${pedidoCreado.id}`)
  }

  const isLoading = loadingDir || loadingFP
  const isBusy = checkoutMutation.isPending || pagoMutation.isPending

  if (isLoading) return <div className="py-12"><Spinner /></div>

  return (
    <div className="max-w-4xl mx-auto">
      <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-6 inline-block">
        ← Volver
      </button>

      <h1 className="text-3xl font-bold text-gray-800 mb-8">Checkout</h1>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8">

        <div className="order-first md:order-last md:col-span-2 md:self-start md:sticky md:top-20">
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Resumen</h2>
              {!pedidoCreado && (
                <button onClick={() => navigate('/catalogo')} className="text-xs text-blue-600 hover:underline">
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

        <div className="order-last md:order-first md:col-span-3 flex flex-col gap-6">

          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">¿Cómo querés recibir tu pedido?</h2>
            <div className="flex flex-col gap-3">
              <label className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${tipoEntrega === 'domicilio' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="tipo_entrega" value="domicilio" checked={tipoEntrega === 'domicilio'} onChange={() => handleTipoEntregaChange('domicilio')} className="mt-0.5 accent-blue-600" disabled={!!pedidoCreado} />
                <div>
                  <p className="font-medium text-sm text-gray-800">Entrega a domicilio</p>
                  <p className="text-xs text-gray-500">Te lo llevamos a tu dirección</p>
                </div>
              </label>
              <label className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${tipoEntrega === 'sucursal' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="tipo_entrega" value="sucursal" checked={tipoEntrega === 'sucursal'} onChange={() => handleTipoEntregaChange('sucursal')} className="mt-0.5 accent-blue-600" disabled={!!pedidoCreado} />
                <div>
                  <p className="font-medium text-sm text-gray-800">Retiro en sucursal</p>
                  <p className="text-xs text-gray-500">Retirá en el local · Podés pagar en efectivo</p>
                </div>
              </label>
            </div>
          </div>

          {tipoEntrega === 'domicilio' && (
            <div className="bg-white rounded-lg shadow p-5">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Dirección de entrega</h2>
              {direcciones.filter((d) => !d.deleted_at).length === 0 ? (
                <div className="text-sm text-gray-500">
                  No tenés direcciones guardadas.{` `}
                  <button onClick={() => navigate('/direcciones')} className="text-blue-600 hover:underline">
                    Agregar dirección
                  </button>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  {direcciones.filter((d) => !d.deleted_at).map((d) => (
                    <label key={d.id} className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${selectedDireccionId === d.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                      <input type="radio" name="direccion" value={d.id} checked={selectedDireccionId === d.id} onChange={() => setSelectedDireccionId(d.id)} className="mt-0.5 accent-blue-600" disabled={!!pedidoCreado} />
                      <div>
                        <p className="font-medium text-sm text-gray-800">
                          {d.etiqueta || 'Dirección'}{' '}
                          {d.es_principal && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full ml-1">Principal</span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500">{d.linea1}, {d.ciudad}</p>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {tipoEntrega === 'sucursal' && (
            <div className="bg-white rounded-lg shadow p-5">
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Punto de retiro</h2>
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
                <p className="font-medium text-gray-800 mb-1">Sucursal principal</p>
                <p>Av. Corrientes 1234, CABA</p>
                <p className="text-gray-500 mt-1">Lun a Sáb · 9 hs a 20 hs</p>
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Notas para el pedido (opcional)</h2>
            <textarea
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              rows={2}
              maxLength={500}
              placeholder="Indicaciones de entrega, referencias, alergias..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
              disabled={!!pedidoCreado}
            />
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Forma de pago</h2>
            <div className="flex flex-col gap-3">
              {formasPagoDisponibles.map((fp) => {
                const codigo = fp.codigo ?? fp.nombre
                const isSelected = selectedFormaPagoId === fp.id
                return (
                  <label key={fp.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input type="radio" name="forma_pago" value={fp.id} checked={isSelected} onChange={() => setSelectedFormaPagoId(fp.id)} className="accent-blue-600" disabled={!!pedidoCreado} />
                    <div>
                      <p className="font-medium text-sm text-gray-800">{fp.nombre}</p>
                      {codigo === EFECTIVO_CODE
                        ? <p className="text-xs text-gray-500">Pago al momento del retiro</p>
                        : fp.descripcion && <p className="text-xs text-gray-500">{fp.descripcion}</p>
                      }
                    </div>
                  </label>
                )
              })}
            </div>
          </div>

          {pedidoCreado && isMercadoPago && (
            <div ref={mpSectionRef} className="bg-white rounded-lg shadow p-5">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Completá el pago</h2>
              {mpError && (
                <div className="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {mpError}
                </div>
              )}
              {mercadoPagoPublicKey ? (
                <div className="relative min-h-[200px]">
                  {(!mpCardReady || pagoMutation.isPending) && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white z-10 rounded">
                      <Spinner />
                    </div>
                  )}
                  <CardPayment
                    initialization={{ amount: total, payer: buildMercadoPagoPayer(usuario) }}
                    onSubmit={handleMercadoPagoSubmit}
                    onReady={handleMpReady}
                    onError={() => undefined}
                  />
                </div>
              ) : (
                <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                  Falta configurar <code>VITE_MP_PUBLIC_KEY</code> en el frontend para habilitar MercadoPago.
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
