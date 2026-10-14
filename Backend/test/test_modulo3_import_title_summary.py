from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.catalogos import models as catalog_models  # noqa: F401
from app.candidatos import models as candidate_models  # noqa: F401
from app.candidatos import schemas, services
from app.clientes import models as cliente_models  # noqa: F401
from app.database import Base
from app.solicitudes import models as solicitud_models  # noqa: F401
from app.usuarios import models as user_models


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    db.add(user_models.EstadoUsuario(esusr_nombre="Activo", esusr_descripcion="Activo"))
    db.commit()
    return db


def _payload(**overrides):
    base = {
        "cand_email": "titulo.resumen.qa@sakura.cl",
        "cand_nombres": "Catherine",
        "cand_apellido_paterno": "Rebolledo",
        "cand_apellido_materno": None,
        "cand_telefono": "957034447",
        "cand_titulo": None,
        "cand_resumen_profesional": None,
    }
    base.update(overrides)
    return schemas.CandidatoCreate(**base)


def test_create_candidate_persiste_titulo_detectado():
    db = _session()
    try:
        created, _password = services.create_candidate(
            db,
            _payload(cand_titulo="UX/UI Designer con enfoque en Frontend"),
        )

        persisted = services.get_candidate(db, created.cand_id)

        assert persisted.cand_titulo == "UX/UI Designer con enfoque en Frontend"
    finally:
        db.close()


def test_create_candidate_persiste_resumen_detectado():
    db = _session()
    try:
        created, _password = services.create_candidate(
            db,
            _payload(
                cand_email="resumen.qa@sakura.cl",
                cand_resumen_profesional="Diseñadora UX/UI con experiencia en productos digitales.",
            ),
        )

        persisted = services.get_candidate(db, created.cand_id)

        assert persisted.cand_resumen_profesional == "Diseñadora UX/UI con experiencia en productos digitales."
    finally:
        db.close()


def test_create_candidate_mantiene_titulo_none_si_parser_no_detecta():
    db = _session()
    try:
        created, _password = services.create_candidate(
            db,
            _payload(cand_email="sin.titulo.qa@sakura.cl", cand_titulo=None),
        )

        persisted = services.get_candidate(db, created.cand_id)

        assert persisted.cand_titulo is None
    finally:
        db.close()


def test_create_candidate_mantiene_resumen_none_si_parser_no_detecta():
    db = _session()
    try:
        created, _password = services.create_candidate(
            db,
            _payload(cand_email="sin.resumen.qa@sakura.cl", cand_resumen_profesional=None),
        )

        persisted = services.get_candidate(db, created.cand_id)

        assert persisted.cand_resumen_profesional is None
    finally:
        db.close()
