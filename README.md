# Netback: Herramienta de Automatización y Backup de Redes

## 1. Resumen General

**Netback** es una aplicación web full-stack diseñada para la **gestión, automatización y respaldo (backup) de configuraciones de dispositivos de red** como routers, switches y firewalls. Su arquitectura de microservicios la hace escalable, robusta y fácil de mantener.

---

## 2. Arquitectura

El proyecto está completamente contenedorizado con Docker, y su arquitectura se compone de los siguientes servicios interconectados:

```
+------------------+      +-----------------+      +--------------------+
|                  |      |                 |      |                    |
|   Usuario Final  +----->+     Proxy       +----->+  Frontend (React)  |
|   (Navegador)    |      |     (Nginx)     |      |                    |
+------------------+      +-------+---------+      +--------------------+
                                  |
                                  |
                  +---------------+----------------+
                  |                                |
        +---------v---------+            +---------v----------+
        |                   |            |                    |
        |  Backend (Django) |            |   Celery Workers   |
        |                   |            | (Tareas Asíncronas)|
        +---------+---------+            +---------+----------+
                  |                                |
+-----------------+--------------------------------+-----------------+
|                 |                                |                 |
|       +---------v---------+            +---------v----------+      |
|       |                   |            |                    |      |
|       |  PostgreSQL (DB)  |            |      Redis         |      |
|       |                   |            | (Cache & Broker)   |      |
|       +-------------------+            +--------------------+      |
|                                                                    |
+----------------- Red Interna (netback-net) ------------------------+

```

---

## 3. Stack Tecnológico

| Componente          | Tecnología Principal                                                              |
| ------------------- | --------------------------------------------------------------------------------- |
| **Frontend**        | **React**, Material-UI (MUI), Zustand, React Router, Axios                        |
| **Backend (API)**   | **Python**, **Django**, Django REST Framework, JWT (para autenticación)           |
| **Base de Datos**   | **PostgreSQL**                                                                    |
| **Tareas Asíncronas** | **Celery** (con Celery Beat para tareas programadas)                              |
| **Message Broker**  | **Redis**                                                                         |
| **Contenerización** | **Docker** y **Docker Compose**                                                   |
| **Librerías Clave** | `netmiko`, `pyserial` (para la interacción con equipos de red)                    |

---

## 4. Descripción de los Servicios

Cada servicio se ejecuta en su propio contenedor Docker y cumple una función específica:

-   **`frontend`**: Es la interfaz de usuario (Single-Page Application) construida con **React**. Permite a los usuarios interactuar con la aplicación de forma visual.
-   **`backend`**: El cerebro de la aplicación. Es una API RESTful desarrollada en **Django** que gestiona la lógica de negocio, la autenticación de usuarios y la comunicación con los dispositivos de red.
-   **`proxy`**: Un proxy inverso (basado en Nginx) que actúa como punto de entrada. Sirve el contenido del frontend y redirige las llamadas de la API al backend de forma segura y eficiente.
-   **`postgres`**: La base de datos **PostgreSQL** donde se almacena toda la información persistente de la aplicación (usuarios, dispositivos, backups, etc.).
-   **`redis`**: Un almacén de datos en memoria que cumple dos roles:
    1.  **Broker de Mensajes** para Celery.
    2.  **Caché** para mejorar el rendimiento (opcional).
-   **`celery`**: Worker que ejecuta tareas pesadas o de larga duración en segundo plano, como realizar un backup o aplicar una configuración a un dispositivo. Esto evita que la interfaz de usuario se bloquee.
-   **`celery-beat`**: Un planificador de tareas (scheduler) que permite programar la ejecución periódica de tareas, como backups automáticos diarios o semanales.

---

## 5. Cómo Empezar

Para levantar el entorno de desarrollo, sigue estos pasos:

1.  **Clonar el Repositorio**:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd netback
    ```

2.  **Configurar Variables de Entorno**:
    Crea un archivo `.env` dentro del directorio `netback-env/` basado en un posible archivo de ejemplo. Este archivo contendrá las credenciales de la base de datos y otras claves secretas.

3.  **Construir y Ejecutar los Contenedores**:
    Desde el directorio raíz del proyecto, ejecuta el siguiente comando:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Fuerza la reconstrucción de las imágenes si ha habido cambios.
    *   `-d`: Ejecuta los contenedores en segundo plano (detached mode).

4.  **Acceder a la Aplicación**:
    -   El frontend estará disponible en `http://localhost:80`.
    -   La API del backend será accesible a través del proxy en `http://localhost:8080`.
