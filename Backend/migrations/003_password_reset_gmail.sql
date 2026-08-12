BEGIN;

CREATE TABLE IF NOT EXISTS public.tbl_password_reset_token (
    prst_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prst_usuario_id integer NOT NULL,
    prst_token_hash character varying(64) NOT NULL,
    prst_fecha_creacion timestamp with time zone NOT NULL DEFAULT now(),
    prst_fecha_expiracion timestamp with time zone NOT NULL,
    prst_fecha_uso timestamp with time zone,
    prst_fecha_revocacion timestamp with time zone,

    CONSTRAINT uq_tbl_password_reset_token_hash UNIQUE (prst_token_hash),
    CONSTRAINT fk_tbl_password_reset_token_usuario
        FOREIGN KEY (prst_usuario_id)
        REFERENCES public.tbl_usuario(usr_id)
);

CREATE INDEX IF NOT EXISTS ix_password_reset_usuario
    ON public.tbl_password_reset_token (prst_usuario_id);

CREATE INDEX IF NOT EXISTS ix_password_reset_expiracion
    ON public.tbl_password_reset_token (prst_fecha_expiracion);

COMMIT;
