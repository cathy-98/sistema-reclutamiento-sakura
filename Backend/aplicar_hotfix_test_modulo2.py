
from pathlib import Path

path = Path("test/test_modulo2.py")
text = path.read_text(encoding="utf-8")

old = """    catalog_models.TipoContrato.__table__,
    catalog_models.Habilidad.__table__,
    catalog_models.NivelHabilidad.__table__,
"""

new = """    catalog_models.TipoContrato.__table__,
    catalog_models.CategoriaHabilidad.__table__,
    catalog_models.Habilidad.__table__,
    catalog_models.NivelHabilidad.__table__,
"""

if old not in text:
    raise SystemExit(
        "No se encontró el bloque esperado en test/test_modulo2.py. "
        "Verifica que estés usando la versión actual del test."
    )

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("OK: test/test_modulo2.py actualizado con tbl_categoria_habilidad")
