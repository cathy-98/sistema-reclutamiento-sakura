from __future__ import annotations
import io, os, sys, uuid, zipfile
import requests
from pypdf import PdfReader

BASE=os.getenv('SAKURA_API_URL','http://127.0.0.1:8000').rstrip('/')
ADMIN_EMAIL=os.getenv('QA_ADMIN_EMAIL','').strip(); ADMIN_PASSWORD=os.getenv('QA_ADMIN_PASSWORD','').strip()
APPROVED=int(os.getenv('QA_M6_APPROVED_SLCD_ID','0') or 0); APPROVED2=int(os.getenv('QA_M6_SECOND_APPROVED_SLCD_ID','0') or 0); REJECTED=int(os.getenv('QA_M6_REJECTED_SLCD_ID','0') or 0)
DIRECTOR=os.getenv('QA_M6_DIRECTOR_EMAIL','').strip(); SEND_EMAIL=os.getenv('QA_M6_SEND_EMAIL','0').strip().lower() in {'1','true','yes','si'}
TIMEOUT=30; RUN=uuid.uuid4().hex[:8]; PASSED=0
class QAError(RuntimeError): pass

def call(method,path,expected=(200,),token=None,**kw):
    h=dict(kw.pop('headers',{}));
    if token: h['Authorization']=f'Bearer {token}'
    r=requests.request(method,BASE+path,headers=h,timeout=TIMEOUT,**kw)
    if r.status_code not in expected: raise QAError(f'{method} {path}: esperado {expected}, recibido {r.status_code}. Body={r.text[:1600]}')
    return r

def ok(msg):
    global PASSED; PASSED+=1; print(f'[PASS {PASSED:02d}] {msg}')

def login():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD: raise QAError('Defina QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD')
    b=call('POST','/auth/login',(200,),json={'email':ADMIN_EMAIL,'password':ADMIN_PASSWORD}).json(); return b['access_token']

def run():
    print('Sakura Módulo 6 - QA LIVE COMPLETO'); print('API=',BASE,' RUN=',RUN)
    spec=call('GET','/openapi.json',(200,)).json(); paths=spec.get('paths',{}); required=['/informes/candidatos','/informes/directivos/preparar','/informes/rechazos/preparar','/informes/plantillas','/catalogos/categorias-habilidad','/catalogos/idiomas','/catalogos/habilidades'];
    if not all(x in paths for x in required): raise QAError('OpenAPI no registra todas las rutas M6')
    ok('OpenAPI registra M6')
    token=login(); ok('Login admin')
    call('GET','/informes/candidatos',(401,)); ok('M6 sin token -> 401')
    # Catálogos canónicos M0/M6. Los aliases /informes/catalogos se mantienen por compatibilidad.
    cats=call('GET','/catalogos/categorias-habilidad',(200,),token=token).json()
    langs=call('GET','/catalogos/idiomas',(200,),token=token).json()
    if not cats or not langs: raise QAError('Catálogos canónicos de categorías/idiomas vacíos')
    ok('Catálogos canónicos categorías e idiomas')

    legacy_cats=call('GET','/informes/catalogos/categorias-habilidad',(200,),token=token).json()
    legacy_langs=call('GET','/informes/catalogos/idiomas',(200,),token=token).json()
    if len(legacy_cats) != len(cats) or len(legacy_langs) != len(langs):
        raise QAError('Aliases M6 no son consistentes con catálogos canónicos')
    ok('Aliases M6 de catálogos compatibles')

    skills=call('GET','/catalogos/habilidades',(200,),token=token,params={'limit':500}).json()
    categorized=next((x for x in skills if x.get('hab_categoria_habilidad_id')),None)
    if not categorized:
        raise QAError('No existe ninguna habilidad con categoría asignada')
    if not categorized.get('categoria') or categorized['categoria'].get('cthb_id') != categorized['hab_categoria_habilidad_id']:
        raise QAError('Habilidad no expone correctamente la categoría anidada')
    filtered=call('GET','/catalogos/habilidades',(200,),token=token,params={'categoria_id':categorized['hab_categoria_habilidad_id'],'limit':500}).json()
    if not any(x['hab_id']==categorized['hab_id'] for x in filtered):
        raise QAError('Filtro de habilidades por categoría no retornó la habilidad esperada')
    if any(x.get('hab_categoria_habilidad_id') != categorized['hab_categoria_habilidad_id'] for x in filtered):
        raise QAError('Filtro de habilidades por categoría retornó registros de otra categoría')
    ok('Habilidades exponen categoría y filtran por categoria_id')
    templates=call('GET','/informes/plantillas',(200,),token=token).json();
    if {x['tipo'] for x in templates}!={'RECHAZO','AGRADECIMIENTO','DIRECTIVOS'}: raise QAError('Plantillas M6 incompletas')
    ok('Plantillas M6')
    listing=call('GET','/informes/candidatos',(200,),token=token,params={'limit':200}).json(); ok('Listado candidatos M6')
    # Validaciones de contrato
    call('GET','/informes/candidatos',(422,),token=token,params={'match_min':90,'match_max':10}); ok('match_min > match_max -> 422')
    call('POST','/informes/candidatos/resumen-masivo',(422,),token=token,json={'solicitud_candidato_ids':[]}); ok('Masivo vacío -> 422')
    if not APPROVED or not REJECTED: raise QAError('Defina QA_M6_APPROVED_SLCD_ID y QA_M6_REJECTED_SLCD_ID con postulaciones QA')
    a=call('GET',f'/informes/candidatos/{APPROVED}',(200,),token=token).json();
    if a['clasificacion']!='APROBADO': raise QAError(f'QA_M6_APPROVED_SLCD_ID no está aprobado: {a}')
    ok('Candidato aprobado confirmado')
    n=call('GET',f'/informes/candidatos/{REJECTED}',(200,),token=token).json();
    if not n['puede_enviar_rechazo']: raise QAError('QA_M6_REJECTED_SLCD_ID debe estar Descartado/Inhabilitado')
    ok('Candidato rechazado formal confirmado')
    # Resumen PDF
    d=call('POST',f'/informes/candidatos/{APPROVED}/resumen',(201,),token=token).json(); pdf=call('GET',f"/informes/documentos/{d['documento_id']}/descargar",(200,),token=token).content
    if not pdf.startswith(b'%PDF'): raise QAError('Resumen no es PDF')
    txt=''.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(pdf)).pages)
    if 'RESUMEN DE CANDIDATO' not in txt: raise QAError('Resumen PDF sin contenido esperado')
    ok('Resumen PDF + descarga + texto')
    # CV
    cv=call('POST',f'/informes/candidatos/{APPROVED}/cv-corporativo',(201,),token=token,json={'resumen_ejecutivo':f'QA LIVE {RUN}'}).json(); raw=call('GET',f"/informes/documentos/{cv['documento_id']}/descargar",(200,),token=token).content
    if not raw.startswith(b'%PDF'): raise QAError('CV no es PDF')
    tx=''.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(raw)).pages)
    if 'INFORMACIÓN ACADÉMICA' not in tx or f'QA LIVE {RUN}' not in tx: raise QAError('CV no contiene estructura/override')
    ok('CV corporativo PDF')
    call('POST',f'/informes/candidatos/{REJECTED}/cv-corporativo',(409,),token=token,json={}); ok('CV corporativo rechazado -> 409')
    # Masivos
    ids=[APPROVED] + ([APPROVED2] if APPROVED2 else [])
    zr=call('POST','/informes/candidatos/cv-corporativo-masivo/descargar',(200,),token=token,json={'solicitud_candidato_ids':ids}); z=zipfile.ZipFile(io.BytesIO(zr.content));
    if len(z.namelist())!=len(ids): raise QAError('ZIP CV masivo cantidad incorrecta')
    ok('ZIP CV corporativo masivo')
    zr=call('POST','/informes/candidatos/resumen-masivo/descargar',(200,),token=token,json={'solicitud_candidato_ids':[APPROVED,REJECTED]}); z=zipfile.ZipFile(io.BytesIO(zr.content));
    if len(z.namelist())!=2: raise QAError('ZIP resumen masivo cantidad incorrecta')
    ok('ZIP resumen masivo')
    # Directivos prepare
    recipient=DIRECTOR or 'qa-directivo@example.com'; prev=call('POST','/informes/directivos/preparar',(200,),token=token,json={'solicitud_candidato_ids':ids,'destinatarios':[recipient],'cc':[],'asunto':f'QA M6 {RUN}','cuerpo':'QA LIVE'}).json();
    if len(prev['adjuntos'])!=len(ids): raise QAError('Preview directivos no adjuntó todos los CV')
    ok('Preparar directivos + adjuntos')
    call('POST','/informes/directivos/preparar',(409,),token=token,json={'solicitud_candidato_ids':[REJECTED],'destinatarios':[recipient],'cc':[]}); ok('Directivos solo aprobados -> 409')
    # Rechazo prepare
    rp=call('POST','/informes/rechazos/preparar',(200,),token=token,json={'solicitud_candidato_ids':[REJECTED],'tipo':'RECHAZO','asunto_plantilla':'QA {nombre}','cuerpo_plantilla':'Solicitud {codigo_solicitud}'}).json();
    if not rp['items'] or '{nombre}' in rp['items'][0]['asunto']: raise QAError('Variables no renderizadas')
    ok('Preparar rechazo editable')
    call('POST','/informes/rechazos/preparar',(409,),token=token,json={'solicitud_candidato_ids':[APPROVED],'tipo':'RECHAZO'}); ok('Rechazo a aprobado -> 409')
    # Documentos/trazabilidad
    docs=call('GET','/informes/documentos',(200,),token=token,params={'solicitud_candidato_id':APPROVED}).json();
    if not docs: raise QAError('No hay trazabilidad documental')
    ok('Trazabilidad documentos')
    # Plantilla: editar y restaurar
    rechazo=next(x for x in templates if x['tipo']=='RECHAZO'); original=rechazo['nombre']; call('PATCH',f"/informes/plantillas/{rechazo['plantilla_id']}",(200,),token=token,json={'nombre':original+' QA'}); call('PATCH',f"/informes/plantillas/{rechazo['plantilla_id']}",(200,),token=token,json={'nombre':original}); ok('Editar/restaurar plantilla')
    if SEND_EMAIL:
        if not DIRECTOR: raise QAError('QA_M6_SEND_EMAIL=1 requiere QA_M6_DIRECTOR_EMAIL')
        rows=call('POST','/informes/directivos/enviar',(200,),token=token,json={'solicitud_candidato_ids':[APPROVED],'destinatarios':[DIRECTOR],'cc':[],'asunto':f'QA M6 {RUN}','cuerpo':'Correo QA LIVE'}).json();
        if not rows or rows[0]['estado']!='ENVIADO': raise QAError(f'Envío directivos no exitoso: {rows}')
        ok('SMTP real directivos + trazabilidad')
        item=rp['items'][0]; rows=call('POST','/informes/rechazos/enviar',(200,),token=token,json={'items':[{'tipo':'RECHAZO','solicitud_candidato_id':REJECTED,'asunto':item['asunto'],'cuerpo':item['cuerpo']}]}).json();
        if not rows or rows[0]['estado']!='ENVIADO': raise QAError(f'Envío rechazo no exitoso: {rows}')
        ok('SMTP real rechazo + trazabilidad')
    else:
        print('[INFO] SMTP real no ejecutado. Para cobertura LIVE completa use QA_M6_SEND_EMAIL=1 y cuentas QA.')
    print(f'\nRESULTADO: PASSED ({PASSED} casos LIVE)')

if __name__=='__main__':
    try: run()
    except (QAError,requests.RequestException,zipfile.BadZipFile) as e: print('\nRESULTADO: FAILED'); print(e); sys.exit(1)
