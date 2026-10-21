"""Modelo de clases del sistema académico de la OTI.

Convenciones: atributos privados con guion bajo (``_nombre``) y acceso mediante
propiedades. Una propiedad lleva setter solo si el dato tiene una regla de
validación; los datos que no deben cambiar son de solo lectura y los que se
pueden deducir de otros se calculan en lugar de guardarse.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from enum import Enum
from itertools import count

from .validaciones import (
    bit,
    decimal_positivo,
    entero_en_rango,
    entero_minimo,
    fecha,
    numero_en_rango,
    texto,
    texto_no_vacio,
)
from .validaciones import dni as validar_dni

_ANIO_MIN, _ANIO_MAX = 1900, 2100


class EstadoPeriodo(Enum):
    """Estados posibles de un periodo académico (en lugar de números sueltos)."""

    PLANIFICADO = 1
    EN_CURSO = 2
    MATRICULA_CERRADA = 3
    FINALIZADO = 4


# ---------------------------------------------------------------------------
# Registros con nombre
# ---------------------------------------------------------------------------
class RegistroNombrado(ABC):
    """Base abstracta de los registros que tienen un nombre validado.

    Cada subclase define su ``longitud_maxima`` y su ``resumen()``.
    """

    def __init__(self, nombre: str) -> None:
        self.nombre = nombre

    @property
    @abstractmethod
    def longitud_maxima(self) -> int:
        """Cantidad máxima de caracteres que admite el nombre."""

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = texto_no_vacio(valor, "nombre", self.longitud_maxima)

    @abstractmethod
    def resumen(self) -> str:
        """Descripción corta del registro, de una sola línea."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nombre={self._nombre!r})"


class Curso(RegistroNombrado):
    """Curso con créditos y cuatro tipos de horas.

    El ``id`` lo genera el sistema al crear el curso y no se puede cambiar. Este
    contador vive en memoria y se reinicia en cada ejecución; en un sistema real
    lo asignaría la base de datos.
    """

    _contador = count(1)

    def __init__(
        self,
        codigo: str,
        nombre: str,
        creditos: Decimal | int | float | str,
        horas_teoricas: int,
        horas_practicas: int,
        horas_seminario: int,
        horas_virtuales: int,
    ) -> None:
        super().__init__(nombre)
        self._codigo = texto_no_vacio(codigo, "código")
        self.creditos = creditos
        self.horas_teoricas = horas_teoricas
        self.horas_practicas = horas_practicas
        self.horas_seminario = horas_seminario
        self.horas_virtuales = horas_virtuales
        # Se asigna al final: si algún dato es inválido no se gasta un id.
        self._id = next(Curso._contador)

    @property
    def longitud_maxima(self) -> int:
        return 200

    @property
    def id(self) -> int:
        return self._id

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def creditos(self) -> Decimal:
        return self._creditos

    @creditos.setter
    def creditos(self, valor: Decimal | int | float | str) -> None:
        self._creditos = decimal_positivo(valor, "créditos")

    @property
    def horas_teoricas(self) -> int:
        return self._horas_teoricas

    @horas_teoricas.setter
    def horas_teoricas(self, valor: int) -> None:
        self._horas_teoricas = entero_en_rango(valor, 0, 255, "horas teóricas")

    @property
    def horas_practicas(self) -> int:
        return self._horas_practicas

    @horas_practicas.setter
    def horas_practicas(self, valor: int) -> None:
        self._horas_practicas = entero_en_rango(valor, 0, 255, "horas prácticas")

    @property
    def horas_seminario(self) -> int:
        return self._horas_seminario

    @horas_seminario.setter
    def horas_seminario(self, valor: int) -> None:
        self._horas_seminario = entero_en_rango(valor, 0, 255, "horas de seminario")

    @property
    def horas_virtuales(self) -> int:
        return self._horas_virtuales

    @horas_virtuales.setter
    def horas_virtuales(self, valor: int) -> None:
        self._horas_virtuales = entero_en_rango(valor, 0, 255, "horas virtuales")

    @property
    def horas_totales(self) -> int:
        """Suma de las cuatro horas. Se calcula, no se guarda."""
        return (
            self._horas_teoricas
            + self._horas_practicas
            + self._horas_seminario
            + self._horas_virtuales
        )

    def resumen(self) -> str:
        return (
            f"Curso {self._codigo}: {self._nombre} "
            f"({self._creditos} créditos, {self.horas_totales} h)"
        )

    def __repr__(self) -> str:
        return f"Curso(codigo={self._codigo!r}, nombre={self._nombre!r})"


class PlanEstudio(RegistroNombrado):
    """Plan de estudio con créditos obligatorios, electivos y extracurriculares."""

    def __init__(
        self,
        nombre: str,
        anio: int,
        obligatorios: int,
        electivos: int,
        extracurriculares: int,
        vigente: bool | int,
    ) -> None:
        super().__init__(nombre)
        self._anio = entero_en_rango(anio, _ANIO_MIN, _ANIO_MAX, "año")
        self.creditos_obligatorios = obligatorios
        self.creditos_electivos = electivos
        self.creditos_extracurriculares = extracurriculares
        self.vigente = vigente

    @property
    def longitud_maxima(self) -> int:
        return 36

    @property
    def anio(self) -> int:
        return self._anio

    @property
    def creditos_obligatorios(self) -> int:
        return self._creditos_obligatorios

    @creditos_obligatorios.setter
    def creditos_obligatorios(self, valor: int) -> None:
        self._creditos_obligatorios = entero_minimo(valor, 0, "créditos obligatorios")

    @property
    def creditos_electivos(self) -> int:
        return self._creditos_electivos

    @creditos_electivos.setter
    def creditos_electivos(self, valor: int) -> None:
        self._creditos_electivos = entero_minimo(valor, 0, "créditos electivos")

    @property
    def creditos_extracurriculares(self) -> int:
        return self._creditos_extracurriculares

    @creditos_extracurriculares.setter
    def creditos_extracurriculares(self, valor: int) -> None:
        self._creditos_extracurriculares = entero_minimo(
            valor, 0, "créditos extracurriculares"
        )

    @property
    def creditos_totales(self) -> int:
        """Suma de los tres tipos de créditos. Se calcula y no se puede editar."""
        return (
            self._creditos_obligatorios
            + self._creditos_electivos
            + self._creditos_extracurriculares
        )

    @property
    def vigente(self) -> bool:
        """Se guarda como 0 o 1, pero se entrega como verdadero o falso."""
        return bool(self._vigente)

    @vigente.setter
    def vigente(self, valor: bool | int) -> None:
        self._vigente = bit(valor, "vigente")

    def resumen(self) -> str:
        return (
            f"Plan {self._nombre} ({self._anio}): "
            f"{self.creditos_totales} créditos, vigente={self.vigente}"
        )


class EscuelaProfesional(RegistroNombrado):
    """Escuela profesional. El director y el secretario se guardan solo por código."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        informacion_general: str,
        perfil_egresado: str,
        codigo_director: str,
        codigo_secretario: str,
    ) -> None:
        super().__init__(nombre)
        self._codigo = texto_no_vacio(codigo, "código")
        self._informacion_general = texto(informacion_general, "información general")
        self._perfil_egresado = texto(perfil_egresado, "perfil del egresado")
        self._codigo_director = texto_no_vacio(codigo_director, "código del director")
        self._codigo_secretario = texto_no_vacio(codigo_secretario, "código del secretario")

    @property
    def longitud_maxima(self) -> int:
        # Supuesto: el caso no indica el máximo para el nombre de una escuela.
        return 100

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def informacion_general(self) -> str:
        return self._informacion_general

    @property
    def perfil_egresado(self) -> str:
        return self._perfil_egresado

    @property
    def codigo_director(self) -> str:
        return self._codigo_director

    @property
    def codigo_secretario(self) -> str:
        return self._codigo_secretario

    def resumen(self) -> str:
        return (
            f"Escuela {self._codigo}: {self._nombre} "
            f"(director: {self._codigo_director})"
        )

    def __repr__(self) -> str:
        return f"EscuelaProfesional(codigo={self._codigo!r}, nombre={self._nombre!r})"


class PeriodoAcademico(RegistroNombrado):
    """Periodo académico con fechas, nota mínima aprobatoria y estado."""

    def __init__(
        self,
        nombre: str,
        numero: int,
        anio: int,
        fecha_inicio: date,
        fecha_fin: date,
        matricula_inicio: date,
        matricula_fin: date,
        es_verano: bool | int,
        nota_minima: float,
        estado: EstadoPeriodo | int,
    ) -> None:
        super().__init__(nombre)
        self._numero = entero_minimo(numero, 1, "número")
        self._anio = entero_en_rango(anio, _ANIO_MIN, _ANIO_MAX, "año")
        self.cambiar_fechas(fecha_inicio, fecha_fin)
        self.cambiar_fechas_matricula(matricula_inicio, matricula_fin)
        self.es_verano = es_verano
        self.nota_minima = nota_minima
        self.estado = estado

    @property
    def longitud_maxima(self) -> int:
        return 45

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def anio(self) -> int:
        return self._anio

    @property
    def fecha_inicio(self) -> date:
        return self._fecha_inicio

    @property
    def fecha_fin(self) -> date:
        return self._fecha_fin

    @property
    def matricula_inicio(self) -> date:
        return self._matricula_inicio

    @property
    def matricula_fin(self) -> date:
        return self._matricula_fin

    def cambiar_fechas(self, inicio: date, fin: date) -> None:
        """Cambia juntas las fechas del periodo; si alguna falla no cambia ninguna."""
        inicio = fecha(inicio, "fecha de inicio")
        fin = fecha(fin, "fecha de fin")
        if fin < inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la de inicio")
        self._fecha_inicio, self._fecha_fin = inicio, fin

    def cambiar_fechas_matricula(self, inicio: date, fin: date) -> None:
        """Cambia juntas las fechas de matrícula; si alguna falla no cambia ninguna."""
        inicio = fecha(inicio, "inicio de matrícula")
        fin = fecha(fin, "fin de matrícula")
        if fin < inicio:
            raise ValueError("El fin de matrícula no puede ser anterior a su inicio")
        self._matricula_inicio, self._matricula_fin = inicio, fin

    @property
    def es_verano(self) -> bool:
        """Se guarda como 0 o 1, pero se entrega como verdadero o falso."""
        return bool(self._es_verano)

    @es_verano.setter
    def es_verano(self, valor: bool | int) -> None:
        self._es_verano = bit(valor, "es_verano")

    @property
    def nota_minima(self) -> float:
        return self._nota_minima

    @nota_minima.setter
    def nota_minima(self, valor: float) -> None:
        self._nota_minima = numero_en_rango(valor, 0, 20, "nota mínima")

    @property
    def estado(self) -> EstadoPeriodo:
        return self._estado

    @estado.setter
    def estado(self, valor: EstadoPeriodo | int) -> None:
        if isinstance(valor, EstadoPeriodo):
            self._estado = valor
        elif isinstance(valor, int) and not isinstance(valor, bool):
            try:
                self._estado = EstadoPeriodo(valor)
            except ValueError:
                raise ValueError(f"estado: {valor} no es un estado válido (1 a 4)") from None
        else:
            raise ValueError("estado: debe ser un EstadoPeriodo o un entero del 1 al 4")

    def resumen(self) -> str:
        return (
            f"Periodo {self._nombre}: {self._estado.name}, "
            f"nota mínima {self._nota_minima}"
        )


# ---------------------------------------------------------------------------
# Sección (no es un registro nombrado: el caso no le pide nombre)
# ---------------------------------------------------------------------------
class Seccion:
    """Sección de un curso en un periodo, que referencia ambos solo por código."""

    def __init__(
        self, codigo: str, codigo_curso: str, codigo_periodo: str, vacantes: int
    ) -> None:
        self._codigo = texto_no_vacio(codigo, "código de la sección")
        self._codigo_curso = texto_no_vacio(codigo_curso, "código del curso")
        self._codigo_periodo = texto_no_vacio(codigo_periodo, "código del periodo")
        self._matriculados = 0
        self.vacantes = vacantes

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def codigo_curso(self) -> str:
        return self._codigo_curso

    @property
    def codigo_periodo(self) -> str:
        return self._codigo_periodo

    @property
    def vacantes(self) -> int:
        return self._vacantes

    @vacantes.setter
    def vacantes(self, valor: int) -> None:
        valor = entero_minimo(valor, 1, "vacantes")
        if valor < self._matriculados:
            raise ValueError(
                "No se pueden reducir las vacantes por debajo de los matriculados"
            )
        self._vacantes = valor

    @property
    def matriculados(self) -> int:
        """Solo cambia con ``matricular()`` y ``retirar()``."""
        return self._matriculados

    @property
    def vacantes_disponibles(self) -> int:
        """Vacantes menos matriculados. Se calcula, no se guarda."""
        return self._vacantes - self._matriculados

    def matricular(self) -> None:
        if self._matriculados >= self._vacantes:
            raise ValueError("La sección está llena")
        self._matriculados += 1

    def retirar(self) -> None:
        if self._matriculados == 0:
            raise ValueError("No hay estudiantes matriculados")
        self._matriculados -= 1

    def __repr__(self) -> str:
        return (
            f"Seccion(codigo={self._codigo!r}, "
            f"matriculados={self._matriculados}/{self._vacantes})"
        )


# ---------------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------------
class Persona(ABC):
    """Base abstracta: en el sistema nunca se registra a alguien que sea solo persona."""

    def __init__(self, dni: str, nombres: str, apellidos: str) -> None:
        self._dni = validar_dni(dni)
        self._nombres = texto_no_vacio(nombres, "nombres")
        self._apellidos = texto_no_vacio(apellidos, "apellidos")

    @property
    def dni(self) -> str:
        return self._dni

    @property
    def nombres(self) -> str:
        return self._nombres

    @property
    def apellidos(self) -> str:
        return self._apellidos

    @property
    def nombre_completo(self) -> str:
        """Nombres y apellidos juntos. Se calcula, no se guarda."""
        return f"{self._nombres} {self._apellidos}"

    @abstractmethod
    def rol(self) -> str:
        """Rol de la persona en el sistema."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(dni={self._dni!r}, nombre={self.nombre_completo!r})"


class Estudiante(Persona):
    def __init__(
        self,
        dni: str,
        nombres: str,
        apellidos: str,
        codigo_estudiante: str,
        codigo_escuela: str,
    ) -> None:
        super().__init__(dni, nombres, apellidos)
        self._codigo_estudiante = texto_no_vacio(codigo_estudiante, "código de estudiante")
        self._codigo_escuela = texto_no_vacio(codigo_escuela, "código de la escuela")

    @property
    def codigo_estudiante(self) -> str:
        return self._codigo_estudiante

    @property
    def codigo_escuela(self) -> str:
        return self._codigo_escuela

    def rol(self) -> str:
        return "Estudiante"


class Docente(Persona):
    def __init__(
        self, dni: str, nombres: str, apellidos: str, codigo_docente: str
    ) -> None:
        super().__init__(dni, nombres, apellidos)
        self._codigo_docente = texto_no_vacio(codigo_docente, "código de docente")

    @property
    def codigo_docente(self) -> str:
        return self._codigo_docente

    def rol(self) -> str:
        return "Docente"
