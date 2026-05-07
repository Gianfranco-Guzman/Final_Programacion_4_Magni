import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import { Producto } from '@types/index'

interface ProductosState {
  search: string
  categoriaId: number | null
  disponible: boolean | null
  page: number
  showDeleted: boolean
  editingProducto: Producto | null
}

const initialState: ProductosState = {
  search: '',
  categoriaId: null,
  disponible: null,
  page: 1,
  showDeleted: false,
  editingProducto: null,
}

type Action =
  | { type: 'SET_SEARCH'; payload: string }
  | { type: 'SET_CATEGORIA'; payload: number | null }
  | { type: 'SET_DISPONIBLE'; payload: boolean | null }
  | { type: 'SET_PAGE'; payload: number }
  | { type: 'SET_SHOW_DELETED'; payload: boolean }
  | { type: 'RESET_FILTROS' }
  | { type: 'SET_EDITING'; payload: Producto }
  | { type: 'CLEAR_EDITING' }

function productosReducer(
  state: ProductosState,
  action: Action,
): ProductosState {
  switch (action.type) {
    case 'SET_SEARCH':
      return { ...state, search: action.payload, page: 1 }
    case 'SET_CATEGORIA':
      return { ...state, categoriaId: action.payload, page: 1 }
    case 'SET_DISPONIBLE':
      return { ...state, disponible: action.payload, page: 1 }
    case 'SET_PAGE':
      return { ...state, page: action.payload }
    case 'SET_SHOW_DELETED':
      return { ...state, showDeleted: action.payload, page: 1 }
    case 'RESET_FILTROS':
      return {
        ...initialState,
        editingProducto: state.editingProducto,
      }
    case 'SET_EDITING':
      return { ...state, editingProducto: action.payload }
    case 'CLEAR_EDITING':
      return { ...state, editingProducto: null }
    default:
      return state
  }
}

interface ProductosContextType {
  state: ProductosState
  dispatch: React.Dispatch<Action>
}

const ProductosContext = createContext<ProductosContextType | undefined>(
  undefined,
)

export function ProductosProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(productosReducer, initialState)

  return (
    <ProductosContext.Provider value={{ state, dispatch }}>
      {children}
    </ProductosContext.Provider>
  )
}

export function useProductosContext() {
  const context = useContext(ProductosContext)
  if (!context) {
    throw new Error(
      'useProductosContext must be used within a ProductosProvider',
    )
  }
  return context
}
