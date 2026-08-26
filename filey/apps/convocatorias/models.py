"""
Convocatorias — contenido de una feria (`FER`, capa por feria).

Esta app vive **dentro del schema de cada feria** (`ADR-0003`). Es la
otra mitad de `FER`: ``apps/ferias`` registra qué ediciones existen,
esto es lo que pasa dentro de una.

.. note:: Ninguna tabla de aquí lleva ``feria_id``, y no es un olvido

   La feria no es una columna: es el schema en el que la conexión está
   mirando. Una consulta desde ``/f/2028/`` no puede alcanzar estas
   filas porque no están en su ``search_path``. Es la garantía que
   compra ADR-0003, y añadir un ``feria_id`` la desharía.
"""

from django.db import models


class TipoConvocatoria(models.TextChoices):
    """A qué módulo pertenece lo que se convoca.

    ``TAL`` no está, y está pendiente a propósito: falta decidir si es
    un cuarto tipo o una convocatoria ``EVT`` con otro público (ver
    `FER/Modelo de datos - Ferias` §6).
    """

    EVT = "EVT", "Eventos"
    STD = "STD", "Venta de stands"
    VIS = "VIS", "Visitas escolares"


class Convocatoria(models.Model):
    """Un llamado abierto dentro de una feria.

    Puede haber **varias del mismo tipo** en la misma feria (decisión
    del 2026-08-25): dos convocatorias de stands con precios distintos
    son un caso real. Por eso ``nombre`` es lo que distingue una de
    otra a ojos del participante, que nunca ve el ``tipo``.
    """

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        ABIERTA = "abierta", "Abierta"
        CERRADA = "cerrada", "Cerrada"

    tipo = models.CharField(max_length=3, choices=TipoConvocatoria.choices)
    nombre = models.CharField(
        max_length=160,
        help_text="Lo que ve el participante. Con dos del mismo tipo, es lo único que las distingue.",
    )
    # `estado` es lo que abre la puerta, no las fechas: adelantar la
    # fecha de cierre NO cierra la convocatoria (CU-FER-008).
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.BORRADOR
    )
    fecha_apertura = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "convocatoria"
        verbose_name_plural = "convocatorias"
        ordering = ["tipo", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
