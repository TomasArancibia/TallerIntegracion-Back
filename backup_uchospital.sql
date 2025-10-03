--
-- PostgreSQL database dump
--

\restrict 9WEL3tGLuSnaRkbAlRcO6cpbk1J2LWyh5MBHwfaVXmM5pZre8fOKJNTwNALH0y1

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

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

--
-- Name: estadosolicitud; Type: TYPE; Schema: public; Owner: ucuser
--

CREATE TYPE public.estadosolicitud AS ENUM (
    'ABIERTO',
    'EN_PROCESO',
    'RESUELTO',
    'CANCELADO'
);


ALTER TYPE public.estadosolicitud OWNER TO ucuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ucuser;

--
-- Name: area; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.area (
    id_area integer NOT NULL,
    nombre character varying NOT NULL
);


ALTER TABLE public.area OWNER TO ucuser;

--
-- Name: area_id_area_seq; Type: SEQUENCE; Schema: public; Owner: ucuser
--

CREATE SEQUENCE public.area_id_area_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.area_id_area_seq OWNER TO ucuser;

--
-- Name: area_id_area_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ucuser
--

ALTER SEQUENCE public.area_id_area_seq OWNED BY public.area.id_area;


--
-- Name: cama; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.cama (
    id_cama integer NOT NULL,
    identificador_qr character varying NOT NULL,
    id_habitacion integer NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.cama OWNER TO ucuser;

--
-- Name: cama_id_cama_seq; Type: SEQUENCE; Schema: public; Owner: ucuser
--

CREATE SEQUENCE public.cama_id_cama_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cama_id_cama_seq OWNER TO ucuser;

--
-- Name: cama_id_cama_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ucuser
--

ALTER SEQUENCE public.cama_id_cama_seq OWNED BY public.cama.id_cama;


--
-- Name: habitacion; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.habitacion (
    id_habitacion integer NOT NULL,
    numero character varying NOT NULL,
    id_hospital integer NOT NULL
);


ALTER TABLE public.habitacion OWNER TO ucuser;

--
-- Name: habitacion_id_habitacion_seq; Type: SEQUENCE; Schema: public; Owner: ucuser
--

CREATE SEQUENCE public.habitacion_id_habitacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.habitacion_id_habitacion_seq OWNER TO ucuser;

--
-- Name: habitacion_id_habitacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ucuser
--

ALTER SEQUENCE public.habitacion_id_habitacion_seq OWNED BY public.habitacion.id_habitacion;


--
-- Name: hospital; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.hospital (
    id_hospital integer NOT NULL,
    nombre character varying NOT NULL
);


ALTER TABLE public.hospital OWNER TO ucuser;

--
-- Name: hospital_id_hospital_seq; Type: SEQUENCE; Schema: public; Owner: ucuser
--

CREATE SEQUENCE public.hospital_id_hospital_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hospital_id_hospital_seq OWNER TO ucuser;

--
-- Name: hospital_id_hospital_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ucuser
--

ALTER SEQUENCE public.hospital_id_hospital_seq OWNED BY public.hospital.id_hospital;


--
-- Name: solicitud; Type: TABLE; Schema: public; Owner: ucuser
--

CREATE TABLE public.solicitud (
    id_solicitud integer NOT NULL,
    id_cama integer NOT NULL,
    id_area integer NOT NULL,
    tipo character varying NOT NULL,
    descripcion character varying,
    estado_actual public.estadosolicitud,
    fecha_creacion timestamp without time zone,
    fecha_en_proceso timestamp without time zone,
    fecha_resuelta timestamp without time zone,
    fecha_cancelada timestamp without time zone,
    identificador_qr character varying NOT NULL
);


ALTER TABLE public.solicitud OWNER TO ucuser;

--
-- Name: solicitud_id_solicitud_seq; Type: SEQUENCE; Schema: public; Owner: ucuser
--

CREATE SEQUENCE public.solicitud_id_solicitud_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.solicitud_id_solicitud_seq OWNER TO ucuser;

--
-- Name: solicitud_id_solicitud_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ucuser
--

ALTER SEQUENCE public.solicitud_id_solicitud_seq OWNED BY public.solicitud.id_solicitud;


--
-- Name: area id_area; Type: DEFAULT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.area ALTER COLUMN id_area SET DEFAULT nextval('public.area_id_area_seq'::regclass);


--
-- Name: cama id_cama; Type: DEFAULT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.cama ALTER COLUMN id_cama SET DEFAULT nextval('public.cama_id_cama_seq'::regclass);


--
-- Name: habitacion id_habitacion; Type: DEFAULT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.habitacion ALTER COLUMN id_habitacion SET DEFAULT nextval('public.habitacion_id_habitacion_seq'::regclass);


--
-- Name: hospital id_hospital; Type: DEFAULT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.hospital ALTER COLUMN id_hospital SET DEFAULT nextval('public.hospital_id_hospital_seq'::regclass);


--
-- Name: solicitud id_solicitud; Type: DEFAULT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.solicitud ALTER COLUMN id_solicitud SET DEFAULT nextval('public.solicitud_id_solicitud_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.alembic_version (version_num) FROM stdin;
75da72fe645d
\.


--
-- Data for Name: area; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.area (id_area, nombre) FROM stdin;
14	Mantención
15	Aseo
16	Alimentación
\.


--
-- Data for Name: cama; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.cama (id_cama, identificador_qr, id_habitacion, activo) FROM stdin;
10	H1-101-A	9	t
11	H1-101-B	9	f
12	H1-102-A	10	t
\.


--
-- Data for Name: habitacion; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.habitacion (id_habitacion, numero, id_hospital) FROM stdin;
9	101	5
10	102	5
\.


--
-- Data for Name: hospital; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.hospital (id_hospital, nombre) FROM stdin;
5	Hospital UC Christus Demo
\.


--
-- Data for Name: solicitud; Type: TABLE DATA; Schema: public; Owner: ucuser
--

COPY public.solicitud (id_solicitud, id_cama, id_area, tipo, descripcion, estado_actual, fecha_creacion, fecha_en_proceso, fecha_resuelta, fecha_cancelada, identificador_qr) FROM stdin;
10	10	14	Reparación	La luz de la habitación no funciona	ABIERTO	2025-10-01 02:17:48.490498	\N	\N	\N	H1-101-A
11	10	14	BAÑO	No drena bien	ABIERTO	2025-10-01 02:20:37.578722	\N	\N	\N	H1-101-A
12	12	14	CAMA (LUCES, TIMBRE, ETC)	peo	ABIERTO	2025-10-01 02:27:34.751236	\N	\N	\N	H1-102-A
13	10	14	CAMA (LUCES, TIMBRE, ETC)	ayiuuuuda	ABIERTO	2025-10-01 02:57:30.376047	\N	\N	\N	H1-101-A
14	10	14	BAÑO	tengo dfreop	ABIERTO	2025-10-02 19:57:39.886639	\N	\N	\N	H1-101-A
\.


--
-- Name: area_id_area_seq; Type: SEQUENCE SET; Schema: public; Owner: ucuser
--

SELECT pg_catalog.setval('public.area_id_area_seq', 16, true);


--
-- Name: cama_id_cama_seq; Type: SEQUENCE SET; Schema: public; Owner: ucuser
--

SELECT pg_catalog.setval('public.cama_id_cama_seq', 12, true);


--
-- Name: habitacion_id_habitacion_seq; Type: SEQUENCE SET; Schema: public; Owner: ucuser
--

SELECT pg_catalog.setval('public.habitacion_id_habitacion_seq', 10, true);


--
-- Name: hospital_id_hospital_seq; Type: SEQUENCE SET; Schema: public; Owner: ucuser
--

SELECT pg_catalog.setval('public.hospital_id_hospital_seq', 5, true);


--
-- Name: solicitud_id_solicitud_seq; Type: SEQUENCE SET; Schema: public; Owner: ucuser
--

SELECT pg_catalog.setval('public.solicitud_id_solicitud_seq', 14, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: area area_pkey; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.area
    ADD CONSTRAINT area_pkey PRIMARY KEY (id_area);


--
-- Name: cama cama_identificador_qr_key; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.cama
    ADD CONSTRAINT cama_identificador_qr_key UNIQUE (identificador_qr);


--
-- Name: cama cama_pkey; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.cama
    ADD CONSTRAINT cama_pkey PRIMARY KEY (id_cama);


--
-- Name: habitacion habitacion_pkey; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.habitacion
    ADD CONSTRAINT habitacion_pkey PRIMARY KEY (id_habitacion);


--
-- Name: hospital hospital_pkey; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.hospital
    ADD CONSTRAINT hospital_pkey PRIMARY KEY (id_hospital);


--
-- Name: solicitud solicitud_pkey; Type: CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.solicitud
    ADD CONSTRAINT solicitud_pkey PRIMARY KEY (id_solicitud);


--
-- Name: ix_area_id_area; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_area_id_area ON public.area USING btree (id_area);


--
-- Name: ix_cama_id_cama; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_cama_id_cama ON public.cama USING btree (id_cama);


--
-- Name: ix_habitacion_id_habitacion; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_habitacion_id_habitacion ON public.habitacion USING btree (id_habitacion);


--
-- Name: ix_hospital_id_hospital; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_hospital_id_hospital ON public.hospital USING btree (id_hospital);


--
-- Name: ix_solicitud_id_solicitud; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_solicitud_id_solicitud ON public.solicitud USING btree (id_solicitud);


--
-- Name: ix_solicitud_identificador_qr; Type: INDEX; Schema: public; Owner: ucuser
--

CREATE INDEX ix_solicitud_identificador_qr ON public.solicitud USING btree (identificador_qr);


--
-- Name: cama cama_id_habitacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.cama
    ADD CONSTRAINT cama_id_habitacion_fkey FOREIGN KEY (id_habitacion) REFERENCES public.habitacion(id_habitacion);


--
-- Name: habitacion habitacion_id_hospital_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.habitacion
    ADD CONSTRAINT habitacion_id_hospital_fkey FOREIGN KEY (id_hospital) REFERENCES public.hospital(id_hospital);


--
-- Name: solicitud solicitud_id_area_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.solicitud
    ADD CONSTRAINT solicitud_id_area_fkey FOREIGN KEY (id_area) REFERENCES public.area(id_area);


--
-- Name: solicitud solicitud_id_cama_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ucuser
--

ALTER TABLE ONLY public.solicitud
    ADD CONSTRAINT solicitud_id_cama_fkey FOREIGN KEY (id_cama) REFERENCES public.cama(id_cama);


--
-- PostgreSQL database dump complete
--

\unrestrict 9WEL3tGLuSnaRkbAlRcO6cpbk1J2LWyh5MBHwfaVXmM5pZre8fOKJNTwNALH0y1

