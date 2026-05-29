from enum import Enum


class UnidadMedida(str, Enum):
    UNIDAD = "UNIDAD"
    GRAMO = "GRAMO"
    KILOGRAMO = "KILOGRAMO"
    MILILITRO = "MILILITRO"
    LITRO = "LITRO"


class TipoProducto(str, Enum):
    FABRICADO = "FABRICADO"
    REVENTA = "REVENTA"


class TipoMovimientoIngrediente(str, Enum):
    ALTA_MANUAL = "ALTA_MANUAL"
    AJUSTE_MANUAL = "AJUSTE_MANUAL"
    CONSUMO_PEDIDO = "CONSUMO_PEDIDO"
    REVERSA_CANCELACION = "REVERSA_CANCELACION"
