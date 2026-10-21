# Sistema académico de la OTI

Modelo en Python (POO) para el Caso de OTI: cursos, secciones, planes de estudio, escuelas profesionales, periodos académicos y personas. El sistema impide por código los errores de datos que tenía la base anterior.

## Estructura

```
oti-sistema-academico/
├── oti/
│   ├── __init__.py
│   ├── modelos.py          # clases del sistema
│   └── validaciones.py     # reglas de validación reutilizables
├── pruebas/
│   ├── __init__.py
│   └── test_modelos.py     # pruebas automáticas (unittest)
├── docs/
│   ├── diagrama-clases.md  # diagrama UML (se ve renderizado en GitHub)
│   └── supuestos.md        # supuestos y límites del modelo
├── demo_reglas.py          # programa de prueba: regla válida e inválida, con try/except
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

Python 3.10 o superior. Solo usa la biblioteca estándar, no hay nada que instalar.

## Cómo ejecutar

Desde la carpeta raíz del repositorio:

```bash
python -m unittest -v      # pruebas automáticas: fallan de verdad si una regla se rompe
python demo_reglas.py      # demostración legible de cada regla
```

En Windows, si `python` no se reconoce, usa `py` en su lugar.

## Diseño

- **Abstracción:** `RegistroNombrado` (Curso, PlanEstudio, EscuelaProfesional, PeriodoAcademico) y `Persona` (Estudiante, Docente) son clases abstractas y no se pueden instanciar.
- **Herencia:** cada frase "X es un Y" se cumple. `Seccion` no hereda de `RegistroNombrado` porque el caso no le pide un nombre.
- **Encapsulamiento:** atributos privados con propiedades. Solo llevan setter los datos con una regla de validación; los que no deben cambiar son de solo lectura.
- **Datos calculados (no se guardan):** `horas_totales`, `creditos_totales`, `vacantes_disponibles`, `nombre_completo`.
- **Sin modificación directa:** `Curso.id`, `Curso.codigo` y `Seccion.matriculados` (este solo cambia con `matricular()` y `retirar()`).
- **Tipo guardado distinto del entregado:** `vigente` y `es_verano` se guardan como 0/1 y se entregan como `bool`.
- **Estado del periodo:** `EstadoPeriodo` es un `Enum`; un valor como 7 se rechaza.
- **Validación uniforme:** toda validación lanza `ValueError` con un mensaje claro, y `True`/`False` no se aceptan como números.
- **Polimorfismo:** una lista mixta se recorre con `resumen()` y `rol()`, sin `isinstance`.
- **Referencias entre registros:** se guarda solo el código como texto.

Los supuestos que el caso no define (por ejemplo, la longitud máxima del nombre de una escuela) están en [docs/supuestos.md](docs/supuestos.md), y el diagrama de clases en [docs/diagrama-clases.md](docs/diagrama-clases.md).

## Autores

Edhts Yhurdin Prado Gomez, Angel Omar Huamani Gutiérrez, Nolberto german vasquez carhuas
Ingeniería de Sistemas, UNSCH.
