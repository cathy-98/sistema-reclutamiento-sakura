from __future__ import annotations

from modulo6_test_support import H, client, seed, reset_db


def test_catalogos_canonicos_categoria_e_idioma(client, seed):
    categorias = client.get("/catalogos/categorias-habilidad")
    idiomas = client.get("/catalogos/idiomas")
    assert categorias.status_code == 200
    assert idiomas.status_code == 200
    assert any(x["cthb_id"] == seed["cat_lang"] for x in categorias.json())
    assert any(x["idio_id"] == seed["lang_es"] for x in idiomas.json())


def test_habilidad_catalogo_expone_categoria_y_filtro(client, seed):
    one = client.get(f"/catalogos/habilidades/{seed['skill']}")
    assert one.status_code == 200
    body = one.json()
    assert body["hab_categoria_habilidad_id"] == seed["cat_lang"]
    assert body["categoria"]["cthb_id"] == seed["cat_lang"]

    filtered = client.get("/catalogos/habilidades", params={"categoria_id": seed["cat_lang"]})
    assert filtered.status_code == 200
    assert any(x["hab_id"] == seed["skill"] for x in filtered.json())
    assert all(x["hab_categoria_habilidad_id"] == seed["cat_lang"] for x in filtered.json())


def test_aliases_m6_siguen_disponibles(client, seed):
    categorias = client.get("/informes/catalogos/categorias-habilidad", headers=H(seed["reporter"]))
    idiomas = client.get("/informes/catalogos/idiomas", headers=H(seed["reporter"]))
    assert categorias.status_code == 200
    assert idiomas.status_code == 200


def test_cambio_categoria_desde_alias_m6_se_refleja_en_catalogo(client, seed):
    changed = client.patch(
        f"/informes/catalogos/habilidades/{seed['skill']}/categoria",
        json={"categoria_id": seed["cat_db"]},
        headers=H(seed["catalog"]),
    )
    assert changed.status_code == 200

    canonical = client.get(f"/catalogos/habilidades/{seed['skill']}")
    assert canonical.status_code == 200
    assert canonical.json()["hab_categoria_habilidad_id"] == seed["cat_db"]
    assert canonical.json()["categoria"]["cthb_id"] == seed["cat_db"]
