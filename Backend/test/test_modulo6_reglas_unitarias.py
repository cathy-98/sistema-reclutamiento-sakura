from __future__ import annotations
import os
from datetime import date
from pathlib import Path

import pytest
from reportlab.lib import colors

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "qa-m6-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz")

from app.auth import email_service
from app.informes import pdf_service, services


def C(state="En entrevista", technical=None, configured=0, interviews=None, meta=None):
    return services.classify_candidate({"estado_postulacion":state}, technical or [], configured, interviews or [], meta or {"total":0,"pending":False,"missing_evaluations":False})

@pytest.mark.parametrize("state", ["Seleccionado","Contratado","SELECCIONADO"," contratado "])
def test_estado_m3_aprobado_tiene_prioridad(state):
    c,s,r=C(state,[{"aprobado":False,"cuestionario":"X"}],1,[{"resultado":"No Aprobado"}],{"total":1,"pending":False,"missing_evaluations":False}); assert c=="APROBADO" and s is False

@pytest.mark.parametrize("state", ["Descartado","Inhabilitado","DESCARTADO"])
def test_estado_m3_rechazado_tiene_prioridad(state):
    c,s,r=C(state); assert c=="NO_APROBADO" and s is False

def test_en_revision_pendiente(): assert C("En revision")[0]=="PENDIENTE"
def test_estado_desconocido_pendiente(): assert C("Otro")[0]=="PENDIENTE"
def test_falla_tecnica_no_aprobado_sugerido():
    c,s,r=C(technical=[{"aprobado":False,"cuestionario":"Python"}],configured=1); assert (c,s)==("NO_APROBADO",True) and "Python" in r[0]
def test_test_no_rendido_pendiente(): assert C(technical=[{"aprobado":None}],configured=1)[0]=="PENDIENTE"
def test_falta_asignacion_test_pendiente(): assert C(technical=[],configured=1)[0]=="PENDIENTE"
def test_no_aprobado_entrevista_sugerido():
    c,s,r=C(interviews=[{"resultado":"No Aprobado"}],meta={"total":1,"pending":False,"missing_evaluations":False}); assert (c,s)==("NO_APROBADO",True)
@pytest.mark.parametrize("result", ["En Espera","Requiere Segunda Entrevista"])
def test_resultados_entrevista_pendientes(result): assert C(interviews=[{"resultado":result}],meta={"total":1,"pending":False,"missing_evaluations":False})[0]=="PENDIENTE"
def test_entrevista_programada_pendiente(): assert C(interviews=[],meta={"total":1,"pending":True,"missing_evaluations":False})[0]=="PENDIENTE"
def test_entrevista_realizada_sin_evaluacion_pendiente(): assert C(interviews=[],meta={"total":1,"pending":False,"missing_evaluations":True})[0]=="PENDIENTE"
def test_sin_entrevista_pendiente(): assert C(interviews=[],meta={"total":0,"pending":False,"missing_evaluations":False})[0]=="PENDIENTE"
@pytest.mark.parametrize("result", ["Aprobado","Aprobado con Observaciones"])
def test_todo_aprobado_es_aprobado_sugerido(result):
    c,s,r=C(technical=[{"aprobado":True}],configured=1,interviews=[{"resultado":result}],meta={"total":1,"pending":False,"missing_evaluations":False}); assert (c,s)==("APROBADO",True)
def test_normalizacion_acentos_y_espacios(): assert services._norm("  Requiere   SEGUNDA entrevista ")=="requiere segunda entrevista"
def test_slug_quita_acentos_y_simbolos(): assert services._slug("José Pérez / Python") == "Jose_Perez_Python"
def test_periodo_completo(): assert "2020" in services._period(date(2020,1,1),date(2021,2,1)) and "2021" in services._period(date(2020,1,1),date(2021,2,1))
def test_periodo_actualidad(): assert "actualidad" in services._period(date(2020,1,1),None)
def test_traffic_green(monkeypatch): monkeypatch.setenv("REPORTS_GREEN_THRESHOLD","80"); assert pdf_service._traffic(85)==pdf_service.GREEN
def test_traffic_yellow(monkeypatch): monkeypatch.setenv("REPORTS_GREEN_THRESHOLD","80"); monkeypatch.setenv("REPORTS_YELLOW_THRESHOLD","60"); assert pdf_service._traffic(70)==pdf_service.YELLOW
def test_traffic_red(monkeypatch): monkeypatch.setenv("REPORTS_YELLOW_THRESHOLD","60"); assert pdf_service._traffic(20)==pdf_service.RED
def test_reset_url_sin_query(): assert email_service.build_password_reset_url("https://x/reset","abc")=="https://x/reset?token=abc"
def test_reset_url_con_query(): assert email_service.build_password_reset_url("https://x/reset?a=1","abc")=="https://x/reset?a=1&token=abc"
def test_smtp_config_falta_username(monkeypatch):
    monkeypatch.delenv("SMTP_USERNAME",raising=False); monkeypatch.delenv("SMTP_PASSWORD",raising=False)
    with pytest.raises(email_service.EmailConfigurationError): email_service.get_smtp_config()
def test_send_email_sin_destinatarios():
    with pytest.raises(email_service.EmailConfigurationError): email_service.send_email(to_emails=[],subject="x",body_text="x")
def test_send_email_adjunto_inexistente(monkeypatch,tmp_path):
    monkeypatch.setenv("SMTP_USERNAME","qa@example.com"); monkeypatch.setenv("SMTP_PASSWORD","x")
    with pytest.raises(email_service.EmailDeliveryError): email_service.send_email(to_emails=["x@example.com"],subject="x",body_text="x",attachments=[("a.pdf",tmp_path/"no.pdf")])
