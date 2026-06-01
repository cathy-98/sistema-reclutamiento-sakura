--
-- PostgreSQL database dump
--

\restrict yghH3j4AQRRmR70k1zb1e9JSbVwHWQVuP1AsPadpYl2BD1mHefHThWwOVM5NhAM

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    usuario character varying(50) NOT NULL,
    contrasena character varying(255) NOT NULL,
    email character varying(100) NOT NULL,
    rol character varying(30) NOT NULL
);


ALTER TABLE public.usuarios OWNER TO elitsoft_admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO elitsoft_admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.usuarios (id, usuario, contrasena, email, rol) FROM stdin;
1	fvaldesm	felipe123	felipe@gmail.com	ADMIN
3	cathy98	cathy123	cathy@gmail.com	RECLUTADORA
2	nmchavezm	noe123	noelid@gmail.com	CANDIDATO
4	jperez	miClave123	juan.perez@gmail.com	CANDIDATO
\.


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 3, true);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_usuario_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_usuario_key UNIQUE (usuario);


--
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- PostgreSQL database dump complete
--

\unrestrict yghH3j4AQRRmR70k1zb1e9JSbVwHWQVuP1AsPadpYl2BD1mHefHThWwOVM5NhAM

