import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { pedidosApi, PedidoCreateInput } from '@api/pedidosApi'
import { useCartStore } from '@store/cartStore'

export const useCheckout = () => {
  const qc = useQueryClient()
  const clearCart = useCartStore((state) => state.clearCart)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: PedidoCreateInput) => pedidosApi.createPedido(data),
    onSuccess: (pedido) => {
      qc.invalidateQueries({ queryKey: ['pedidos'] })
      clearCart()
      navigate(`/pedidos/${pedido.id}`)
    },
  })
}
