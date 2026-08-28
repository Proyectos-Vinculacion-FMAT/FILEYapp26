"""
Catálogo de países (ISO 3166-1), en español.

`Persona.pais` guarda el **código de dos letras**, no el nombre: el
nombre de un país cambia (y se escribe de varias formas), el código no.
Así "MX" es siempre el mismo país aunque la etiqueta se traduzca o se
corrija, y un informe puede agrupar sin normalizar cadenas a mano.

La lista vive en un módulo propio, y no dentro de `models.py`, porque no
es lógica de negocio: es un catálogo estable que también consultan los
formularios. Si algún día hace falta filtrar (solo los países con
participación histórica, por ejemplo), se filtra aquí, en un solo sitio.
"""

#: Los que van arriba del desplegable, en este orden: los tres que hacen
#: frontera con México y después los mercados de habla hispana que de
#: hecho mandan expositores a una feria del libro latinoamericana.
#:
#: .. warning:: Es una decisión de usabilidad, no un dato de FILEY
#:
#:    No sale de ningún documento del cliente: es un atajo para que la
#:    mayoría no recorra 197 entradas. Si algún día hay histórico de
#:    participación, esta lista debería salir de ahí y no de una
#:    suposición.
CERCANOS = [
    "US", "GT", "BZ",                                # frontera
    "ES", "CO", "AR", "CL", "PE",                    # los que más mandan
    "CU", "CR", "EC", "SV", "HN", "NI", "PA", "DO",  # el resto de la región
    "BO", "PY", "UY", "VE", "BR",
]

# Orden alfabético en español, con México primero: es de donde viene la
# inmensa mayoría de los participantes y ahorrarles el desplazamiento en
# un desplegable de ~200 entradas es la diferencia entre un campo que se
# llena bien y uno que se llena con lo primero que quede a mano.
PAISES = [
    ("MX", "México"),
    ("AF", "Afganistán"),
    ("AL", "Albania"),
    ("DE", "Alemania"),
    ("AD", "Andorra"),
    ("AO", "Angola"),
    ("AG", "Antigua y Barbuda"),
    ("SA", "Arabia Saudita"),
    ("DZ", "Argelia"),
    ("AR", "Argentina"),
    ("AM", "Armenia"),
    ("AU", "Australia"),
    ("AT", "Austria"),
    ("AZ", "Azerbaiyán"),
    ("BS", "Bahamas"),
    ("BD", "Bangladés"),
    ("BB", "Barbados"),
    ("BH", "Baréin"),
    ("BE", "Bélgica"),
    ("BZ", "Belice"),
    ("BJ", "Benín"),
    ("BY", "Bielorrusia"),
    ("BO", "Bolivia"),
    ("BA", "Bosnia y Herzegovina"),
    ("BW", "Botsuana"),
    ("BR", "Brasil"),
    ("BN", "Brunéi"),
    ("BG", "Bulgaria"),
    ("BF", "Burkina Faso"),
    ("BI", "Burundi"),
    ("BT", "Bután"),
    ("CV", "Cabo Verde"),
    ("KH", "Camboya"),
    ("CM", "Camerún"),
    ("CA", "Canadá"),
    ("QA", "Catar"),
    ("TD", "Chad"),
    ("CL", "Chile"),
    ("CN", "China"),
    ("CY", "Chipre"),
    ("VA", "Ciudad del Vaticano"),
    ("CO", "Colombia"),
    ("KM", "Comoras"),
    ("CG", "Congo"),
    ("CD", "Congo (República Democrática)"),
    ("KP", "Corea del Norte"),
    ("KR", "Corea del Sur"),
    ("CI", "Costa de Marfil"),
    ("CR", "Costa Rica"),
    ("HR", "Croacia"),
    ("CU", "Cuba"),
    ("DK", "Dinamarca"),
    ("DM", "Dominica"),
    ("EC", "Ecuador"),
    ("EG", "Egipto"),
    ("SV", "El Salvador"),
    ("AE", "Emiratos Árabes Unidos"),
    ("ER", "Eritrea"),
    ("SK", "Eslovaquia"),
    ("SI", "Eslovenia"),
    ("ES", "España"),
    ("US", "Estados Unidos"),
    ("EE", "Estonia"),
    ("SZ", "Esuatini"),
    ("ET", "Etiopía"),
    ("PH", "Filipinas"),
    ("FI", "Finlandia"),
    ("FJ", "Fiyi"),
    ("FR", "Francia"),
    ("GA", "Gabón"),
    ("GM", "Gambia"),
    ("GE", "Georgia"),
    ("GH", "Ghana"),
    ("GD", "Granada"),
    ("GR", "Grecia"),
    ("GT", "Guatemala"),
    ("GN", "Guinea"),
    ("GQ", "Guinea Ecuatorial"),
    ("GW", "Guinea-Bisáu"),
    ("GY", "Guyana"),
    ("HT", "Haití"),
    ("HN", "Honduras"),
    ("HU", "Hungría"),
    ("IN", "India"),
    ("ID", "Indonesia"),
    ("IQ", "Irak"),
    ("IR", "Irán"),
    ("IE", "Irlanda"),
    ("IS", "Islandia"),
    ("MH", "Islas Marshall"),
    ("SB", "Islas Salomón"),
    ("IL", "Israel"),
    ("IT", "Italia"),
    ("JM", "Jamaica"),
    ("JP", "Japón"),
    ("JO", "Jordania"),
    ("KZ", "Kazajistán"),
    ("KE", "Kenia"),
    ("KG", "Kirguistán"),
    ("KI", "Kiribati"),
    ("KW", "Kuwait"),
    ("LA", "Laos"),
    ("LS", "Lesoto"),
    ("LV", "Letonia"),
    ("LB", "Líbano"),
    ("LR", "Liberia"),
    ("LY", "Libia"),
    ("LI", "Liechtenstein"),
    ("LT", "Lituania"),
    ("LU", "Luxemburgo"),
    ("MK", "Macedonia del Norte"),
    ("MG", "Madagascar"),
    ("MY", "Malasia"),
    ("MW", "Malaui"),
    ("MV", "Maldivas"),
    ("ML", "Malí"),
    ("MT", "Malta"),
    ("MA", "Marruecos"),
    ("MU", "Mauricio"),
    ("MR", "Mauritania"),
    ("FM", "Micronesia"),
    ("MD", "Moldavia"),
    ("MC", "Mónaco"),
    ("MN", "Mongolia"),
    ("ME", "Montenegro"),
    ("MZ", "Mozambique"),
    ("MM", "Myanmar"),
    ("NA", "Namibia"),
    ("NR", "Nauru"),
    ("NP", "Nepal"),
    ("NI", "Nicaragua"),
    ("NE", "Níger"),
    ("NG", "Nigeria"),
    ("NO", "Noruega"),
    ("NZ", "Nueva Zelanda"),
    ("OM", "Omán"),
    ("NL", "Países Bajos"),
    ("PK", "Pakistán"),
    ("PW", "Palaos"),
    ("PS", "Palestina"),
    ("PA", "Panamá"),
    ("PG", "Papúa Nueva Guinea"),
    ("PY", "Paraguay"),
    ("PE", "Perú"),
    ("PL", "Polonia"),
    ("PT", "Portugal"),
    ("PR", "Puerto Rico"),
    ("GB", "Reino Unido"),
    ("CF", "República Centroafricana"),
    ("CZ", "República Checa"),
    ("DO", "República Dominicana"),
    ("RW", "Ruanda"),
    ("RO", "Rumanía"),
    ("RU", "Rusia"),
    ("WS", "Samoa"),
    ("KN", "San Cristóbal y Nieves"),
    ("SM", "San Marino"),
    ("VC", "San Vicente y las Granadinas"),
    ("LC", "Santa Lucía"),
    ("ST", "Santo Tomé y Príncipe"),
    ("SN", "Senegal"),
    ("RS", "Serbia"),
    ("SC", "Seychelles"),
    ("SL", "Sierra Leona"),
    ("SG", "Singapur"),
    ("SY", "Siria"),
    ("SO", "Somalia"),
    ("LK", "Sri Lanka"),
    ("ZA", "Sudáfrica"),
    ("SD", "Sudán"),
    ("SS", "Sudán del Sur"),
    ("SE", "Suecia"),
    ("CH", "Suiza"),
    ("SR", "Surinam"),
    ("TH", "Tailandia"),
    ("TW", "Taiwán"),
    ("TZ", "Tanzania"),
    ("TJ", "Tayikistán"),
    ("TL", "Timor Oriental"),
    ("TG", "Togo"),
    ("TO", "Tonga"),
    ("TT", "Trinidad y Tobago"),
    ("TN", "Túnez"),
    ("TM", "Turkmenistán"),
    ("TR", "Turquía"),
    ("TV", "Tuvalu"),
    ("UA", "Ucrania"),
    ("UG", "Uganda"),
    ("UY", "Uruguay"),
    ("UZ", "Uzbekistán"),
    ("VU", "Vanuatu"),
    ("VE", "Venezuela"),
    ("VN", "Vietnam"),
    ("YE", "Yemen"),
    ("DJ", "Yibuti"),
    ("ZM", "Zambia"),
    ("ZW", "Zimbabue"),
]

PAIS_POR_DEFECTO = "MX"

NOMBRES_POR_CODIGO = dict(PAISES)


def nombre_de(codigo: str) -> str:
    """Etiqueta legible de un código, o el propio código si no está.

    No lanza: un país retirado del catálogo no debe reventar la ficha de
    una persona que se registró cuando sí estaba.
    """
    return NOMBRES_POR_CODIGO.get(codigo or "", codigo or "")


def opciones(preferido: str | None = None) -> list[tuple[str, str]]:
    """El catálogo ordenado para un desplegable, sin repetir ninguno.

    Arriba va el país de quien llena el formulario —si se sabe—, después
    México, después los de `CERCANOS`, y al final el resto en orden
    alfabético. La lógica es la misma que justifica tener México primero
    en `PAISES`, llevada un paso más allá: quien escribe desde Bogotá
    tampoco debería recorrer la lista entera.

    Si `preferido` es México, o no se sabe, no pasa nada raro: no se
    duplica y el orden queda como estaba.

    :param preferido: código ISO de dos letras, o ``None``.
    """
    nombres = dict(PAISES)
    orden = [preferido, "MX", *CERCANOS] if preferido else ["MX", *CERCANOS]

    arriba, vistos = [], set()
    for codigo in orden:
        if codigo in nombres and codigo not in vistos:
            arriba.append((codigo, nombres[codigo]))
            vistos.add(codigo)

    resto = [(c, n) for c, n in PAISES if c not in vistos]
    return arriba + resto
