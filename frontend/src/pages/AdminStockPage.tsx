import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useIngredientes, useCargarStock, useMisCargas, useCorregirEntrada } from '@hooks/useIngredientes'
import { MovimientoEntrada } from '@api/ingredientesApi'
import { Spinner } from '@components/Spinner'
import { Ingrediente } from '@models/index'

type StockNivel = 'critico' | 'minimo' | 'bajo' | 'ok'

const UNIDADES_COMPRA: Record<string, string> = {
  GRAMO:     'kg',
  MILILITRO: 'L',
  UNIDAD:    'unidad',
  KILOGRAMO: 'kg',
  LITRO:     'L',
}

function getNivel(ingrediente: Ingrediente): StockNivel {
  const actual = Number(ingrediente.stock_actual)
  const minimo = Number(ingrediente.stock_minimo)
  if (minimo === 0) return 'ok'
  if (actual < minimo) return 'critico'
  if (actual <= minimo * 1.1) return 'minimo'
  if (actual <= minimo * 1.5) return 'bajo'
  return 'ok'
}

const NIVEL_ORDEN: Record<StockNivel, number> = { critico: 0, minimo: 1, bajo: 2, ok: 3 }

const NIVEL_ESTILOS: Record<StockNivel, { fila: string; badge: string; label: string }> = {
  critico: { fila: 'bg-red-50',    badge: 'bg-red-100 text-red-700',       label: 'Crítico' },
  minimo:  { fila: 'bg-orange-50', badge: 'bg-orange-100 text-orange-700', label: 'En mínimo' },
  bajo:    { fila: 'bg-yellow-50', badge: 'bg-yellow-100 text-yellow-700', label: 'Stock bajo' },
  ok:      { fila: '',             badge: 'bg-green-100 text-green-700',   label: 'OK' },
}

function fmt(n: number): string {
  if (Number.isInteger(n)) return String(n)
  return parseFloat(n.toFixed(3)).toString()
}

function formatValor(val: number, unidad: string): string {
  if (unidad === 'GRAMO') {
    if (val >= 1000) return `${fmt(val / 1000)} kg`
    return `${fmt(val)} g`
  }
  if (unidad === 'MILILITRO') {
    if (val >= 1000) return `${fmt(val / 1000)} L`
    return `${fmt(val)} ml`
  }
  return val === 1 ? '1 unidad' : `${fmt(val)} unidades`
}

function formatStock(ingrediente: Ingrediente): string {
  return formatValor(Number(ingrediente.stock_actual), ingrediente.unidad_medida)
}

function formatMinimo(ingrediente: Ingrediente): string {
  const minimo = Number(ingrediente.stock_minimo)
  if (minimo === 0) return '—'
  return formatValor(minimo, ingrediente.unidad_medida)
}

function formatFecha(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })
}

const FACTORES_BASE: Record<string, Record<string, number>> = {
  GRAMO:     { kg: 1000 },
  MILILITRO: { L: 1000 },
  UNIDAD:    { unidad: 1 },
  KILOGRAMO: { kg: 1 },
  LITRO:     { L: 1 },
}

interface CorreccionState {
  movimientoId: number
  ingredienteId: number
  cantidadMaxBase: number
  unidadMedida: string
  cantidad: string
  motivo: string
  error: string
}

export const AdminStockPage: React.FC = () => {
  const { data: ingredientes = [], isLoading } = useIngredientes()
  const { data: misCargas = [], isLoading: cargandoHistorial } = useMisCargas()
  const cargarStockMutation = useCargarStock()
  const corregirMutation = useCorregirEntrada()

  const [expandido, setExpandido] = useState<number | null>(null)
  const [cantidad, setCantidad] = useState('')
  const [errorLocal, setErrorLocal] = useState('')

  const [correccion, setCorreccion] = useState<CorreccionState | null>(null)
  const historialRef = useRef<HTMLDivElement>(null)
  const [mostrarSubir, setMostrarSubir] = useState(false)

  useEffect(() => {
    const onScroll = () => setMostrarSubir(window.scrollY > 300)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const ingredientesMap = useMemo(
    () => Object.fromEntries(ingredientes.map((i) => [i.id, i])),
    [ingredientes],
  )

  const ordenados = useMemo(
    () => [...ingredientes]
      .filter((i) => !i.deleted_at)
      .sort((a, b) => NIVEL_ORDEN[getNivel(a)] - NIVEL_ORDEN[getNivel(b)]),
    [ingredientes],
  )

  const entradas = useMemo(
    () => misCargas.filter((m) => m.tipo_movimiento === 'ENTRADA_STOCK'),
    [misCargas],
  )

  const correcciones = useMemo(() => {
    const map: Record<number, MovimientoEntrada[]> = {}
    for (const m of misCargas) {
      if (m.tipo_movimiento === 'CORRECCION_ENTRADA' && m.movimiento_referencia_id != null) {
        if (!map[m.movimiento_referencia_id]) map[m.movimiento_referencia_id] = []
        map[m.movimiento_referencia_id].push(m)
      }
    }
    return map
  }, [misCargas])

  const abrirExpandido = (ing: Ingrediente) => {
    setExpandido(ing.id)
    setCantidad('')
    setErrorLocal('')
    setCorreccion(null)
  }

  const cerrar = () => {
    setExpandido(null)
    setCantidad('')
    setErrorLocal('')
  }

  const confirmarCarga = (ing: Ingrediente) => {
    const num = Number(cantidad)
    if (!cantidad || isNaN(num) || num <= 0) {
      setErrorLocal('Ingresá una cantidad válida mayor a 0')
      return
    }
    const unidad = UNIDADES_COMPRA[ing.unidad_medida] ?? 'unidad'
    setErrorLocal('')
    cargarStockMutation.mutate(
      { id: ing.id, cantidad: num, unidad_entrada: unidad },
      { onSuccess: () => cerrar() },
    )
  }

  const abrirCorreccion = (entrada: MovimientoEntrada) => {
    const ing = ingredientesMap[entrada.ingrediente_id]
    if (!ing) return
    const disponibleBase = Number(entrada.cantidad) - Number(entrada.ya_corregido_total)
    setCorreccion({
      movimientoId: entrada.id,
      ingredienteId: entrada.ingrediente_id,
      cantidadMaxBase: disponibleBase,
      unidadMedida: ing.unidad_medida,
      cantidad: '',
      motivo: '',
      error: '',
    })
  }

  const confirmarCorreccion = () => {
    if (!correccion) return
    const num = Number(correccion.cantidad)
    const unidad = UNIDADES_COMPRA[correccion.unidadMedida] ?? 'unidad'
    const factor = FACTORES_BASE[correccion.unidadMedida]?.[unidad] ?? 1
    const enBase = num * factor

    if (!correccion.cantidad || isNaN(num) || num <= 0) {
      setCorreccion({ ...correccion, error: 'Ingresá una cantidad válida' })
      return
    }
    if (enBase > correccion.cantidadMaxBase) {
      const ing = ingredientesMap[correccion.ingredienteId]
      const maxLeg = correccion.cantidadMaxBase / factor
      setCorreccion({ ...correccion, error: `Máximo: ${fmt(maxLeg)} ${unidad} (${formatValor(correccion.cantidadMaxBase, ing?.unidad_medida ?? '')})` })
      return
    }
    if (correccion.motivo.trim().length < 3) {
      setCorreccion({ ...correccion, error: 'El motivo es obligatorio' })
      return
    }
    corregirMutation.mutate(
      {
        movimiento_id: correccion.movimientoId,
        cantidad: num,
        unidad_entrada: unidad,
        motivo: correccion.motivo.trim(),
      },
      { onSuccess: () => setCorreccion(null) },
    )
  }

  if (isLoading) return <div className="py-12"><Spinner /></div>

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 mb-1">Gestión de stock</h1>
          <p className="text-sm text-gray-500">Ingredientes ordenados por urgencia. Los críticos aparecen primero.</p>
        </div>
        <button
          onClick={() => historialRef.current?.scrollIntoView({ behavior: 'smooth' })}
          className="shrink-0 text-sm text-blue-600 border border-blue-200 bg-blue-50 rounded px-4 py-2 hover:bg-blue-100"
        >
          Ver historial de cargas
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ingrediente</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock actual</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mínimo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {ordenados.map((ing) => {
              const nivel = getNivel(ing)
              const estilos = NIVEL_ESTILOS[nivel]
              const abierto = expandido === ing.id
              const unidad = UNIDADES_COMPRA[ing.unidad_medida] ?? 'unidad'

              return (
                <React.Fragment key={ing.id}>
                  <tr className={estilos.fila}>
                    <td className="px-6 py-3 text-sm font-medium text-gray-900">{ing.nombre}</td>
                    <td className="px-6 py-3 text-sm text-gray-700">{formatStock(ing)}</td>
                    <td className="px-6 py-3 text-sm text-gray-500">{formatMinimo(ing)}</td>
                    <td className="px-6 py-3">
                      {nivel !== 'ok' && (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${estilos.badge}`}>
                          {estilos.label}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3 text-right">
                      {!abierto && (
                        <button
                          onClick={() => abrirExpandido(ing)}
                          className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded px-3 py-1 hover:bg-blue-100"
                        >
                          Actualizar stock
                        </button>
                      )}
                    </td>
                  </tr>
                  {abierto && (
                    <tr className="bg-blue-50 border-l-4 border-blue-400">
                      <td colSpan={5} className="px-6 py-4">
                        <p className="text-xs font-medium text-gray-600 mb-2">
                          {ing.nombre} — actual: {formatStock(ing)}
                        </p>
                        <div className="flex items-center gap-2">
                          <input
                            type="number"
                            min="0.001"
                            step="any"
                            value={cantidad}
                            onChange={(e) => { setCantidad(e.target.value); setErrorLocal('') }}
                            placeholder="Cantidad"
                            className="w-32 rounded border border-gray-300 px-3 py-1.5 text-sm [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                            autoFocus
                          />
                          <span className="text-sm text-gray-600 font-medium">{unidad}</span>
                          <button
                            onClick={() => confirmarCarga(ing)}
                            disabled={cargarStockMutation.isPending}
                            className="rounded bg-blue-600 text-white text-sm px-4 py-1.5 hover:bg-blue-700 disabled:opacity-50"
                          >
                            {cargarStockMutation.isPending ? 'Guardando...' : 'Confirmar'}
                          </button>
                          <button
                            onClick={cerrar}
                            disabled={cargarStockMutation.isPending}
                            className="rounded border border-gray-300 text-gray-600 text-sm px-4 py-1.5 hover:bg-gray-50 disabled:opacity-50"
                          >
                            Cancelar
                          </button>
                        </div>
                        {errorLocal && <p className="text-xs text-red-600 mt-1">{errorLocal}</p>}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      <div ref={historialRef}>
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Mis cargas de stock</h2>
        {cargandoHistorial ? (
          <Spinner />
        ) : entradas.length === 0 ? (
          <p className="text-sm text-gray-400">No realizaste cargas de stock todavía.</p>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ingrediente</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cargaste</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ya corregido</th>
                  <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {entradas.map((entrada) => {
                  const ing = ingredientesMap[entrada.ingrediente_id]
                  const unidadMedida = ing?.unidad_medida ?? ''
                  const disponibleBase = Number(entrada.cantidad) - Number(entrada.ya_corregido_total)
                  const yaCorregidoBase = Number(entrada.ya_corregido_total)
                  const puedeCorregir = disponibleBase > 0
                  const esCorreccionActiva = correccion?.movimientoId === entrada.id
                  const correccionesDeEsta = correcciones[entrada.id] ?? []

                  return (
                    <React.Fragment key={entrada.id}>
                      <tr className="hover:bg-gray-50">
                        <td className="px-5 py-3 text-sm text-gray-500 whitespace-nowrap">{formatFecha(entrada.created_at)}</td>
                        <td className="px-5 py-3 text-sm font-medium text-gray-800">{ing?.nombre ?? `#${entrada.ingrediente_id}`}</td>
                        <td className="px-5 py-3 text-sm text-gray-700">{formatValor(Number(entrada.cantidad), unidadMedida)}</td>
                        <td className="px-5 py-3 text-sm">
                          {yaCorregidoBase > 0 ? (
                            <span className="text-orange-600 font-medium">−{formatValor(yaCorregidoBase, unidadMedida)}</span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-5 py-3 text-right">
                          {puedeCorregir && !esCorreccionActiva && (
                            <button
                              onClick={() => abrirCorreccion(entrada)}
                              className="text-xs text-orange-600 border border-orange-200 bg-orange-50 rounded px-3 py-1 hover:bg-orange-100"
                            >
                              Corregir
                            </button>
                          )}
                          {!puedeCorregir && (
                            <span className="text-xs text-gray-400">Corregido</span>
                          )}
                        </td>
                      </tr>

                      {correccionesDeEsta.map((c) => (
                        <tr key={c.id} className="bg-orange-50">
                          <td className="pl-10 pr-5 py-2 text-xs text-gray-400">{formatFecha(c.created_at)}</td>
                          <td className="px-5 py-2 text-xs text-gray-500 italic" colSpan={2}>Corrección: {c.observacion}</td>
                          <td className="px-5 py-2 text-xs text-orange-600">−{formatValor(Number(c.cantidad), unidadMedida)}</td>
                          <td />
                        </tr>
                      ))}

                      {esCorreccionActiva && correccion && (
                        <tr className="bg-orange-50 border-l-4 border-orange-400">
                          <td colSpan={5} className="px-5 py-4">
                            <p className="text-xs font-medium text-gray-700 mb-2">
                              Máximo a corregir: <span className="text-orange-700">{formatValor(disponibleBase, unidadMedida)}</span>
                            </p>
                            <div className="flex flex-wrap items-end gap-3">
                              <div>
                                <label className="text-xs text-gray-500 block mb-1">Cantidad a quitar</label>
                                <div className="flex items-center gap-2">
                                  <input
                                    type="number"
                                    min="0.001"
                                    step="any"
                                    value={correccion.cantidad}
                                    onChange={(e) => setCorreccion({ ...correccion, cantidad: e.target.value, error: '' })}
                                    placeholder="Cantidad"
                                    className="w-28 rounded border border-orange-300 px-3 py-1.5 text-sm [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                    autoFocus
                                  />
                                  <span className="text-sm text-gray-600 font-medium">{UNIDADES_COMPRA[correccion.unidadMedida]}</span>
                                </div>
                              </div>
                              <div className="flex-1 min-w-48">
                                <label className="text-xs text-gray-500 block mb-1">Motivo (obligatorio)</label>
                                <input
                                  type="text"
                                  value={correccion.motivo}
                                  onChange={(e) => setCorreccion({ ...correccion, motivo: e.target.value, error: '' })}
                                  placeholder="Ej: cargué de más por error"
                                  className="w-full rounded border border-orange-300 px-3 py-1.5 text-sm"
                                />
                              </div>
                              <div className="flex gap-2">
                                <button
                                  onClick={confirmarCorreccion}
                                  disabled={corregirMutation.isPending}
                                  className="rounded bg-orange-600 text-white text-sm px-4 py-1.5 hover:bg-orange-700 disabled:opacity-50"
                                >
                                  {corregirMutation.isPending ? 'Guardando...' : 'Confirmar'}
                                </button>
                                <button
                                  onClick={() => setCorreccion(null)}
                                  disabled={corregirMutation.isPending}
                                  className="rounded border border-gray-300 text-gray-600 text-sm px-4 py-1.5 hover:bg-gray-50 disabled:opacity-50"
                                >
                                  Cancelar
                                </button>
                              </div>
                            </div>
                            {correccion.error && <p className="text-xs text-red-600 mt-2">{correccion.error}</p>}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  )
                })}
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
