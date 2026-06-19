import { useQuery } from '@tanstack/react-query'
import { formasPagoApi } from '@api/formasPagoApi'

export const useFormasPago = () => {
  return useQuery({
    queryKey: ['formas-pago'],
    queryFn: formasPagoApi.getFormasPago,
    staleTime: 1000 * 60 * 60,
  })
}
