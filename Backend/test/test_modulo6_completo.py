from __future__ import annotations
import hashlib, io, zipfile
from pathlib import Path

import pytest
from pypdf import PdfReader
from sqlalchemy import select, text

from modulo6_test_support import TestingSessionLocal, H, HC, client, seed, reset_db
from app.auth.email_service import EmailDeliveryError
from app.informes import models as im, services

# ---------------- Seguridad / RBAC ----------------
def test_listado_sin_token_401(client): assert client.get('/informes/candidatos').status_code==401
def test_listado_sin_rep_view_403(client,seed): assert client.get('/informes/candidatos',headers=H(seed['noperm'])).status_code==403
def test_candidato_no_usa_m6_403(client,seed): assert client.get('/informes/candidatos',headers=HC(seed['csel'])).status_code==403
def test_reporter_puede_listar(client,seed): assert client.get('/informes/candidatos',headers=H(seed['reporter'])).status_code==200
def test_categoria_requiere_cat_admin(client,seed): assert client.patch(f"/informes/catalogos/habilidades/{seed['skill']}/categoria",json={'categoria_id':seed['cat_db']},headers=H(seed['reporter'])).status_code==403
def test_idiomas_get_requiere_can_view(client,seed): assert client.get(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",headers=H(seed['reporter'])).status_code==403
def test_idiomas_put_requiere_can_update(client,seed): assert client.put(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",json={'idiomas':[]},headers=H(seed['canview'])).status_code==403

# ---------------- Clasificación integrada ----------------
@pytest.mark.parametrize('key,expected,suggested',[
 ('psel','APROBADO',False),('pcon','APROBADO',False),('pdes','NO_APROBADO',False),('pinh','NO_APROBADO',False),('prev','PENDIENTE',False),('ppass','APROBADO',True),('pfailt','NO_APROBADO',True),('ppendt','PENDIENTE',False),('pfaili','NO_APROBADO',True),('ppendi','PENDIENTE',False),('pnoinv','PENDIENTE',False)])
def test_clasificaciones_casos_m3_m4_m5(client,seed,key,expected,suggested):
    r=client.get(f"/informes/candidatos/{seed[key]}",headers=H(seed['reporter'])); assert r.status_code==200,r.text; b=r.json(); assert b['clasificacion']==expected; assert b['clasificacion_sugerida'] is suggested

def test_detalle_inexistente_404(client,seed): assert client.get('/informes/candidatos/999999',headers=H(seed['reporter'])).status_code==404
def test_aprobado_permitedirectivos(client,seed): assert client.get(f"/informes/candidatos/{seed['ppass']}",headers=H(seed['reporter'])).json()['puede_enviar_directivos'] is True
def test_rechazo_solo_estado_m3_formal(client,seed):
    assert client.get(f"/informes/candidatos/{seed['pdes']}",headers=H(seed['reporter'])).json()['puede_enviar_rechazo'] is True
    assert client.get(f"/informes/candidatos/{seed['pfailt']}",headers=H(seed['reporter'])).json()['puede_enviar_rechazo'] is False

# ---------------- Filtros / paginación ----------------
def _ids(r): return {x['solicitud_candidato_id'] for x in r.json()['items']}
@pytest.mark.parametrize('params,key',[
 ({'clasificacion':'APROBADO'},'psel'),({'solicitud_id':None},'psel'),({'cargo_id':None},'psel'),({'habilidad_id':None},'psel'),({'estado_postulacion_id':None},'psel'),({'disponibilidad_id':None},'psel'),({'match_min':90},'psel'),({'match_max':45},'pdes'),({'nombre':'Seleccionado'},'psel')])
def test_filtros_principales(client,seed,params,key):
    params={k:(seed['s1'] if k=='solicitud_id' else seed['cargo'] if k=='cargo_id' else seed['skill'] if k=='habilidad_id' else seed['post_states']['Seleccionado'] if k=='estado_postulacion_id' else seed['disp'] if k=='disponibilidad_id' else v) for k,v in params.items()}
    r=client.get('/informes/candidatos',params=params,headers=H(seed['reporter'])); assert r.status_code==200,r.text; assert seed[key] in _ids(r)
def test_filtro_segunda_solicitud(client,seed):
    r=client.get('/informes/candidatos',params={'solicitud_id':seed['s2']},headers=H(seed['reporter'])); assert _ids(r)=={seed['psecond']}
def test_match_min_mayor_max_422(client,seed): assert client.get('/informes/candidatos',params={'match_min':90,'match_max':50},headers=H(seed['reporter'])).status_code==422
def test_clasificacion_invalida_422(client,seed): assert client.get('/informes/candidatos',params={'clasificacion':'OTRO'},headers=H(seed['reporter'])).status_code==422
def test_paginacion(client,seed):
    r=client.get('/informes/candidatos',params={'skip':0,'limit':2},headers=H(seed['reporter'])); assert r.status_code==200 and len(r.json()['items'])==2 and r.json()['total']>=2

# ---------------- Categorías ----------------
def test_listar_categorias(client,seed):
    b=client.get('/informes/catalogos/categorias-habilidad',headers=H(seed['reporter'])).json(); assert any(x['nombre']=='Lenguajes' for x in b)
def test_asignar_categoria(client,seed):
    r=client.patch(f"/informes/catalogos/habilidades/{seed['skill']}/categoria",json={'categoria_id':seed['cat_db']},headers=H(seed['catalog'])); assert r.status_code==200 and r.json()['categoria_id']==seed['cat_db']
def test_quitar_categoria(client,seed): assert client.patch(f"/informes/catalogos/habilidades/{seed['skill']}/categoria",json={'categoria_id':None},headers=H(seed['catalog'])).status_code==200
def test_habilidad_inexistente_404(client,seed): assert client.patch('/informes/catalogos/habilidades/999999/categoria',json={'categoria_id':seed['cat_db']},headers=H(seed['catalog'])).status_code==404
def test_categoria_inexistente_422(client,seed): assert client.patch(f"/informes/catalogos/habilidades/{seed['skill']}/categoria",json={'categoria_id':999999},headers=H(seed['catalog'])).status_code==422

# ---------------- Idiomas ----------------
def test_listar_idiomas(client,seed): assert len(client.get('/informes/catalogos/idiomas',headers=H(seed['reporter'])).json())>=2
def test_get_idiomas_candidato(client,seed):
    r=client.get(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",headers=H(seed['canview'])); assert r.status_code==200 and r.json()[0]['nivel']=='Nativo'
def test_reemplazar_idiomas(client, seed):
    payload = {
        "idiomas": [
            {
                "idioma_id": seed["lang_en"],
                "nivel": "Avanzado",
            }
        ]
    }

    response = client.put(
        f"/informes/candidatos-perfil/{seed['csel']}/idiomas",
        json=payload,
        headers=H(seed["canupdate"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    idioma = data[0]

    assert idioma["idioma_id"] == seed["lang_en"]
    assert idioma["idioma"] == "Inglés"
    assert idioma["nivel"] == "Avanzado"

    # Migración 008: nivel normalizado
    assert idioma["nivel_codigo"] == "AVA"
    assert idioma["nivel_grupo"] == "Avanzado"
    assert isinstance(idioma["nivel_idioma_id"], int)
    assert idioma["nivel_idioma_id"] > 0
def test_reemplazar_idiomas_con_nivel_normalizado(client, seed):
    # Buscar nivel C1
    niveles = client.get(
        "/catalogos/niveles-idioma",
        headers=H(seed["canupdate"]),
    )

    assert niveles.status_code == 200

    c1 = next(
        item
        for item in niveles.json()
        if item["nvid_codigo"] == "C1"
    )

    payload = {
        "idiomas": [
            {
                "idioma_id": seed["lang_en"],
                "nivel_idioma_id": c1["nvid_id"],
            }
        ]
    }

    response = client.put(
        f"/informes/candidatos-perfil/{seed['csel']}/idiomas",
        json=payload,
        headers=H(seed["canupdate"]),
    )

    assert response.status_code == 200

    idioma = response.json()[0]

    assert idioma["idioma_id"] == seed["lang_en"]
    assert idioma["nivel_idioma_id"] == c1["nvid_id"]
    assert idioma["nivel_codigo"] == "C1"
    assert idioma["nivel"] == "Avanzado C1"
    assert idioma["nivel_grupo"] == "Avanzado"
def test_reemplazar_idiomas_vacio(client,seed): assert client.put(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",json={'idiomas':[]},headers=H(seed['canupdate'])).status_code==200
def test_idioma_duplicado_422(client,seed):
    p={'idiomas':[{'idioma_id':seed['lang_en'],'nivel':'Avanzado'},{'idioma_id':seed['lang_en'],'nivel':'Nativo'}]}; assert client.put(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",json=p,headers=H(seed['canupdate'])).status_code==422
def test_idioma_inexistente_422(client,seed): assert client.put(f"/informes/candidatos-perfil/{seed['csel']}/idiomas",json={'idiomas':[{'idioma_id':999999,'nivel':'Avanzado'}]},headers=H(seed['canupdate'])).status_code==422
def test_candidato_idioma_inexistente_404(client,seed): assert client.get('/informes/candidatos-perfil/999999/idiomas',headers=H(seed['canview'])).status_code==404

# ---------------- PDF resumen / documentos ----------------
def test_generar_resumen_cualquier_clasificacion(client,seed):
    for key in ['psel','pdes','prev']:
        r=client.post(f"/informes/candidatos/{seed[key]}/resumen",headers=H(seed['reporter'])); assert r.status_code==201,r.text; assert r.json()['tipo_documento']=='RESUMEN'; assert len(r.json()['hash_sha256'])==64

def test_resumen_pdf_valido_y_con_texto(client,seed):
    d=client.post(f"/informes/candidatos/{seed['psel']}/resumen",headers=H(seed['reporter'])).json(); rr=client.get(f"/informes/documentos/{d['documento_id']}/descargar",headers=H(seed['reporter'])); assert rr.status_code==200 and rr.content.startswith(b'%PDF'); txt=''.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(rr.content)).pages); assert 'RESUMEN DE CANDIDATO' in txt and 'Seleccionado' in txt

def test_documento_list_get_filters(client,seed):
    d=client.post(f"/informes/candidatos/{seed['psel']}/resumen",headers=H(seed['reporter'])).json(); assert client.get(f"/informes/documentos/{d['documento_id']}",headers=H(seed['reporter'])).status_code==200; b=client.get('/informes/documentos',params={'solicitud_candidato_id':seed['psel'],'tipo':'RESUMEN'},headers=H(seed['reporter'])).json(); assert any(x['documento_id']==d['documento_id'] for x in b)
def test_documento_inexistente_404(client,seed): assert client.get('/informes/documentos/999999',headers=H(seed['reporter'])).status_code==404

def test_integridad_documento_detecta_tamper(client,seed):
    d=client.post(f"/informes/candidatos/{seed['psel']}/resumen",headers=H(seed['reporter'])).json(); db=TestingSessionLocal(); obj=db.get(im.DocumentoReporteCandidato,d['documento_id']); Path(obj.drcp_ruta_archivo).write_bytes(b'alterado'); db.close(); assert client.get(f"/informes/documentos/{d['documento_id']}/descargar",headers=H(seed['reporter'])).status_code==409

def test_documento_archivo_faltante_404(client,seed):
    d=client.post(f"/informes/candidatos/{seed['psel']}/resumen",headers=H(seed['reporter'])).json(); db=TestingSessionLocal(); obj=db.get(im.DocumentoReporteCandidato,d['documento_id']); Path(obj.drcp_ruta_archivo).unlink(); db.close(); assert client.get(f"/informes/documentos/{d['documento_id']}/descargar",headers=H(seed['reporter'])).status_code==404

def test_documento_ruta_fuera_storage_409(client,seed,tmp_path):
    d=client.post(f"/informes/candidatos/{seed['psel']}/resumen",headers=H(seed['reporter'])).json(); outside=tmp_path/'outside.pdf'; outside.write_bytes(b'%PDF fake'); db=TestingSessionLocal(); obj=db.get(im.DocumentoReporteCandidato,d['documento_id']); obj.drcp_ruta_archivo=str(outside.resolve()); obj.drcp_hash_sha256=hashlib.sha256(outside.read_bytes()).hexdigest(); db.commit(); db.close(); assert client.get(f"/informes/documentos/{d['documento_id']}/descargar",headers=H(seed['reporter'])).status_code==409

# ---------------- CV corporativo ----------------
@pytest.mark.parametrize('key',['psel','pcon','ppass'])
def test_cv_solo_aprobados(client,seed,key): assert client.post(f"/informes/candidatos/{seed[key]}/cv-corporativo",json={},headers=H(seed['reporter'])).status_code==201
@pytest.mark.parametrize('key',['pdes','prev','pfailt','ppendt'])
def test_cv_no_aprobados_o_pendientes_409(client,seed,key): assert client.post(f"/informes/candidatos/{seed[key]}/cv-corporativo",json={},headers=H(seed['reporter'])).status_code==409

def test_cv_pdf_contiene_perfil_corporativo(client,seed):
    d=client.post(f"/informes/candidatos/{seed['psel']}/cv-corporativo",json={'resumen_ejecutivo':'Resumen QA especial','roles_recomendados':['Arquitecto Backend'],'fortalezas':['Python avanzado']},headers=H(seed['reporter'])).json(); rr=client.get(f"/informes/documentos/{d['documento_id']}/descargar",headers=H(seed['reporter'])); txt=''.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(rr.content)).pages); assert 'INFORMACIÓN ACADÉMICA' in txt and 'EXPERIENCIA LABORAL' in txt and 'Resumen QA especial' in txt and 'Arquitecto Backend' in txt

# ---------------- Masivos / ZIP ----------------
def test_resumen_masivo(client,seed):
    p={'solicitud_candidato_ids':[seed['psel'],seed['pdes'],seed['prev']]}; r=client.post('/informes/candidatos/resumen-masivo',json=p,headers=H(seed['reporter'])); assert r.status_code==201 and r.json()['cantidad']==3

def test_cv_masivo_aprobados(client,seed):
    p={'solicitud_candidato_ids':[seed['psel'],seed['pcon'],seed['ppass']]}; r=client.post('/informes/candidatos/cv-corporativo-masivo',json=p,headers=H(seed['reporter'])); assert r.status_code==201 and r.json()['cantidad']==3

def test_cv_masivo_con_no_aprobado_es_atomico(client,seed):
    db=TestingSessionLocal(); before=db.query(im.DocumentoReporteCandidato).count(); db.close(); p={'solicitud_candidato_ids':[seed['psel'],seed['pdes']]}; r=client.post('/informes/candidatos/cv-corporativo-masivo',json=p,headers=H(seed['reporter'])); assert r.status_code==409; db=TestingSessionLocal(); after=db.query(im.DocumentoReporteCandidato).count(); db.close(); assert after==before

def test_masivo_ids_vacios_422(client,seed): assert client.post('/informes/candidatos/resumen-masivo',json={'solicitud_candidato_ids':[]},headers=H(seed['reporter'])).status_code==422
def test_masivo_ids_duplicados_422(client,seed): assert client.post('/informes/candidatos/resumen-masivo',json={'solicitud_candidato_ids':[seed['psel'],seed['psel']]},headers=H(seed['reporter'])).status_code==422

def test_descarga_zip_resumen(client,seed):
    r=client.post('/informes/candidatos/resumen-masivo/descargar',json={'solicitud_candidato_ids':[seed['psel'],seed['pdes']]},headers=H(seed['reporter'])); assert r.status_code==200; z=zipfile.ZipFile(io.BytesIO(r.content)); assert len(z.namelist())==2 and all(x.endswith('.pdf') for x in z.namelist())
def test_descarga_zip_cv(client,seed):
    r=client.post('/informes/candidatos/cv-corporativo-masivo/descargar',json={'solicitud_candidato_ids':[seed['psel'],seed['pcon']]},headers=H(seed['reporter'])); assert r.status_code==200; z=zipfile.ZipFile(io.BytesIO(r.content)); assert len(z.namelist())==2

# ---------------- Directivos ----------------
def test_preparar_directivos_default(client,seed):
    p={'solicitud_candidato_ids':[seed['psel'],seed['pcon']],'destinatarios':['director@example.com'],'cc':['cc@example.com']}; r=client.post('/informes/directivos/preparar',json=p,headers=H(seed['reporter'])); assert r.status_code==200,r.text; b=r.json(); assert len(b['candidatos'])==2 and len(b['adjuntos'])==2 and 'Backend' in b['asunto']
def test_preparar_directivos_custom(client,seed):
    p={'solicitud_candidato_ids':[seed['psel']],'destinatarios':['director@example.com'],'cc':[],'asunto':'Asunto editado','cuerpo':'Cuerpo editado'}; b=client.post('/informes/directivos/preparar',json=p,headers=H(seed['reporter'])).json(); assert b['asunto']=='Asunto editado' and b['cuerpo']=='Cuerpo editado'
def test_preparar_directivos_no_aprobado_409(client,seed):
    p={'solicitud_candidato_ids':[seed['pdes']],'destinatarios':['director@example.com'],'cc':[]}; assert client.post('/informes/directivos/preparar',json=p,headers=H(seed['reporter'])).status_code==409
def test_directivos_email_invalido_422(client,seed):
    p={'solicitud_candidato_ids':[seed['psel']],'destinatarios':['invalido'],'cc':[]}; assert client.post('/informes/directivos/preparar',json=p,headers=H(seed['reporter'])).status_code==422

def test_enviar_directivos_exito_registra_por_candidato(client,seed,monkeypatch):
    sent={}; monkeypatch.setattr(services,'send_email',lambda **kw: sent.update(kw)); p={'solicitud_candidato_ids':[seed['psel'],seed['pcon']],'destinatarios':['director@example.com'],'cc':['cc@example.com'],'asunto':'QA','cuerpo':'QA'}; r=client.post('/informes/directivos/enviar',json=p,headers=H(seed['reporter'])); assert r.status_code==200,r.text; assert len(r.json())==2 and all(x['estado']=='ENVIADO' for x in r.json()); assert len(sent['attachments'])==2

def test_enviar_directivos_error_smtp_502_y_traza(client,seed,monkeypatch):
    def boom(**kw): raise EmailDeliveryError('SMTP QA')
    monkeypatch.setattr(services,'send_email',boom); p={'solicitud_candidato_ids':[seed['psel']],'destinatarios':['director@example.com'],'cc':[],'asunto':'QA','cuerpo':'QA'}; r=client.post('/informes/directivos/enviar',json=p,headers=H(seed['reporter'])); assert r.status_code==502; rows=client.get('/informes/notificaciones',params={'tipo':'DIRECTIVOS','estado':'ERROR'},headers=H(seed['reporter'])).json(); assert rows and rows[0]['error']

# ---------------- Rechazo / agradecimiento ----------------
@pytest.mark.parametrize('key',['pdes','pinh'])
def test_preparar_rechazo_estados_formales(client,seed,key):
    p={'solicitud_candidato_ids':[seed[key]],'tipo':'RECHAZO'}; r=client.post('/informes/rechazos/preparar',json=p,headers=H(seed['reporter'])); assert r.status_code==200; b=r.json()['items'][0]; assert 'Backend Senior' in b['asunto'] and 'cand' in b['destinatario']
@pytest.mark.parametrize('key',['psel','pfailt','prev'])
def test_no_permite_rechazo_sin_estado_m3_formal(client,seed,key):
    p={'solicitud_candidato_ids':[seed[key]],'tipo':'RECHAZO'}; assert client.post('/informes/rechazos/preparar',json=p,headers=H(seed['reporter'])).status_code==409

def test_preparar_agradecimiento_custom(client,seed):
    p={'solicitud_candidato_ids':[seed['pdes']],'tipo':'AGRADECIMIENTO','asunto_plantilla':'Hola {nombre}','cuerpo_plantilla':'Cargo {cargo} / {codigo_solicitud}'}; b=client.post('/informes/rechazos/preparar',json=p,headers=H(seed['reporter'])).json()['items'][0]; assert 'Descartado' in b['asunto'] and 'SOL-M60001' in b['cuerpo']
def test_tipo_rechazo_invalido_422(client,seed): assert client.post('/informes/rechazos/preparar',json={'solicitud_candidato_ids':[seed['pdes']],'tipo':'OTRO'},headers=H(seed['reporter'])).status_code==422

def test_enviar_rechazo_exito(client,seed,monkeypatch):
    monkeypatch.setattr(services,'send_email',lambda **kw: None); p={'items':[{'tipo':'RECHAZO','solicitud_candidato_id':seed['pdes'],'asunto':'Cierre QA','cuerpo':'Gracias'}]}; r=client.post('/informes/rechazos/enviar',json=p,headers=H(seed['reporter'])); assert r.status_code==200 and r.json()[0]['estado']=='ENVIADO'
def test_enviar_rechazo_error_devuelve_error_y_traza(client,seed,monkeypatch):
    monkeypatch.setattr(services,'send_email',lambda **kw: (_ for _ in ()).throw(EmailDeliveryError('SMTP'))); p={'items':[{'tipo':'RECHAZO','solicitud_candidato_id':seed['pdes'],'asunto':'Cierre QA','cuerpo':'Gracias'}]}; r=client.post('/informes/rechazos/enviar',json=p,headers=H(seed['reporter'])); assert r.status_code==200 and r.json()[0]['estado']=='ERROR' and r.json()[0]['error']
def test_enviar_rechazo_candidato_no_formal_409(client,seed,monkeypatch):
    monkeypatch.setattr(services,'send_email',lambda **kw: None); p={'items':[{'tipo':'RECHAZO','solicitud_candidato_id':seed['pfailt'],'asunto':'Cierre QA','cuerpo':'Gracias'}]}; assert client.post('/informes/rechazos/enviar',json=p,headers=H(seed['reporter'])).status_code==409
def test_rechazo_items_duplicados_422(client,seed):
    x={'tipo':'RECHAZO','solicitud_candidato_id':seed['pdes'],'asunto':'A','cuerpo':'B'}; assert client.post('/informes/rechazos/enviar',json={'items':[x,x]},headers=H(seed['reporter'])).status_code==422

# ---------------- Notificaciones ----------------
def test_notificaciones_listado_filtros_y_detalle(client,seed,monkeypatch):
    monkeypatch.setattr(services,'send_email',lambda **kw: None); p={'items':[{'tipo':'RECHAZO','solicitud_candidato_id':seed['pdes'],'asunto':'QA','cuerpo':'QA cuerpo'}]}; row=client.post('/informes/rechazos/enviar',json=p,headers=H(seed['reporter'])).json()[0]; r=client.get('/informes/notificaciones',params={'solicitud_candidato_id':seed['pdes'],'tipo':'RECHAZO','estado':'ENVIADO'},headers=H(seed['reporter'])); assert any(x['notificacion_id']==row['notificacion_id'] for x in r.json()); d=client.get(f"/informes/notificaciones/{row['notificacion_id']}",headers=H(seed['reporter'])); assert d.status_code==200 and d.json()['cuerpo']=='QA cuerpo'
def test_notificacion_inexistente_404(client,seed): assert client.get('/informes/notificaciones/999999',headers=H(seed['reporter'])).status_code==404

# ---------------- Plantillas ----------------
def test_listar_plantillas(client,seed):
    b=client.get('/informes/plantillas',headers=H(seed['reporter'])).json(); assert {x['tipo'] for x in b}=={'RECHAZO','AGRADECIMIENTO','DIRECTIVOS'}
def test_editar_plantilla_y_auditoria(client,seed):
    b=client.get('/informes/plantillas',headers=H(seed['reporter'])).json(); pid=next(x['plantilla_id'] for x in b if x['tipo']=='RECHAZO'); r=client.patch(f"/informes/plantillas/{pid}",json={'asunto':'Nuevo asunto {cargo}'},headers=H(seed['reporter'])); assert r.status_code==200 and r.json()['asunto'].startswith('Nuevo'); db=TestingSessionLocal(); obj=db.get(im.PlantillaNotificacion,pid); assert obj.plnt_usuario_actualizacion_id==seed['reporter']; db.close()
def test_patch_plantilla_vacio_422(client,seed):
    pid=client.get('/informes/plantillas',headers=H(seed['reporter'])).json()[0]['plantilla_id']; assert client.patch(f"/informes/plantillas/{pid}",json={},headers=H(seed['reporter'])).status_code==422
def test_plantilla_inexistente_404(client,seed): assert client.patch('/informes/plantillas/999999',json={'asunto':'X'},headers=H(seed['reporter'])).status_code==404
def test_plantilla_inactiva_bloquea_preparacion(client,seed):
    b=client.get('/informes/plantillas',headers=H(seed['reporter'])).json(); pid=next(x['plantilla_id'] for x in b if x['tipo']=='RECHAZO'); client.patch(f"/informes/plantillas/{pid}",json={'activa':False},headers=H(seed['reporter'])); assert client.post('/informes/rechazos/preparar',json={'solicitud_candidato_ids':[seed['pdes']],'tipo':'RECHAZO'},headers=H(seed['reporter'])).status_code==409

# ---------------- Contrato estricto ----------------
def test_extra_field_listado_documento_payload_422(client,seed): assert client.post('/informes/candidatos/resumen-masivo',json={'solicitud_candidato_ids':[seed['psel']],'hack':1},headers=H(seed['reporter'])).status_code==422
def test_cv_override_extra_field_422(client,seed): assert client.post(f"/informes/candidatos/{seed['psel']}/cv-corporativo",json={'hack':1},headers=H(seed['reporter'])).status_code==422
