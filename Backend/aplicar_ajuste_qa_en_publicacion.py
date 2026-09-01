from pathlib import Path

# No modifica código productivo. Actualiza solamente referencias del estado de SOLICITUD
# en suites QA/LIVE. Se evita un reemplazo global del repositorio porque la frase
# "en curso" también se usa en otros módulos con otro significado.
FILES = [
    Path('test/test_modulo2.py'),
    Path('test/test_modulo3.py'),
    Path('test/test_modulo3_completo.py'),
    Path('test/test_modulo5_completo.py'),
    Path('test/modulo6_test_support.py'),
    Path('live/test_modulo2_live.py'),
    Path('live/test_modulo3_live.py'),
    Path('live/test_modulo3_live_completo.py'),
]

changed = []
missing = []
for path in FILES:
    if not path.exists():
        missing.append(str(path))
        continue
    text = path.read_text(encoding='utf-8')
    new = text.replace('En Curso', 'En Publicacion')
    if new != text:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path))

print('Archivos QA/LIVE actualizados:')
for item in changed:
    print('  OK ', item)
if missing:
    print('\nArchivos no presentes en esta instalación (se omiten):')
    for item in missing:
        print('  -- ', item)
print('\nIMPORTANTE: no se hizo reemplazo dentro de app/cuestionarios/services.py,')
print('porque allí "en curso" describe el estado de una evaluación, no el estado de solicitud.')
