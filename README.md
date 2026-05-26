# 🚀 Sakura Recruitment System - 

Este repositorio contiene el código fuente unificado y la infraestructura local para el desarrollo e integración del módulo de autenticación (**Login**) del Sistema de Reclutamiento y Evaluación de Sakura. 

El proyecto adopta un enfoque de monorrepositorio local, segmentando limpiamente la capa de servicios (Backend), la capa de interfaz de usuario (Frontend) y la orquestación del entorno de datos a través de contenedores.

---

## 🛠️ Stack Tecnológico

* **Base de Datos:** PostgreSQL 15 (Contenerizado bajo Docker con imagen Alpine Linux).
* **Backend:** Python 3.10+ (FastAPI / SQLAlchemy ORM / PyJWT / Bcrypt).
* **Frontend:** Angular 18 (Arquitectura basada en Componentes, Servicios SPA y AuthGuards).
* **Infraestructura Local:** Docker Desktop & Docker Compose.

---

## 📂 Estructura del Repositorio

```text
sistema-reclutamiento/
├── backend/          # Microservicio en Python enfocado en la API de autenticación y lógica JWT.
├── frontend/         # Aplicación Single Page Application (SPA) en Angular para las vistas de usuario.
├── docker-compose.yml# Orquestador local para los contenedores de PostgreSQL y pgAdmin.
└── .gitignore        # Exclusión estricta de entornos virtuales, node_modules y credenciales sensibles.
