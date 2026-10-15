from __future__ import annotations

import io
import re
import zipfile
from datetime import datetime, timedelta

from pypdf import PdfReader

from modulo6_test_support import H, TestingSessionLocal, client, reset_db, seed
from app.candidatos import models as candidato_models
from app.catalogos import models as catalog_models
from app.clientes import models as cliente_models
from app.entrevistas import models as entrevista_models
from app.solicitudes import models as solicitud_models
from app.usuarios import models as user_models


def _preparar_solicitud_comparativa(seed):
    db = TestingSessionLocal()
    try:
        area = db.query(user_models.Area).filter(user_models.Area.area_nombre == "QA M6").one()
        empresa = db.query(cliente_models.Empresa).filter(cliente_models.Empresa.emp_nombre == "ELITSOFT QA").one()
        cliente = cliente_models.Cliente(
            cli_nombre="Cliente QA",
            cli_area_empresa_id=area.area_id,
            cli_empresa_id=empresa.emp_id,
            cli_email="cliente.qa@sakura.cl",
        )
        modalidad = catalog_models.Modalidad(mdld_nombre="Hibrida", mdld_descripcion="Hibrida")
        db.add_all([cliente, modalidad])
        db.flush()

        solicitud = db.get(solicitud_models.Solicitud, seed["s1"])
        solicitud.sol_cliente_id = cliente.cli_id
        solicitud.sol_modalidad_id = modalidad.mdld_id
        solicitud.sol_cantidad_vacantes = 3

        db.add_all([
            solicitud_models.SolicitudHabilidad(
                solhb_solicitud_id=seed["s1"],
                solhb_habilidad_id=seed["skill"],
                solhb_nivel_habilidad_id=None,
                solhb_anios_experiencia_req=2,
                solhb_es_excluyente=True,
            ),
            solicitud_models.SolicitudHabilidad(
                solhb_solicitud_id=seed["s1"],
                solhb_habilidad_id=seed["skill2"],
                solhb_nivel_habilidad_id=None,
                solhb_anios_experiencia_req=1,
                solhb_es_excluyente=False,
            ),
        ])

        db.execute(
            solicitud_models.SolicitudCandidato.__table__.update()
            .where(solicitud_models.SolicitudCandidato.slcd_id == seed["psel"])
            .values(slcd_pretension_renta=1500000)
        )
        candidato_contratado_id = db.get(solicitud_models.SolicitudCandidato, seed["pcon"]).slcd_candidato_id
        db.execute(
            catalog_models.Disponibilidad.__table__.update()
            .where(catalog_models.Disponibilidad.disp_id == seed["disp"])
            .values(disp_nombre="Inmediata")
        )
        db.execute(
            db.get(solicitud_models.SolicitudCandidato, seed["pcon"])
            .__table__
            .update()
            .where(solicitud_models.SolicitudCandidato.slcd_id == seed["pcon"])
            .values(slcd_pretension_renta=None)
        )
        from app.candidatos import models as candidato_models

        db.execute(
            candidato_models.Candidato.__table__.update()
            .where(candidato_models.Candidato.cand_id == candidato_contratado_id)
            .values(cand_disponibilidad_id=None)
        )
        db.commit()
    finally:
        db.close()


def test_comparativo_datos_solicitud_con_varios_candidatos_y_tecnologias(client, seed):
    _preparar_solicitud_comparativa(seed)

    response = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["psel"], seed["pcon"]]},
        headers=H(seed["reporter"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["solicitud"] == {
        "solicitud_id": seed["s1"],
        "codigo": "SOL-M60001",
        "cargo": "Backend Senior",
        "empresa": "ELITSOFT QA",
        "vacantes": 3,
        "area": "QA M6",
        "modalidad": "Hibrida",
    }
    assert [c["solicitud_candidato_id"] for c in body["candidatos"]] == [seed["psel"], seed["pcon"]]
    assert {h["habilidad"] for h in body["habilidades_requeridas"]} == {"Python", "PostgreSQL"}
    assert {h["habilidad"] for h in body["candidatos"][0]["tecnologias_excluyentes"]} == {"Python"}
    assert {h["habilidad"] for h in body["candidatos"][0]["tecnologias_no_excluyentes"]} == {"PostgreSQL"}
    pcon_postgresql = body["candidatos"][1]["tecnologias_no_excluyentes"][0]
    assert pcon_postgresql["habilidad"] == "PostgreSQL"
    assert pcon_postgresql["presente"] is False
    assert pcon_postgresql["nivel_candidato"] == "Nada"
    assert body["candidatos"][0]["pretension_renta"] == 1500000
    assert body["candidatos"][1]["pretension_renta"] is None
    assert body["candidatos"][1]["disponibilidad"] is None
    assert body["candidatos"][0]["observacion_operacional"] == "Sin observaciones registradas"
    assert body["candidatos"][0]["observacion_tecnica"] == "Sin observaciones registradas"


def test_comparativo_diferencia_habilidad_ausente_de_nivel_no_informado(client, seed):
    _preparar_solicitud_comparativa(seed)
    db = TestingSessionLocal()
    try:
        candidato_id = db.get(solicitud_models.SolicitudCandidato, seed["pdes"]).slcd_candidato_id
        db.add(candidato_models.CandidatoHabilidad(
            cdhb_candidato_id=candidato_id,
            cdhb_habilidad_id=seed["skill2"],
            cdhb_nivel_habilidad_id=None,
            cdhb_anios_experiencia=1,
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["pcon"], seed["pdes"]]},
        headers=H(seed["reporter"]),
    )

    assert response.status_code == 200, response.text
    pcon, pdes = response.json()["candidatos"]
    assert pcon["tecnologias_no_excluyentes"][0]["presente"] is False
    assert pcon["tecnologias_no_excluyentes"][0]["nivel_candidato"] == "Nada"
    assert pdes["tecnologias_no_excluyentes"][0]["presente"] is True
    assert pdes["tecnologias_no_excluyentes"][0]["nivel_candidato"] == "No informado"


def test_comparativo_rechaza_postulaciones_de_otras_solicitudes(client, seed):
    _preparar_solicitud_comparativa(seed)

    response = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["psel"], seed["psecond"]]},
        headers=H(seed["reporter"]),
    )

    assert response.status_code == 409
    assert seed["psecond"] in response.json()["detail"]["ids"]


def test_comparativo_descarga_pdf_y_docx_editable(client, seed):
    _preparar_solicitud_comparativa(seed)
    payload = {"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["psel"], seed["pcon"]]}

    pdf = client.post("/informes/comparativo/pdf/descargar", json=payload, headers=H(seed["reporter"]))
    assert pdf.status_code == 200, pdf.text
    assert pdf.content.startswith(b"%PDF")
    pdf_text = "".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(pdf.content)).pages)
    assert "INFORME DE CANDIDATOS" in pdf_text
    assert "CANDIDATOS SELECCIONADOS" in pdf_text
    assert "Seleccionado QA" in pdf_text
    assert "PostgreSQL" in pdf_text
    assert "Sin observaciones registradas" in pdf_text
    assert "Pendiente de definición funcional" not in pdf_text

    docx = client.post("/informes/comparativo/docx/descargar", json=payload, headers=H(seed["reporter"]))
    assert docx.status_code == 200, docx.text
    assert docx.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    package = zipfile.ZipFile(io.BytesIO(docx.content))
    assert "word/document.xml" in package.namelist()
    xml = package.read("word/document.xml").decode("utf-8")
    text = re.sub(r"<[^>]+>", " ", xml)
    assert "INFORME DE CANDIDATOS" in text
    assert "Resumen comparativo para revisión y selección" in text
    assert "Seleccionado QA" in text
    assert "PostgreSQL" in text
    assert "Nada" in text
    assert "Sin observaciones registradas" in text
    assert "Pendiente de definición funcional" not in text


def test_comparativo_descargas_rechazan_postulaciones_de_otras_solicitudes(client, seed):
    _preparar_solicitud_comparativa(seed)
    payload = {"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["psel"], seed["psecond"]]}

    pdf = client.post("/informes/comparativo/pdf/descargar", json=payload, headers=H(seed["reporter"]))
    docx = client.post("/informes/comparativo/docx/descargar", json=payload, headers=H(seed["reporter"]))

    assert pdf.status_code == 409
    assert docx.status_code == 409


def test_comparativo_valida_lista_vacia_e_ids_invalidos(client, seed):
    empty = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": []},
        headers=H(seed["reporter"]),
    )
    missing = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": [999999]},
        headers=H(seed["reporter"]),
    )

    assert empty.status_code == 422
    assert missing.status_code == 404


def test_comparativo_admite_solicitud_sin_datos_opcionales(client, seed):
    response = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s2"], "solicitud_candidato_ids": [seed["psecond"]]},
        headers=H(seed["reporter"]),
    )

    assert response.status_code == 200, response.text
    solicitud = response.json()["solicitud"]
    assert solicitud["codigo"] == "SOL-M60002"
    assert solicitud["empresa"] is None
    assert solicitud["area"] is None
    assert solicitud["modalidad"] is None


def test_comparativo_usa_ultima_observacion_por_area(client, seed):
    db = TestingSessionLocal()
    try:
        now = datetime.now()
        estado = db.query(catalog_models.EstadoEntrevista).filter_by(esev_nombre="Realizada").one()
        tipo_tecnica = db.query(catalog_models.TipoEntrevista).filter_by(tpet_nombre="Tecnica").one()
        tipo_operacional = db.query(catalog_models.TipoEntrevista).filter_by(tpet_nombre="RRHH").one()
        resultado = db.query(catalog_models.NombreResultado).filter_by(nore_nombre="Aprobado").one()
        for index, tipo in enumerate([tipo_tecnica, tipo_tecnica, tipo_operacional, tipo_operacional]):
            fecha = now + timedelta(days=index + 1)
            cita = entrevista_models.CitaEntrevista(
                ctev_solicitud_candidato_id=seed["psel"],
                ctev_tipo_entrevista_id=tipo.tpet_id,
                ctev_estado_entrevista_id=estado.esev_id,
                ctev_fecha_hora_inicio=fecha,
                ctev_fecha_hora_fin=fecha + timedelta(hours=1),
                ctev_fecha_creacion=now,
                ctev_titulo_evento=f"Entrevista {tipo.tpet_nombre} {index}",
                ctev_usuario_creador_id=seed["admin"],
            )
            db.add(cita)
            db.flush()
            area = "tecnica" if tipo.tpet_id == tipo_tecnica.tpet_id else "operacional"
            db.add(entrevista_models.EvaluacionEntrevista(
                even_nombre_resultado_id=resultado.nore_id,
                even_observacion=f"Observacion {area} {index}",
                even_cita_entrevista_id=cita.ctev_id,
                even_usuario_id=seed["recruiter"],
                even_tipo_entrevista_id=tipo.tpet_id,
                even_fecha_creacion=fecha,
                even_fecha_actualizacion=fecha,
            ))
        db.commit()
    finally:
        db.close()
    _preparar_solicitud_comparativa(seed)

    response = client.post(
        "/informes/comparativo/datos",
        json={"solicitud_id": seed["s1"], "solicitud_candidato_ids": [seed["psel"]]},
        headers=H(seed["reporter"]),
    )

    assert response.status_code == 200, response.text
    candidate = response.json()["candidatos"][0]
    assert candidate["observacion_tecnica"] == "Observacion tecnica 1"
    assert candidate["observacion_operacional"] == "Observacion operacional 3"
    assert candidate["observaciones_pendientes_definicion"] == []
