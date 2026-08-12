"""
Utilidades transversales del monolito.

Aquí vive lo que no pertenece a ningún dominio: plomería de HTTP/HTMX
y el limitador de peticiones. `comun` **no importa de ninguna app**, así
que cualquier módulo puede depender de él sin crear ciclos (ver la regla
de dependencias en CLAUDE.md).
"""
