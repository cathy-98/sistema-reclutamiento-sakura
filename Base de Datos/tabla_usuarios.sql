-- public.usuarios definition

-- Drop table

-- DROP TABLE public.usuarios;

CREATE TABLE public.usuarios (
	id serial4 NOT NULL,
	usuario varchar(50) NOT NULL,
	contrasena varchar(255) NOT NULL,
	email varchar(100) NOT NULL,
	rol varchar(30) NOT NULL,
	CONSTRAINT usuarios_email_key UNIQUE (email),
	CONSTRAINT usuarios_pkey PRIMARY KEY (id),
	CONSTRAINT usuarios_usuario_key UNIQUE (usuario)
);
CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);