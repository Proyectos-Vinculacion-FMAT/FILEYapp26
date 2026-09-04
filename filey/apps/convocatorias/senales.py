"""
Lo que `FER` anuncia y los verticales escuchan.

Es la misma inversión de dependencia que el registro de módulos
(`ADR-0006`), por el mismo motivo y con otra herramienta: **esta app no
puede nombrar a ningún vertical**. Escribir aquí
``from apps.eventos... import`` invertiría la dirección de la regla 4 y,
de paso, reventaría el catálogo en cualquier despliegue donde `eventos`
no esté instalado.

Con una señal, `convocatorias` dice qué pasó y no sabe quién escucha; cada
vertical se conecta desde su ``AppConfig.ready()``, igual que se inscribe
en el registro de módulos.

.. note:: Señal y no un campo más de `Modulo`

   El contrato de `Modulo` es deliberadamente corto: **cada campo que se
   le añada lo tienen que llenar los seis módulos**. Esto lo necesita
   uno solo, y un módulo que no escuche no tiene que declarar nada.
"""

from django.dispatch import Signal

#: Alguien abrió el catálogo de una feria.
#:
#: Para un vertical, eso significa que **salió de sus pantallas**: el
#: catálogo es la portada de la feria y el sitio al que se vuelve cuando
#: se abandona lo que se estaba haciendo. `EVT` lo usa para descartar los
#: adjuntos que quedaran a medio subir (`CU-EVT-002`).
#:
#: Argumentos: ``peticion`` y ``persona`` —que puede ser anónima, porque
#: el catálogo no pide sesión (`CU-FER-006` A1)—.
se_abrio_el_catalogo = Signal()
