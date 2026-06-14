import axiosClient from './axiosClient'
import { Pago } from '@models/index'

export interface PagoCreateInput {
  pedido_id: number
  token: string
  payment_method_id: string
  installments: number
  issuer_id?: string
  payer_email?: string
}

export const pagosApi = {
  createPago: async (data: PagoCreateInput): Promise<Pago> => {
    const response = await axiosClient.post<Pago>('/pagos/crear', data)
    return response.data
  },

  getPagoByPedidoId: async (pedidoId: number): Promise<Pago> => {
    const response = await axiosClient.get<Pago>(`/pagos/${pedidoId}`)
    return response.data
  },
}
