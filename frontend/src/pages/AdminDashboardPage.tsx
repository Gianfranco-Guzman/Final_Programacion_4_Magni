import React from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { Spinner } from '@components/Spinner'
import {
  useIngresosFormaPagoStats,
  usePedidosPorEstadoStats,
  useProductosTopStats,
  useResumenStats,
  useVentasStats,
} from '@hooks/useEstadisticas'

const COLORS = ['#2563eb', '#16a34a', '#ea580c', '#7c3aed', '#dc2626', '#0891b2']

const money = (value: number) => `$${Number(value ?? 0).toFixed(2)}`

const StatCard = ({ title, value }: { title: string; value: string | number }) => (
  <div className="bg-white rounded-lg shadow-md p-5">
    <p className="text-xs uppercase text-gray-500 tracking-wide">{title}</p>
    <p className="mt-2 text-2xl font-bold text-gray-800">{value}</p>
  </div>
)

export const AdminDashboardPage: React.FC = () => {
  const resumenQuery = useResumenStats()
  const ventasQuery = useVentasStats('day')
  const topQuery = useProductosTopStats(8)
  const estadosQuery = usePedidosPorEstadoStats()
  const ingresosQuery = useIngresosFormaPagoStats()

  const queries = [resumenQuery, ventasQuery, topQuery, estadosQuery, ingresosQuery]
  const isLoading = queries.some((query) => query.isLoading)
  const error = queries.find((query) => query.error)?.error

  if (isLoading) {
    return <div className="py-12"><Spinner /></div>
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error instanceof Error ? error.message : 'Error cargando estadísticas'}</p>
      </div>
    )
  }

  const resumen = resumenQuery.data
  const ventas = ventasQuery.data ?? []
  const topProductos = topQuery.data ?? []
  const pedidosPorEstado = estadosQuery.data ?? []
  const ingresosPorFormaPago = ingresosQuery.data ?? []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Dashboard admin</h1>
        <p className="text-sm text-gray-500 mt-1">Métricas operativas y de ventas del negocio.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Ventas hoy" value={money(resumen?.ventas_hoy ?? 0)} />
        <StatCard title="Ticket promedio" value={money(resumen?.ticket_promedio ?? 0)} />
        <StatCard title="Pedidos activos" value={resumen?.pedidos_activos ?? 0} />
        <StatCard title="Ingresos mes actual" value={money(resumen?.ingresos_mes_actual ?? 0)} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Ventas por período</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={ventas}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="periodo" tickFormatter={(value) => new Date(value).toLocaleDateString('es-AR')} />
                <YAxis />
                <Tooltip
                  formatter={(value: number, name: string) =>
                    name === 'total_ventas' ? money(value) : value
                  }
                  labelFormatter={(value) => new Date(value).toLocaleDateString('es-AR')}
                />
                <Legend />
                <Line type="monotone" dataKey="total_ventas" name="Total ventas" stroke="#2563eb" strokeWidth={2} />
                <Line type="monotone" dataKey="cantidad_pedidos" name="Cantidad pedidos" stroke="#16a34a" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Distribución por estado</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pedidosPorEstado} dataKey="cantidad" nameKey="estado_codigo" outerRadius={110} label>
                  {pedidosPorEstado.map((entry, index) => (
                    <Cell key={entry.estado_codigo} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top productos</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topProductos}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre" tickFormatter={(value) => String(value).slice(0, 12)} />
                <YAxis />
                <Tooltip formatter={(value: number, name: string) => (name === 'ingresos' ? money(value) : value)} />
                <Legend />
                <Bar dataKey="ingresos" name="Ingresos" fill="#7c3aed" />
                <Bar dataKey="cantidad_vendida" name="Cantidad" fill="#0891b2" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Ingresos por forma de pago</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ingresosPorFormaPago} layout="vertical" margin={{ left: 16 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="forma_pago_codigo" width={120} />
                <Tooltip formatter={(value: number, name: string) => (name === 'total' ? money(value) : value)} />
                <Legend />
                <Bar dataKey="total" name="Total" fill="#ea580c" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
