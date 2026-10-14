from datetime import date
from types import SimpleNamespace

from app.candidatos import services
from app.catalogos.models import (
    Carrera,
    Cargo,
    Habilidad,
    Idioma,
    Institucion,
    NivelEducacional,
    NivelHabilidad,
    NivelIdioma,
)
from app.clientes.models import Empresa


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values

    def __iter__(self):
        return iter(self._values)


class _FakeDb:
    def __init__(self, *, instituciones=None, carreras=None, niveles=None):
        self._values_by_model = {
            Empresa: [],
            Cargo: [],
            NivelHabilidad: [],
            Habilidad: [],
            Institucion: instituciones or [],
            Carrera: carreras or [],
            NivelEducacional: niveles or [],
            NivelIdioma: [],
            Idioma: [],
        }

    def scalars(self, statement):
        model = statement.column_descriptions[0]["entity"]
        return _ScalarResult(self._values_by_model.get(model, []))


def _institucion(item_id: int, nombre: str):
    return SimpleNamespace(inst_id=item_id, inst_nombre=nombre)


def _carrera(item_id: int, nombre: str):
    return SimpleNamespace(crra_id=item_id, crra_nombre=nombre)


def _nivel(item_id: int, nombre: str):
    return SimpleNamespace(nved_id=item_id, nved_nombre=nombre)


def _derive_estudios(texto: str, *, instituciones=None, carreras=None, niveles=None):
    nested, _warnings = services.derive_nested_from_cv(
        _FakeDb(
            instituciones=instituciones,
            carreras=carreras,
            niveles=niveles,
        ),
        texto,
    )
    return nested["estudios"]


def test_estudios_mapea_carrera_exacta():
    estudios = _derive_estudios(
        "Ingenieria Informatica",
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_carrera_id"] == 20
    assert estudios[0]["etcd_institucion_id"] is None


def test_estudios_mapea_institucion_exacta():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] is None


def test_estudios_mapea_mayusculas_y_tildes():
    estudios = _derive_estudios(
        "universidad tecnologica inacap ingenieria informatica profesional",
        instituciones=[_institucion(10, "Universidad Tecnológica INACAP")],
        carreras=[_carrera(20, "Ingeniería Informática")],
        niveles=[_nivel(30, "Profesional")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] == 20
    assert estudios[0]["etcd_nivel_educacional_id"] == 30


def test_estudios_mapea_espacios_adicionales():
    estudios = _derive_estudios(
        "Universidad    Tecnologica    INACAP    Ingenieria    Informatica",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] == 20


def test_estudios_mapea_puntuacion_y_separadores():
    estudios = _derive_estudios(
        "Universidad Tecnologica, INACAP - Ingenieria en Diseno UX - UI",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingeniería en Diseño UX/UI")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] == 20


def test_estudios_mapea_carrera_y_no_exige_institucion():
    estudios = _derive_estudios(
        "Instituto no catalogado Ingenieria Informatica",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_carrera_id"] == 20
    assert estudios[0]["etcd_institucion_id"] is None


def test_estudios_mapea_institucion_y_no_exige_carrera():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Carrera no catalogada",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] is None


def test_estudios_no_genera_si_no_reconoce_institucion_ni_carrera():
    estudios = _derive_estudios(
        "Centro Desconocido Carrera no catalogada",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert estudios == []


def test_estudios_no_elije_institucion_ambigua():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Ingenieria Informatica",
        instituciones=[
            _institucion(10, "Universidad Tecnologica INACAP"),
            _institucion(11, "Universidad Tecnológica INACAP"),
        ],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] is None
    assert estudios[0]["etcd_carrera_id"] == 20


def test_estudios_no_elije_carrera_ambigua():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Ingenieria en Diseno UX UI",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[
            _carrera(20, "Ingeniería en Diseño UX/UI"),
            _carrera(21, "Ingenieria en Diseno UX - UI"),
        ],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_carrera_id"] is None


def test_estudios_no_mapea_coincidencia_dentro_de_palabra_mas_larga():
    estudios = _derive_estudios(
        "Programa UXResearch UniversidadDesconocida",
        carreras=[_carrera(20, "UX")],
    )

    assert estudios == []


def test_estudios_integracion_confirma_ids_y_fechas_en_none():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Ingenieria en Diseno UX - UI Profesional 2018 - 2022",
        instituciones=[_institucion(10, "Universidad Tecnológica INACAP")],
        carreras=[_carrera(20, "Ingeniería en Diseño UX/UI")],
        niveles=[_nivel(30, "Profesional")],
    )

    assert estudios == [
        {
            "etcd_nivel_educacional_id": 30,
            "etcd_institucion_id": 10,
            "etcd_carrera_id": 20,
            "etcd_fecha_inicio": None,
            "etcd_fecha_fin": None,
        }
    ]


def test_estudios_extrae_fecha_misma_linea_mes_anio_numerico_03_2017_01_2019():
    estudios = _derive_estudios(
        "03/2017 - 01/2019 MBA Magister Universidad Tecnica Federico Santa Maria",
        instituciones=[_institucion(10, "Universidad Tecnica Federico Santa Maria")],
        carreras=[_carrera(20, "MBA Magister")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2017, 3, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2019, 1, 31)


def test_estudios_extrae_fecha_misma_linea_mes_anio_numerico_01_2010_09_2016():
    estudios = _derive_estudios(
        "01/2010 - 09/2016 Ingenieria Civil Industrial Universidad de Playa Ancha",
        instituciones=[_institucion(10, "Universidad de Playa Ancha")],
        carreras=[_carrera(20, "Ingenieria Civil Industrial")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2010, 1, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2016, 9, 30)


def test_estudios_extrae_fecha_misma_linea_mes_anio_numerico_01_2012_06_2016():
    estudios = _derive_estudios(
        "01/2012 - 06/2016 Ingeniero en Computacion e Informatica Universidad Jose Velez",
        instituciones=[_institucion(10, "Universidad Jose Velez")],
        carreras=[_carrera(20, "Ingeniero en Computacion e Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2012, 1, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2016, 6, 30)


def test_estudios_extrae_fecha_misma_linea_mes_texto():
    estudios = _derive_estudios(
        "Feb 2016 - Jul 2016 Intercambio universitario Universidad de Zurich",
        instituciones=[_institucion(10, "Universidad de Zurich")],
        carreras=[_carrera(20, "Intercambio universitario")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2016, 2, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2016, 7, 31)


def test_estudios_extrae_fecha_linea_adyacente_en_bloque_educativo():
    estudios = _derive_estudios(
        "Universidad Tecnica Federico Santa Maria MBA Magister\n03/2017 - 01/2019",
        instituciones=[_institucion(10, "Universidad Tecnica Federico Santa Maria")],
        carreras=[_carrera(20, "MBA Magister")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2017, 3, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2019, 1, 31)


def test_estudios_no_extrae_fecha_anio_anio_2011_2015():
    estudios = _derive_estudios(
        "2011 - 2015 Ingeniero en Informatica Universidad Tecnologica INACAP",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingeniero en Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_extrae_fecha_anio_anio_2013_2018():
    estudios = _derive_estudios(
        "2013 - 2018 Universidad de Santiago de Chile Ingenieria de Ejecucion en Informatica",
        instituciones=[_institucion(10, "Universidad de Santiago de Chile")],
        carreras=[_carrera(20, "Ingenieria de Ejecucion en Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_extrae_fecha_anio_unico_2007():
    estudios = _derive_estudios(
        "Ingenieria Informatica Universidad Autonoma Gabriel Rene Moreno 2007",
        instituciones=[_institucion(10, "Universidad Autonoma Gabriel Rene Moreno")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_extrae_fecha_anio_unico_2011():
    estudios = _derive_estudios(
        "Bachiller en Ciencias Unidad Educativa Madariaga 2011",
        instituciones=[_institucion(10, "Unidad Educativa Madariaga")],
        carreras=[_carrera(20, "Bachiller en Ciencias")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_extrae_rango_partido_entre_lineas():
    estudios = _derive_estudios(
        "Ingenieria Administracion de Empresas Universidad Tecnologica de Chile INACAP\nmar. 2011 - feb.\n2020",
        instituciones=[_institucion(10, "Universidad Tecnologica de Chile INACAP")],
        carreras=[_carrera(20, "Ingenieria Administracion de Empresas")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_contamina_con_fecha_de_certificacion_cercana():
    estudios = _derive_estudios(
        "Ingenieria Informatica Universidad Tecnologica INACAP\nCertificacion Increible 03/2017 - 01/2019",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_contamina_con_fecha_de_experiencia_cercana():
    estudios = _derive_estudios(
        "Ingenieria Informatica Universidad Tecnologica INACAP\nExperiencia laboral 09/2018 - 08/2024 Analista Programador",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_no_asocia_fecha_de_ayudantia_a_universidad_adyacente():
    estudios = _derive_estudios(
        "\n".join([
            "Ayudante Instructor y Corrector",
            "Ingenieria Ambiental (Mar 2018 - Jul 2018)",
            "Universidad Adolfo Ibanez",
            "Asistente en ferias de exposicion",
        ]),
        instituciones=[_institucion(10, "Universidad Adolfo Ibanez")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_institucion_id"] == 10
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_mantiene_fecha_academica_adyacente_sin_contexto_profesional():
    estudios = _derive_estudios(
        "\n".join([
            "Universidad de Zurich Intercambio universitario",
            "Feb 2016 - Jul 2016",
        ]),
        instituciones=[_institucion(10, "Universidad de Zurich")],
        carreras=[_carrera(20, "Intercambio universitario")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] == date(2016, 2, 1)
    assert estudios[0]["etcd_fecha_fin"] == date(2016, 7, 31)


def test_estudios_no_extrae_fecha_si_hay_mas_de_un_rango_ambiguo():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Ingenieria Informatica 03/2017 - 01/2019 01/2010 - 09/2016",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None


def test_estudios_sin_fecha_mantiene_none():
    estudios = _derive_estudios(
        "Universidad Tecnologica INACAP Ingenieria Informatica",
        instituciones=[_institucion(10, "Universidad Tecnologica INACAP")],
        carreras=[_carrera(20, "Ingenieria Informatica")],
    )

    assert len(estudios) == 1
    assert estudios[0]["etcd_fecha_inicio"] is None
    assert estudios[0]["etcd_fecha_fin"] is None
