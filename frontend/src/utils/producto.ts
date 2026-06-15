import { Producto, ProductoDetalleConfig } from '@models/index'

export const getProductoImagenPrincipal = (producto: Producto) =>
  producto.imagenes_url?.find(Boolean) || null

export const getCloudinaryProductImageUrl = (url: string | null, transformation = 'f_auto,q_auto,c_fill,w_640,h_360') => {
  if (!url) return null
  const marker = '/upload/'
  const index = url.indexOf(marker)
  if (index === -1) return url
  return `${url.slice(0, index + marker.length)}${transformation}/${url.slice(index + marker.length)}`
}

export const getProductoPrecioBase = (producto: Producto) => Number(producto.precio_venta) || 0

export const getProductoPrecioFinal = (producto: Producto) => {
  if (typeof producto.precio_final === 'number') return producto.precio_final
  const precio = Number(producto.precio_venta) || 0
  const descuento = Number(producto.descuento_porcentaje) || 0
  return Number((precio * (1 - descuento / 100)).toFixed(2))
}

export const getProductoStockDisponible = (producto: Producto) =>
  Math.max(Number(producto.stock_disponible_calculado) || 0, 0)

export const isProductoOperativamenteDisponible = (producto: Producto) =>
  producto.disponible && getProductoStockDisponible(producto) > 0

export const getProductoEtiquetaStock = (producto: Producto) => {
  if (!producto.disponible) return 'No disponible'
  const stock = getProductoStockDisponible(producto)
  return stock > 0 ? `${stock} disponibles` : 'Sin stock'
}

export const calcularCostoProducto = (ingredientes: ProductoDetalleConfig[]) =>
  Number(
    ingredientes
      .reduce((sum, item) => sum + Number(item.ingrediente.costo_unitario) * Number(item.cantidad), 0)
      .toFixed(2),
  )

export const calcularStockMaximoProducto = (ingredientes: ProductoDetalleConfig[]) => {
  if (ingredientes.length === 0) return 0

  const disponibilidades = ingredientes.map((item) => {
    if (item.cantidad <= 0) return 0
    return Math.floor(item.ingrediente.stock_actual / item.cantidad)
  })

  return Math.min(...disponibilidades)
}
