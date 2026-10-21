"""Funciones de validación reutilizables del sistema académico.

Todas devuelven el valor ya validado y, si el dato no sirve, lanzan siempre
``ValueError`` con un mensaje que empieza por la etiqueta del campo. Así el
resto del sistema solo necesita capturar un tipo de excepción.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def texto(valor: object, etiqueta: str) -> str:
    """Exige un ``str`` (puede estar vacío)."""
    if not isinstance(valor, str):
        raise ValueError(f"{etiqueta}: debe ser texto")
    return valor


def texto_no_vacio(valor: object, etiqueta: str, maximo: int | None = None) -> str:
    """Exige un ``str`` con contenido y, si se indica, de longitud <= ``maximo``."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{etiqueta}: no puede estar vacío")
    if maximo is not None and len(valor) > maximo:
        raise ValueError(f"{etiqueta}: no puede pasar de {maximo} caracteres")
    return valor


def entero_en_rango(valor: object, minimo: int, maximo: int, etiqueta: str) -> int:
    """Exige un ``int`` entre ``minimo`` y ``maximo``. ``True``/``False`` no valen."""
    if isinstance(valor, bool) or not isinstance(valor, int) or not minimo <= valor <= maximo:
        raise ValueError(f"{etiqueta}: se esperaba un entero entre {minimo} y {maximo}")
    return valor


def entero_minimo(valor: object, minimo: int, etiqueta: str) -> int:
    """Exige un ``int`` mayor o igual que ``minimo``. ``True``/``False`` no valen."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ValueError(f"{etiqueta}: se esperaba un entero mayor o igual que {minimo}")
    return valor


def decimal_positivo(valor: object, etiqueta: str, decimales: int = 2) -> Decimal:
    """Convierte a ``Decimal`` un número > 0 con a lo más ``decimales`` decimales."""
    mensaje = f"{etiqueta}: debe ser un número mayor que 0 con máximo {decimales} decimales"
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise ValueError(mensaje)
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(mensaje) from None
    if not numero.is_finite() or numero <= 0:
        raise ValueError(mensaje)
    if numero.normalize().as_tuple().exponent < -decimales:
        raise ValueError(mensaje)
    return numero


def numero_en_rango(valor: object, minimo: float, maximo: float, etiqueta: str) -> float:
    """Exige un ``int`` o ``float`` entre ``minimo`` y ``maximo`` (acepta decimales)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not minimo <= valor <= maximo:
        raise ValueError(f"{etiqueta}: se esperaba un número entre {minimo} y {maximo}")
    return float(valor)


def bit(valor: object, etiqueta: str) -> int:
    """Acepta 0, 1, ``True`` o ``False`` y devuelve 0 o 1."""
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, int) and valor in (0, 1):
        return valor
    raise ValueError(f"{etiqueta}: debe ser 0, 1, True o False")


def fecha(valor: object, etiqueta: str) -> date:
    """Exige un ``datetime.date`` (un texto o un ``datetime`` no valen)."""
    if not isinstance(valor, date) or isinstance(valor, datetime):
        raise ValueError(f"{etiqueta}: debe ser una fecha (datetime.date)")
    return valor


def dni(valor: object) -> str:
    """Exige un DNI de 8 dígitos, como texto."""
    if not isinstance(valor, str) or len(valor) != 8 or not (valor.isascii() and valor.isdigit()):
        raise ValueError("DNI: debe ser un texto de 8 dígitos")
    return valor
