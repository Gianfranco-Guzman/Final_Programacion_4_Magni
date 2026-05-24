import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spinner } from '@components/Spinner'
import { useCartStore, selectCartTotal } from '@store/cartStore'
import { useCheckout } from '@hooks/useCheckout'
import { useDirecciones } from '@hooks/useDirecciones'
import { useFormasPago } from '@hooks/useFormasPago'

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate()
  const { items } = useCartStore()
  const total = useCartStore(selectCartTotal)
  const checkoutMutation = useCheckout()

  const { data: direcciones = [], isLoading: loadingDir } = useDirecciones()
  const { data: formasPago = [], isLoading: loadingFP } = useFormasPago()

  const direccionPrincipal = direcciones.find((d) => d.es_principal)
  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(
    direccionPrincipal?.id ?? null,
  )
  const [selectedFormaPagoId, setSelectedFormaPagoId] = useState<number | null>(
    formasPago[0]?.id ?? null,
  )
  const [notas, setNotas] = useState('')
  const [error, setError] = useState('')

  // Sync defaults once data loads
  React.useEffect(() => {
    if (direccionPrincipal && selectedDireccionId === null) {
      setSelectedDireccionId(direccionPrincipal.id)
    }
  }, [direcciones])

  React.useEffect(() => {
    if (formasPago.length > 0 && selectedFormaPagoId === null) {
      setSelectedFormaPagoId(formasPago[0].id)
    }
  }, [formasPago])

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

  const handleConfirmar = async () => {
    setError('')
    if (!selectedDireccionId) return setError('Seleccioná una dirección de entrega.')
    if (!selectedFormaPagoId) return setError('Seleccioná una forma de pago.')

    checkoutMutation.mutate(
      {
        direccion_entrega_id: selectedDireccionId,
        forma_pago_id: selectedFormaPagoId,
        items: items.map((i) => ({ producto_id: i.producto.id, cantidad: i.cantidad })),
        notas: notas.trim() || undefined,
      },
      {
        onError: (err: unknown) =>
          setError(err instanceof Error ? err.message : 'Error al confirmar el pedido'),
      },
    )
  }

  const isLoading = loadingDir || loadingFP

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
        {/* Left: forms */}
        <div className="lg:col-span-3 flex flex-col gap-6">

          {/* Dirección */}
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Dirección de entrega</h2>
            {direcciones.filter((d) => !d.deleted_at).length === 0 ? (
              <div className="text-sm text-gray-500">
                No tenés direcciones guardadas.{' '}
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

          {/* Forma de pago */}
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
                  />
                  <div>
                    <p className="font-medium text-sm text-gray-800">{fp.nombre}</p>
                    {fp.descripcion && <p className="text-xs text-gray-500">{fp.descripcion}</p>}
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Notas */}
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Notas (opcional)</h2>
            <textarea
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              rows={3}
              maxLength={500}
              placeholder="Indicaciones especiales, referencias de entrega..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            />
          </div>
        </div>

        {/* Right: order summary */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-5 sticky top-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Resumen</h2>

            <div className="flex flex-col gap-2 mb-4">
              {items.map((item) => (
                <div key={item.producto.id} className="flex justify-between text-sm">
                  <span className="text-gray-700 truncate pr-2">
                    {item.producto.nombre} <span className="text-gray-400">x{item.cantidad}</span>
                  </span>
                  <span className="font-medium text-gray-800 flex-shrink-0">
                    ${(item.producto.precio * item.cantidad).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>

            <div className="border-t pt-3 flex justify-between font-bold text-lg mb-6">
              <span>Total</span>
              <span className="text-blue-600">${total.toFixed(2)}</span>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-3 py-2 mb-4">
                {error}
              </div>
            )}

            <button
              onClick={handleConfirmar}
              disabled={checkoutMutation.isPending}
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {checkoutMutation.isPending ? 'Confirmando...' : 'Confirmar pedido'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
