import axiosClient from './axiosClient'
import { FormaPago } from '@models/index'

export const formasPagoApi = {
  getFormasPago: async (): Promise<FormaPago[]> => {
    const response = await axiosClient.get<FormaPago[]>('/formas-pago/')
    return response.data
  },

  getFormaPagoById: async (id: number): Promise<FormaPago> => {
    const response = await axiosClient.get<FormaPago>(`/formas-pago/${id}`)
    return response.data
  },
}
