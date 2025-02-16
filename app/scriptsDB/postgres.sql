-- Database: vector_db

-- DROP DATABASE IF EXISTS vector_db;

CREATE DATABASE vector_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    ICU_LOCALE = 'en-US'
    LOCALE_PROVIDER = 'icu'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
  
  
  
    
    
-- Table: public.candidate

-- DROP TABLE IF EXISTS public.candidate;

CREATE TABLE IF NOT EXISTS public.candidate
(
    id integer NOT NULL DEFAULT nextval('candidate_id_seq'::regclass),
    name text COLLATE pg_catalog."default",
    phone text COLLATE pg_catalog."default",
    email text COLLATE pg_catalog."default",
    state text COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    english_level text COLLATE pg_catalog."default",
    education text[] COLLATE pg_catalog."default",
    years_experience text COLLATE pg_catalog."default",
    summary text COLLATE pg_catalog."default",
    companies text[] COLLATE pg_catalog."default",
    level text COLLATE pg_catalog."default",
    skills text[] COLLATE pg_catalog."default",
    main_skills text[] COLLATE pg_catalog."default",
    certs text[] COLLATE pg_catalog."default",
    previous_roles text[] COLLATE pg_catalog."default",
    resume_type text COLLATE pg_catalog."default",
    rehire boolean,
    cl integer,
    current_project text COLLATE pg_catalog."default",
    roll_on_date text COLLATE pg_catalog."default",
    roll_off_date text COLLATE pg_catalog."default",
    embedding vector(768),
    CONSTRAINT candidate_pkey PRIMARY KEY (id),
    CONSTRAINT candidate_email_key UNIQUE (email)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.candidate
    OWNER to postgres;
   
   
   
   
   
    
    
-- Table: public.roles

-- DROP TABLE IF EXISTS public.roles;

CREATE TABLE IF NOT EXISTS public.roles
(
    id integer NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
    role_id text COLLATE pg_catalog."default",
    role_name text COLLATE pg_catalog."default",
    project text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    industry text COLLATE pg_catalog."default",
    location text COLLATE pg_catalog."default",
    location_type text COLLATE pg_catalog."default",
    level text COLLATE pg_catalog."default",
    level2 text COLLATE pg_catalog."default",
    main_skill text COLLATE pg_catalog."default",
    secondary_skill text COLLATE pg_catalog."default",
    contact text COLLATE pg_catalog."default",
    start_date date,
    end_date date,
    capability text COLLATE pg_catalog."default",
    opportunity_type text COLLATE pg_catalog."default",
    embedding vector(768),
    CONSTRAINT roles_pkey PRIMARY KEY (id),
    CONSTRAINT roles_role_id_key UNIQUE (role_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.roles
    OWNER to postgres;