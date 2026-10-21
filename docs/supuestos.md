# Supuestos y límites del modelo

El caso de la OTI no define algunos datos. Estas son las decisiones tomadas; si el docente indica otra cosa, se cambia en un solo lugar.

| Tema | Decisión | Dónde cambiarla |
|---|---|---|
| Longitud máxima del nombre de una escuela | 100 caracteres | `EscuelaProfesional.longitud_maxima` |
| DNI | Texto de exactamente 8 dígitos (formato peruano) | `validaciones.dni` |
| Año (plan y periodo) | Entero entre 1900 y 2100 | `_ANIO_MIN` y `_ANIO_MAX` en `modelos.py` |
| Número de periodo | Entero mayor o igual que 1 | `PeriodoAcademico.__init__` |
| Códigos (curso, sección, escuela, estudiante, docente) | Texto no vacío; no se valida el formato | `texto_no_vacio` |
| Información general y perfil del egresado | Solo deben ser texto; pueden estar vacíos | `EscuelaProfesional.__init__` |
| Créditos de un curso | `Decimal` mayor que 0 con máximo 2 decimales | `validaciones.decimal_positivo` |
| Nota mínima | Número (con decimales) entre 0 y 20 | `PeriodoAcademico.nota_minima` |
| Fechas | Objetos `datetime.date`; un texto o un `datetime` se rechaza | `validaciones.fecha` |
| Fechas de matrícula | Se valida que el fin no sea anterior al inicio; no se exige que estén dentro del periodo | `cambiar_fechas_matricula` |
| Cambios de estado del periodo | Se acepta cualquier estado válido (1 a 4); no se controla el orden de las transiciones | `PeriodoAcademico.estado` |
| `Curso.id` | Contador en memoria que se reinicia en cada ejecución; en un sistema real lo asignaría la base de datos | `Curso._contador` |
| Persistencia | El modelo no guarda datos en disco ni en una base de datos | Fuera del alcance del caso |
