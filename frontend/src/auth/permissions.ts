export type UserRole = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'

export interface RoleInfo {
  id: number
  nombre: UserRole | string
}

export function hasAnyRole(userRoles: RoleInfo[] | undefined, allowedRoles: readonly string[]): boolean {
  if (!userRoles?.length) return false

  return userRoles.some((role) => allowedRoles.includes(role.nombre))
}
