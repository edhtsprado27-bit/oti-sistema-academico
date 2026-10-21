"""Programa de prueba del caso OTI: muestra cada regla con un dato válido y uno inválido.

Ejecutar desde la raíz del repositorio:  python demo_reglas.py
Termina con código 1 si alguna regla no se comporta como se espera.
"""
import sys
from datetime import date

from oti.modelos import (
    Curso, Docente, EscuelaProfesional, Estudiante, PeriodoAcademico,
    PlanEstudio, RegistroNombrado, Persona, Seccion,
)

fallos = 0


def probar(regla, valida, invalida, esperado=ValueError):
    """Ejecuta una acción válida (debe aceptarse) y una inválida (debe lanzar ``esperado``)."""
    global fallos
    print(f"\n[{regla}]")
    try:
        valida()
        print("  VÁLIDO   -> aceptado")
    except Exception as e:  # cualquier error en un dato válido es un fallo
        fallos += 1
        print(f"  VÁLIDO   -> FALLO, se rechazó un dato válido: {e!r}")
    try:
        invalida()
        fallos += 1
        print("  INVÁLIDO -> FALLO, se aceptó un dato inválido")
    except esperado as e:
        print(f"  INVÁLIDO -> rechazado ({esperado.__name__}): {e}")


def seccion(vacantes=2, matriculados=0):
    s = Seccion("S-A", "IS-282", "2026-II", vacantes)
    for _ in range(matriculados):
        s.matricular()
    return s


def curso(**c):
    d = dict(codigo="IS-282", nombre="Programación Orientada a Objetos", creditos="4.5",
             horas_teoricas=2, horas_practicas=4, horas_seminario=0, horas_virtuales=1)
    d.update(c)
    return Curso(**d)


def plan(**c):
    d = dict(nombre="Plan 2018", anio=2018, obligatorios=180, electivos=20,
             extracurriculares=4, vigente=1)
    d.update(c)
    return PlanEstudio(**d)


def periodo(**c):
    d = dict(nombre="2026-II", numero=2, anio=2026,
             fecha_inicio=date(2026, 8, 24), fecha_fin=date(2026, 12, 18),
             matricula_inicio=date(2026, 8, 10), matricula_fin=date(2026, 8, 21),
             es_verano=0, nota_minima=10.5, estado=2)
    d.update(c)
    return PeriodoAcademico(**d)


def escuela(**c):
    d = dict(codigo="IS", nombre="Ingeniería de Sistemas",
             informacion_general="Escuela de la Facultad de Ingeniería",
             perfil_egresado="Diseña y desarrolla sistemas de información",
             codigo_director="D-001", codigo_secretario="D-002")
    d.update(c)
    return EscuelaProfesional(**d)


print("=" * 60, "\nCURSO")
probar("Nombre no vacío", lambda: curso(nombre="POO"), lambda: curso(nombre="  "))
probar("Nombre <= 200 caracteres", lambda: curso(nombre="A" * 200), lambda: curso(nombre="A" * 201))
probar("Créditos > 0", lambda: curso(creditos="3"), lambda: curso(creditos=0))
probar("Créditos con máx. 2 decimales", lambda: curso(creditos="3.25"), lambda: curso(creditos="3.255"))
probar("Créditos deben ser un número", lambda: curso(creditos=4), lambda: curso(creditos="abc"))
probar("Horas entre 0 y 255", lambda: curso(horas_teoricas=255), lambda: curso(horas_teoricas=256))
probar("Horas no negativas", lambda: curso(horas_virtuales=0), lambda: curso(horas_virtuales=-1))
probar("Horas no aceptan True", lambda: curso(horas_practicas=1), lambda: curso(horas_practicas=True))
probar("Identificador no modificable", lambda: curso().id, lambda: setattr(curso(), "id", 99), AttributeError)
probar("Código no modificable", lambda: curso().codigo, lambda: setattr(curso(), "codigo", "X"), AttributeError)
c = curso()
print(f"\n[Horas totales calculadas] 2+4+0+1 = {c.horas_totales}")
c.horas_practicas = 10
print(f"  Tras corregir las prácticas a 10, el total se actualiza solo: {c.horas_totales}")
probar("Horas totales no se asigna", lambda: c.horas_totales, lambda: setattr(c, "horas_totales", 50), AttributeError)

print("\n" + "=" * 60, "\nSECCIÓN")
probar("Vacantes > 0", lambda: seccion(vacantes=2), lambda: seccion(vacantes=0))
probar("Matricular con cupo", lambda: seccion(2, 1).matricular(), lambda: seccion(1, 1).matricular())
probar("Retirar con matriculados", lambda: seccion(2, 1).retirar(), lambda: seccion(2, 0).retirar())
probar("Matriculados no se escribe directo", lambda: seccion().matriculados,
       lambda: setattr(seccion(), "matriculados", 0), AttributeError)
probar("No reducir vacantes bajo los matriculados", lambda: setattr(seccion(5, 2), "vacantes", 3),
       lambda: setattr(seccion(5, 2), "vacantes", 1))
s = seccion(3, 1)
print(f"\n[Vacantes disponibles calculadas] 3 - 1 = {s.vacantes_disponibles}")

print("\n" + "=" * 60, "\nPLAN DE ESTUDIO")
probar("Nombre <= 36 caracteres", lambda: plan(nombre="A" * 36), lambda: plan(nombre="A" * 37))
probar("Créditos no negativos", lambda: plan(electivos=0), lambda: plan(electivos=-1))
p = plan()
print(f"\n[Total calculado] 180+20+4 = {p.creditos_totales}")
probar("Total de créditos no editable", lambda: p.creditos_totales,
       lambda: setattr(p, "creditos_totales", 100), AttributeError)
print(f"\n[0/1 interno, bool al consultar] vigente={p.vigente} ({type(p.vigente).__name__}), interno={p._vigente}")
probar("Vigente solo 0 o 1", lambda: plan(vigente=0), lambda: plan(vigente=5))

print("\n" + "=" * 60, "\nPERIODO ACADÉMICO")
probar("Nombre <= 45 caracteres", lambda: periodo(nombre="A" * 45), lambda: periodo(nombre="A" * 46))
probar("Fecha fin >= inicio", lambda: periodo(),
       lambda: periodo(fecha_inicio=date(2026, 12, 18), fecha_fin=date(2026, 8, 24)))
probar("Fechas de matrícula: fin >= inicio", lambda: periodo(),
       lambda: periodo(matricula_inicio=date(2026, 8, 21), matricula_fin=date(2026, 8, 10)))
probar("Las fechas deben ser date, no texto", lambda: periodo(),
       lambda: periodo(fecha_inicio="2026-08-24"))
pe = periodo()
probar("Cambiar fechas juntas", lambda: pe.cambiar_fechas(date(2026, 9, 1), date(2026, 12, 20)),
       lambda: pe.cambiar_fechas(date(2026, 12, 20), date(2026, 9, 1)))
print(f"  (las fechas siguen intactas tras el rechazo: {pe.fecha_inicio} a {pe.fecha_fin})")
probar("Nota mínima entre 0 y 20", lambda: periodo(nota_minima=10.5), lambda: periodo(nota_minima=21))
probar("Nota mínima debe ser número", lambda: periodo(nota_minima=11), lambda: periodo(nota_minima="abc"))
probar("Verano solo 0 o 1", lambda: periodo(es_verano=1), lambda: periodo(es_verano=2))
print(f"\n[Verano 0/1 -> bool] es_verano={periodo(es_verano=1).es_verano}")
probar("Estado válido (Enum)", lambda: periodo(estado=3), lambda: periodo(estado=7))
print(f"  estado=2 se entrega como: {periodo().estado}")

print("\n" + "=" * 60, "\nESCUELA PROFESIONAL")
probar("Nombre no vacío y <= 100", lambda: escuela(), lambda: escuela(nombre=""))
probar("Código del director obligatorio", lambda: escuela(), lambda: escuela(codigo_director=""))

print("\n" + "=" * 60, "\nPERSONAS")
probar("DNI de 8 dígitos", lambda: Estudiante("12345678", "Ana", "Quispe", "27123456", "IS"),
       lambda: Estudiante("1234", "Ana", "Quispe", "27123456", "IS"))
probar("Persona no se instancia", lambda: Docente("87654321", "Luis", "Mendoza", "D-1"),
       lambda: Persona("12345678", "Ana", "Quispe"), TypeError)
probar("RegistroNombrado no se instancia", lambda: curso(),
       lambda: RegistroNombrado("x"), TypeError)
est = Estudiante("12345678", "Ana", "Quispe Rojas", "27123456", "IS")
doc = Docente("87654321", "Luis", "Mendoza Paz", "DOC-77")
print(f"\n[Nombre completo calculado] {est.nombre_completo}")

print("\n" + "=" * 60, "\nPOLIMORFISMO (lista mixta, sin isinstance)")
for registro in [curso(), plan(), escuela(), periodo()]:
    print(" ", registro.resumen())
for persona in [est, doc]:
    print(" ", persona.nombre_completo, "->", persona.rol())

print("\n" + "=" * 60)
print("RESULTADO:", "todas las reglas se comportan como se espera" if fallos == 0 else f"{fallos} FALLO(S)")
sys.exit(1 if fallos else 0)
