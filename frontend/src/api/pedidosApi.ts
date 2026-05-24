import axiosClient from './axiosClient'
import { Pedido } from '@models/index'

export interface ItemCarritoInput {
  producto_id: number
  cantidad: number
}

export interface PedidoCreateInput {
  direccion_entrega_id: number
  forma_pago_id: number
  items: ItemCarritoInput[]
  notas?: string
}

export interface PedidoFiltros {
  estado?: string
  page?: number
  size?: number
}

export const pedidosApi = {
  createPedido: async (data: PedidoCreateInput): Promise<Pedido> => {
    const response = await axiosClient.post<Pedido>('/pedidos/', data)
    return response.data
  },

  getPedidos: async (params?: PedidoFiltros): Promise<Pedido[]> => {
    const response = await axiosClient.get<Pedido[]>('/pedidos/', { params })
    return response.data
  },

  getPedidoById: async (id: number): Promise<Pedido> => {
    const response = await axiosClient.get<Pedido>(`/pedidos/${id}`)
    return response.data
  },

  avanzarEstado: async (id: number, observacion?: string): Promise<Pedido> => {
    const response = await axiosClient.patch<Pedido>(`/pedidos/${id}/estado`, { observacion })
    return response.data
  },

  cancelarPedido: async (id: number, observacion?: string): Promise<Pedido> => {
    const response = await axiosClient.patch<Pedido>(`/pedidos/${id}/cancelar`, { observacion })
    return response.data
  },
}
