"""Pruebas automáticas del modelo. Ejecutar desde la raíz: python -m unittest -v"""
import unittest
from datetime import date, datetime
from decimal import Decimal

from oti.modelos import (
    Curso,
    Docente,
    EscuelaProfesional,
    Estudiante,
    EstadoPeriodo,
    PeriodoAcademico,
    Persona,
    PlanEstudio,
    RegistroNombrado,
    Seccion,
)


def hacer_curso(**cambios):
    datos = dict(
        codigo="IS-282", nombre="Programación Orientada a Objetos", creditos="4.5",
        horas_teoricas=2, horas_practicas=4, horas_seminario=0, horas_virtuales=1,
    )
    datos.update(cambios)
    return Curso(**datos)


def hacer_plan(**cambios):
    datos = dict(nombre="Plan 2018", anio=2018, obligatorios=180, electivos=20,
                 extracurriculares=4, vigente=1)
    datos.update(cambios)
    return PlanEstudio(**datos)


def hacer_escuela(**cambios):
    datos = dict(codigo="IS", nombre="Ingeniería de Sistemas",
                 informacion_general="Escuela de la Facultad de Ingeniería",
                 perfil_egresado="Diseña y desarrolla sistemas de información",
                 codigo_director="D-001", codigo_secretario="D-002")
    datos.update(cambios)
    return EscuelaProfesional(**datos)


def hacer_periodo(**cambios):
    datos = dict(
        nombre="2026-II", numero=2, anio=2026,
        fecha_inicio=date(2026, 8, 24), fecha_fin=date(2026, 12, 18),
        matricula_inicio=date(2026, 8, 10), matricula_fin=date(2026, 8, 21),
        es_verano=0, nota_minima=10.5, estado=2,
    )
    datos.update(cambios)
    return PeriodoAcademico(**datos)


def hacer_seccion(vacantes=2, matriculados=0):
    seccion = Seccion("S-A", "IS-282", "2026-II", vacantes)
    for _ in range(matriculados):
        seccion.matricular()
    return seccion


class PruebaBase(unittest.TestCase):
    def rechaza(self, funcion, *args, error=ValueError, **kwargs):
        with self.assertRaises(error):
            funcion(*args, **kwargs)


class TestCurso(PruebaBase):
    def test_nombre_vacio_o_solo_espacios(self):
        for nombre in ("", "   ", None, 5):
            with self.subTest(nombre=nombre):
                self.rechaza(hacer_curso, nombre=nombre)

    def test_nombre_hasta_200_caracteres(self):
        self.assertEqual(len(hacer_curso(nombre="A" * 200).nombre), 200)
        self.rechaza(hacer_curso, nombre="A" * 201)

    def test_creditos_validos(self):
        for valor in ("3", "3.25", 4, 2.5, Decimal("1.5"), "3.250"):
            with self.subTest(valor=valor):
                self.assertGreater(hacer_curso(creditos=valor).creditos, 0)

    def test_creditos_invalidos_lanzan_value_error(self):
        for valor in (0, -1, "3.255", "abc", None, True, float("nan"), "NaN", "Infinity", []):
            with self.subTest(valor=valor):
                self.rechaza(hacer_curso, creditos=valor)

    def test_creditos_se_entregan_como_decimal(self):
        self.assertIsInstance(hacer_curso(creditos=2.5).creditos, Decimal)

    def test_horas_validas_en_los_extremos(self):
        curso = hacer_curso(horas_teoricas=0, horas_virtuales=255)
        self.assertEqual((curso.horas_teoricas, curso.horas_virtuales), (0, 255))

    def test_horas_invalidas(self):
        for campo in ("horas_teoricas", "horas_practicas", "horas_seminario", "horas_virtuales"):
            for valor in (-1, 256, 1.5, "3", True, None):
                with self.subTest(campo=campo, valor=valor):
                    self.rechaza(hacer_curso, **{campo: valor})

    def test_codigo_vacio(self):
        self.rechaza(hacer_curso, codigo="")

    def test_id_autogenerado_y_de_solo_lectura(self):
        a, b = hacer_curso(), hacer_curso()
        self.assertLess(a.id, b.id)
        self.rechaza(setattr, a, "id", 99, error=AttributeError)

    def test_codigo_de_solo_lectura(self):
        self.rechaza(setattr, hacer_curso(), "codigo", "X", error=AttributeError)

    def test_curso_invalido_no_gasta_id(self):
        antes = hacer_curso().id
        self.rechaza(hacer_curso, creditos=0)
        self.assertEqual(hacer_curso().id, antes + 1)

    def test_horas_totales_se_calcula(self):
        curso = hacer_curso()
        self.assertEqual(curso.horas_totales, 7)
        curso.horas_practicas = 10
        self.assertEqual(curso.horas_totales, 13)
        self.rechaza(setattr, curso, "horas_totales", 1, error=AttributeError)


class TestSeccion(PruebaBase):
    def test_vacantes_deben_ser_enteros_positivos(self):
        for valor in (0, -3, 1.5, "2", True, None):
            with self.subTest(valor=valor):
                self.rechaza(hacer_seccion, vacantes=valor)

    def test_matricular_y_retirar(self):
        seccion = hacer_seccion(vacantes=2)
        seccion.matricular()
        self.assertEqual((seccion.matriculados, seccion.vacantes_disponibles), (1, 1))
        seccion.retirar()
        self.assertEqual(seccion.matriculados, 0)

    def test_seccion_llena_rechaza_matricula(self):
        self.rechaza(hacer_seccion(vacantes=1, matriculados=1).matricular)

    def test_retirar_sin_matriculados(self):
        self.rechaza(hacer_seccion().retirar)

    def test_matriculados_no_se_escribe_directo(self):
        self.rechaza(setattr, hacer_seccion(), "matriculados", 0, error=AttributeError)
        self.rechaza(setattr, hacer_seccion(), "vacantes_disponibles", 5, error=AttributeError)

    def test_no_reducir_vacantes_por_debajo_de_matriculados(self):
        seccion = hacer_seccion(vacantes=5, matriculados=2)
        seccion.vacantes = 2
        self.assertEqual(seccion.vacantes, 2)
        self.rechaza(setattr, seccion, "vacantes", 1)
        self.assertEqual(seccion.vacantes, 2)

    def test_codigos_vacios(self):
        for args in (("", "C", "P", 1), ("S", "", "P", 1), ("S", "C", "", 1)):
            with self.subTest(args=args):
                self.rechaza(Seccion, *args)


class TestPlanEstudio(PruebaBase):
    def test_nombre_hasta_36(self):
        hacer_plan(nombre="A" * 36)
        self.rechaza(hacer_plan, nombre="A" * 37)

    def test_creditos_no_negativos(self):
        for campo in ("obligatorios", "electivos", "extracurriculares"):
            with self.subTest(campo=campo):
                hacer_plan(**{campo: 0})
                self.rechaza(hacer_plan, **{campo: -1})
                self.rechaza(hacer_plan, **{campo: True})

    def test_total_se_calcula_y_no_se_edita(self):
        plan = hacer_plan()
        self.assertEqual(plan.creditos_totales, 204)
        plan.creditos_electivos = 30
        self.assertEqual(plan.creditos_totales, 214)
        self.rechaza(setattr, plan, "creditos_totales", 1, error=AttributeError)

    def test_vigente_se_guarda_como_0_o_1_y_se_entrega_como_bool(self):
        plan = hacer_plan(vigente=1)
        self.assertIs(plan.vigente, True)
        self.assertEqual(plan._vigente, 1)
        plan.vigente = False
        self.assertIs(plan.vigente, False)
        self.assertEqual(plan._vigente, 0)

    def test_vigente_invalido(self):
        for valor in (5, -1, 1.0, "1", None):
            with self.subTest(valor=valor):
                self.rechaza(hacer_plan, vigente=valor)

    def test_anio_fuera_de_rango(self):
        for valor in (1899, 2101, "2018", 2018.0, True):
            with self.subTest(valor=valor):
                self.rechaza(hacer_plan, anio=valor)


class TestEscuela(PruebaBase):
    def test_nombre(self):
        hacer_escuela(nombre="A" * 100)
        self.rechaza(hacer_escuela, nombre="A" * 101)
        self.rechaza(hacer_escuela, nombre="")

    def test_codigos_obligatorios(self):
        for campo in ("codigo", "codigo_director", "codigo_secretario"):
            with self.subTest(campo=campo):
                self.rechaza(hacer_escuela, **{campo: ""})

    def test_textos_deben_ser_texto(self):
        self.rechaza(hacer_escuela, informacion_general=None)
        self.rechaza(hacer_escuela, perfil_egresado=5)


class TestPeriodo(PruebaBase):
    def test_nombre_hasta_45(self):
        hacer_periodo(nombre="A" * 45)
        self.rechaza(hacer_periodo, nombre="A" * 46)

    def test_fin_no_anterior_a_inicio(self):
        self.rechaza(hacer_periodo, fecha_inicio=date(2026, 12, 18), fecha_fin=date(2026, 8, 24))
        self.rechaza(hacer_periodo, matricula_inicio=date(2026, 8, 21), matricula_fin=date(2026, 8, 10))

    def test_fechas_iguales_son_validas(self):
        hacer_periodo(fecha_inicio=date(2026, 9, 1), fecha_fin=date(2026, 9, 1))

    def test_fechas_deben_ser_date(self):
        for valor in ("2026-08-24", datetime(2026, 8, 24), 20260824, None):
            with self.subTest(valor=valor):
                self.rechaza(hacer_periodo, fecha_inicio=valor)

    def test_cambiar_fechas_es_atomico(self):
        periodo = hacer_periodo()
        inicio, fin = periodo.fecha_inicio, periodo.fecha_fin
        periodo.cambiar_fechas(date(2026, 9, 1), date(2026, 12, 20))
        self.assertEqual((periodo.fecha_inicio, periodo.fecha_fin), (date(2026, 9, 1), date(2026, 12, 20)))
        self.rechaza(periodo.cambiar_fechas, date(2026, 12, 31), date(2026, 1, 1))
        self.rechaza(periodo.cambiar_fechas, date(2026, 10, 1), "2026-12-01")
        self.assertEqual((periodo.fecha_inicio, periodo.fecha_fin), (date(2026, 9, 1), date(2026, 12, 20)))
        self.assertNotEqual((inicio, fin), (periodo.fecha_inicio, periodo.fecha_fin))

    def test_fechas_de_solo_lectura(self):
        self.rechaza(setattr, hacer_periodo(), "fecha_inicio", date.today(), error=AttributeError)

    def test_nota_minima(self):
        for valor in (0, 10.5, 20):
            self.assertEqual(hacer_periodo(nota_minima=valor).nota_minima, float(valor))
        for valor in (-0.1, 20.1, "10", None, True, float("nan")):
            with self.subTest(valor=valor):
                self.rechaza(hacer_periodo, nota_minima=valor)

    def test_es_verano_0_1_y_bool(self):
        self.assertIs(hacer_periodo(es_verano=1).es_verano, True)
        self.assertIs(hacer_periodo(es_verano=False).es_verano, False)
        for valor in (2, -1, 1.0, "1", None):
            with self.subTest(valor=valor):
                self.rechaza(hacer_periodo, es_verano=valor)

    def test_estado_valido_se_entrega_como_enum(self):
        self.assertIs(hacer_periodo(estado=2).estado, EstadoPeriodo.EN_CURSO)
        self.assertIs(hacer_periodo(estado=EstadoPeriodo.FINALIZADO).estado, EstadoPeriodo.FINALIZADO)

    def test_estado_invalido(self):
        for valor in (0, 5, 7, True, "2", None, 2.0):
            with self.subTest(valor=valor):
                self.rechaza(hacer_periodo, estado=valor)

    def test_numero_y_anio(self):
        self.rechaza(hacer_periodo, numero=0)
        self.rechaza(hacer_periodo, anio=1800)


class TestPersonas(PruebaBase):
    def test_persona_es_abstracta(self):
        self.rechaza(Persona, "12345678", "Ana", "Quispe", error=TypeError)

    def test_dni(self):
        for valor in ("1234567", "123456789", "ABCDEFGH", "1234 678", 12345678, None, "１２３４５６７８"):
            with self.subTest(valor=valor):
                self.rechaza(Estudiante, valor, "Ana", "Quispe", "27", "IS")

    def test_nombres_y_apellidos_obligatorios(self):
        self.rechaza(Docente, "12345678", "", "Mendoza", "D1")
        self.rechaza(Docente, "12345678", "Luis", " ", "D1")

    def test_nombre_completo_y_rol(self):
        estudiante = Estudiante("12345678", "Ana", "Quispe Rojas", "27123456", "IS")
        docente = Docente("87654321", "Luis", "Mendoza Paz", "DOC-77")
        self.assertEqual(estudiante.nombre_completo, "Ana Quispe Rojas")
        self.assertEqual((estudiante.rol(), docente.rol()), ("Estudiante", "Docente"))
        self.rechaza(setattr, estudiante, "nombre_completo", "X", error=AttributeError)

    def test_codigos_obligatorios(self):
        self.rechaza(Estudiante, "12345678", "Ana", "Q", "", "IS")
        self.rechaza(Estudiante, "12345678", "Ana", "Q", "27", "")
        self.rechaza(Docente, "12345678", "Luis", "M", "")


class TestAbstraccionYPolimorfismo(PruebaBase):
    def test_registro_nombrado_es_abstracto(self):
        self.rechaza(RegistroNombrado, "x", error=TypeError)

    def test_todos_los_registros_dan_resumen_sin_isinstance(self):
        registros = [hacer_curso(), hacer_plan(), hacer_escuela(), hacer_periodo()]
        for registro in registros:
            with self.subTest(registro=type(registro).__name__):
                self.assertIsInstance(registro, RegistroNombrado)
                self.assertTrue(registro.resumen())
                self.assertIn(type(registro).__name__, repr(registro))

    def test_cada_clase_tiene_su_longitud_maxima(self):
        esperado = {Curso: 200, PlanEstudio: 36, EscuelaProfesional: 100, PeriodoAcademico: 45}
        objetos = {Curso: hacer_curso(), PlanEstudio: hacer_plan(),
                   EscuelaProfesional: hacer_escuela(), PeriodoAcademico: hacer_periodo()}
        for clase, maximo in esperado.items():
            self.assertEqual(objetos[clase].longitud_maxima, maximo)


if __name__ == "__main__":
    unittest.main()
