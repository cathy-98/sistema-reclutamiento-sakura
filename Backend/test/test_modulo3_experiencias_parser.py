from datetime import date
from contextlib import nullcontext
from types import SimpleNamespace

from app.candidatos import services
from app.candidatos.services import _buscar_unico_por_nombre_normalizado
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
    def __init__(self, *, empresas=None, cargos=None):
        self._values_by_model = {
            Empresa: empresas or [],
            Cargo: cargos or [],
            NivelHabilidad: [],
            Habilidad: [],
            Institucion: [],
            Carrera: [],
            NivelEducacional: [],
            NivelIdioma: [],
            Idioma: [],
        }

    def scalars(self, statement):
        model = statement.column_descriptions[0]["entity"]
        return _ScalarResult(self._values_by_model.get(model, []))


class _WritableFakeDb(_FakeDb):
    def add(self, instance):
        self._values_by_model.setdefault(type(instance), []).append(instance)

    def flush(self):
        for values in self._values_by_model.values():
            for index, item in enumerate(values, start=1):
                for attr in ("emp_id", "crgo_id"):
                    if hasattr(item, attr) and getattr(item, attr, None) is None:
                        setattr(item, attr, index)

    def begin_nested(self):
        return nullcontext()


def _item(item_id: int, nombre: str):
    return SimpleNamespace(id=item_id, nombre=nombre)


def _match(items, contexto):
    return _buscar_unico_por_nombre_normalizado(items, "nombre", "id", contexto)


def _empresa(item_id: int, nombre: str):
    return SimpleNamespace(emp_id=item_id, emp_nombre=nombre)


def _cargo(item_id: int, nombre: str):
    return SimpleNamespace(crgo_id=item_id, crgo_nombre=nombre)


def _derive_experiencias(texto: str, *, empresas, cargos):
    nested, _warnings = services.derive_nested_from_cv(
        _FakeDb(empresas=empresas, cargos=cargos),
        texto,
    )
    return nested["experiencias"]


def test_match_experiencia_coincidencia_exacta():
    item = _item(1, "Disenador UX/UI")

    assert _match([item], "Trabaje como Disenador UX/UI en el equipo digital") is item


def test_match_experiencia_ignora_mayusculas():
    item = _item(1, "Disenador UX/UI")

    assert _match([item], "trabaje como disenador ux/ui en el equipo digital") is item


def test_match_experiencia_ignora_tildes():
    item = _item(1, "Diseñador UX/UI")

    assert _match([item], "Experiencia como Disenador UX/UI") is item


def test_match_experiencia_tolera_separadores_equivalentes():
    item = _item(1, "Disenador UX/UI")

    assert _match([item], "Experiencia: Disenador UX - UI") is item


def test_match_experiencia_tolera_espacios_adicionales():
    item = _item(1, "Disenador UX/UI")

    assert _match([item], "Experiencia como Disenador    UX    UI") is item


def test_match_experiencia_no_asocia_textos_realmente_diferentes():
    item = _item(1, "Disenador UX/UI")

    assert _match([item], "Experiencia como Desarrollador Backend") is None


def test_match_experiencia_ambigua_no_elije_arbitrariamente():
    items = [
        _item(1, "Disenador UX/UI"),
        _item(2, "Disenador UX - UI"),
    ]

    assert _match(items, "Experiencia como Disenador UX UI") is None


def test_match_experiencia_ambigua_por_coincidencia_parcial_no_elije():
    items = [
        _item(1, "Disenador UX"),
        _item(2, "Disenador UX/UI"),
    ]

    assert _match(items, "Experiencia como Disenador UX/UI") is None


def test_derive_nested_mapea_experiencia_con_empresa_y_cargo_formato_distinto():
    experiencias = _derive_experiencias(
        "Experiencia laboral\nEmpresa Ejemplo S.A Disenador UX - UI\nProyecto mobile",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_empresa_id"] == 10
    assert experiencias[0]["expl_cargo_id"] == 20
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None
    assert experiencias[0]["habilidades_ids"] == []


def test_derive_nested_extrae_fecha_experiencia_misma_linea_mes_anio_numerico():
    experiencias = _derive_experiencias(
        "09/2018 - 08/2024, Analista Programador, Soluciones IT Transparentes, Santiago",
        empresas=[_empresa(10, "Soluciones IT Transparentes")],
        cargos=[_cargo(20, "Analista Programador")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] == date(2018, 9, 1)
    assert experiencias[0]["expl_fecha_fin"] == date(2024, 8, 31)


def test_derive_nested_extrae_fecha_experiencia_linea_posterior_mes_texto():
    experiencias = _derive_experiencias(
        "Black+Decker - Asistente de Bodega y Operaciones\nMayo - Julio 2019\nPreparacion de pedidos",
        empresas=[_empresa(10, "Black+Decker")],
        cargos=[_cargo(20, "Asistente de Bodega y Operaciones")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] == date(2019, 5, 1)
    assert experiencias[0]["expl_fecha_fin"] == date(2019, 7, 31)


def test_derive_nested_extrae_fecha_experiencia_actualidad_como_fin_none():
    experiencias = _derive_experiencias(
        "BOLSA DE COMERCIO - SONDA\nOct. 2019 - Presente\nOperador de procesos",
        empresas=[_empresa(10, "BOLSA DE COMERCIO")],
        cargos=[_cargo(20, "Operador de procesos")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] == date(2019, 10, 1)
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_experiencia_anio_anio_2019_2022():
    experiencias = _derive_experiencias(
        "Analista Contable e Impositivo | Empresa Increible 2\n2019 - 2022\nSoporte contable",
        empresas=[_empresa(10, "Empresa Increible 2")],
        cargos=[_cargo(20, "Analista Contable e Impositivo")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_experiencia_anio_anio_2022_2024():
    experiencias = _derive_experiencias(
        "Plan Ok Customer Support UX/UI Designer\n2022 - 2024\nSoporte y experiencia de usuario",
        empresas=[_empresa(10, "Plan Ok")],
        cargos=[_cargo(20, "Customer Support UX/UI Designer")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_experiencia_anio_anio_2013_2015():
    experiencias = _derive_experiencias(
        "Control GPS Desarrollador Web\n2013 - 2015\nDesarrollo de aplicaciones web",
        empresas=[_empresa(10, "Control GPS")],
        cargos=[_cargo(20, "Desarrollador Web")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_si_actualidad_inicia_con_solo_anio():
    experiencias = _derive_experiencias(
        "Elitsoft UX/UI Designer\n2020 - Actualidad\nDiseno de productos digitales",
        empresas=[_empresa(10, "Elitsoft")],
        cargos=[_cargo(20, "UX/UI Designer")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_extrae_fecha_experiencia_a_la_fecha_con_mes_texto():
    experiencias = _derive_experiencias(
        "Telecheque Informacion y Gestion\nJulio 2018 a la fecha\nJefe de Proyecto TI",
        empresas=[_empresa(10, "Telecheque Informacion y Gestion")],
        cargos=[_cargo(20, "Jefe de Proyecto TI")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] == date(2018, 7, 1)
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_experiencia_vigente():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A Disenador UX/UI\nOct. 2019 - vigente\nProyecto mobile",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_si_hay_multiples_rangos_cercanos():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A Disenador UX/UI 2019 - 2022 / proyecto 2020 - 2021",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_extrae_fecha_de_linea_con_senal_educativa():
    experiencias = _derive_experiencias(
        "Elitsoft UX/UI Designer\n2024 - Actualidad Udemy\nDiseno de productos digitales",
        empresas=[_empresa(10, "Elitsoft")],
        cargos=[_cargo(20, "UX/UI Designer")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_fecha_inicio"] is None
    assert experiencias[0]["expl_fecha_fin"] is None


def test_derive_nested_no_crea_experiencia_si_solo_coincide_empresa():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A. Desarrollador Backend",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert experiencias == []


def test_derive_nested_no_crea_experiencia_si_solo_coincide_cargo():
    experiencias = _derive_experiencias(
        "Compania Desconocida Disenador UX/UI",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert experiencias == []


def test_match_nombre_corto_no_coincide_dentro_de_palabra_larga():
    item = _item(1, "QA")

    assert _match([item], "Experiencia en plataforma QAutomation") is None


def test_derive_nested_mapea_empresa_con_puntuacion_equivalente():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A Disenador UX/UI",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert len(experiencias) == 1
    assert experiencias[0]["expl_empresa_id"] == 10
    assert experiencias[0]["expl_cargo_id"] == 20


def test_match_no_reconoce_token_dentro_de_palabra_mas_larga():
    item = _item(1, "UX")

    assert _match([item], "Experiencia en UXResearch") is None


def test_derive_nested_no_mapea_experiencia_si_empresa_es_ambigua():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A Disenador UX/UI",
        empresas=[
            _empresa(10, "Empresa Ejemplo S.A."),
            _empresa(11, "Empresa Ejemplo S.A"),
        ],
        cargos=[_cargo(20, "Diseñador UX/UI")],
    )

    assert experiencias == []


def test_derive_nested_crea_empresa_y_cargo_nuevos_desde_par_de_trabajo():
    db = _WritableFakeDb()

    nested, warnings = services.derive_nested_from_cv(
        db,
        "Experiencia laboral\nNova Sistemas SpA - Arquitecto de Integraciones",
    )

    assert warnings == [
        "No se detectaron habilidades persistibles: no hubo un valor válido, inequívoco y asociado a un contexto confiable.",
        "No se detectaron estudios persistibles: no hubo institución o carrera válida, inequívoca y asociada a contexto académico.",
    ]
    assert len(nested["experiencias"]) == 1
    empresas = db._values_by_model[Empresa]
    cargos = db._values_by_model[Cargo]
    assert empresas[0].emp_nombre == "Nova Sistemas SpA"
    assert empresas[0].emp_creado_automaticamente is True
    assert cargos[0].crgo_nombre == "Arquitecto de Integraciones"
    assert cargos[0].crgo_creado_automaticamente is True


def test_derive_nested_reutiliza_empresa_normalizada_y_crea_solo_cargo_nuevo():
    db = _WritableFakeDb(empresas=[_empresa(10, "Compañía Ñ")])

    nested, _warnings = services.derive_nested_from_cv(
        db,
        "Experiencia laboral\nCompania   N - Especialista de Datos",
    )

    assert len(nested["experiencias"]) == 1
    assert nested["experiencias"][0]["expl_empresa_id"] == 10
    assert len(db._values_by_model[Empresa]) == 1
    assert len(db._values_by_model[Cargo]) == 1


def test_derive_nested_no_crea_catalogos_desde_par_generico():
    db = _WritableFakeDb()

    nested, warnings = services.derive_nested_from_cv(
        db,
        "Experiencia laboral\nEmpresa - Cargo",
    )

    assert nested["experiencias"] == []
    assert db._values_by_model[Empresa] == []
    assert db._values_by_model[Cargo] == []
    assert any("empresa" in warning.lower() for warning in warnings)


def test_derive_nested_no_mapea_experiencia_si_cargo_es_ambiguo():
    experiencias = _derive_experiencias(
        "Empresa Ejemplo S.A Disenador UX UI",
        empresas=[_empresa(10, "Empresa Ejemplo S.A.")],
        cargos=[
            _cargo(20, "Diseñador UX/UI"),
            _cargo(21, "Diseñador UX - UI"),
        ],
    )

    assert experiencias == []
