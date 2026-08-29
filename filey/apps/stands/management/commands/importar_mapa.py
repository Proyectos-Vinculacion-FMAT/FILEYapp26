"""
Carga el showfloor de una convocatoria desde un JSON (`CU-STD-039`).

La vía habitual será el admin de la edición. Este comando existe por la
regla 3 de `CLAUDE.md` —si una regla no se puede llamar sin pasar por
HTTP, está en el lugar equivocado— y porque importar un mapa es una
operación de montaje: se hace una vez por edición, desde una consola, y
conviene poder repetirla en un despliegue sin abrir un navegador.

Uso:
    python manage.py importar_mapa --feria 2026 --convocatoria 3 \\
        --archivo apps/stands/mapas/filey-2026.json [--confirmar]
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria
from apps.ferias.models import Feria
from apps.stands.servicios import mapas


class Command(BaseCommand):
    help = "Importa el mapa del showfloor de una convocatoria (CU-STD-039)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--feria",
            required=True,
            help="Slug de la edición. El mapa vive en su schema (ADR-0003).",
        )
        parser.add_argument(
            "--convocatoria",
            required=True,
            type=int,
            help="Id de la convocatoria de stands destino.",
        )
        parser.add_argument("--archivo", required=True, help="Ruta del JSON.")
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help=(
                "Necesario para reemplazar un mapa que ya existe: borra todos "
                "sus espacios."
            ),
        )

    def handle(self, *args, **opciones):
        ruta = Path(opciones["archivo"])
        if not ruta.exists():
            raise CommandError(f"No existe el archivo {ruta}.")
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"{ruta} no es JSON válido: {exc}") from exc

        feria = Feria.reales.filter(slug=opciones["feria"]).first()
        if feria is None:
            raise CommandError(f"No hay ninguna feria con el slug «{opciones['feria']}».")

        # Todo lo de `STD` vive en el schema de su feria, así que hay que
        # entrar en él a mano: un comando no pasa por el middleware que lo
        # fija en una petición.
        with schema_context(feria.schema_name):
            convocatoria = Convocatoria.objects.filter(
                pk=opciones["convocatoria"]
            ).first()
            if convocatoria is None:
                raise CommandError(
                    f"«{feria.nombre}» no tiene ninguna convocatoria "
                    f"con id {opciones['convocatoria']}."
                )
            try:
                resumen = mapas.importar(
                    convocatoria=convocatoria,
                    datos=datos,
                    confirmado=opciones["confirmar"],
                )
            except mapas.ImportacionRechazada as exc:
                raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"{resumen} — {convocatoria.nombre}"))
