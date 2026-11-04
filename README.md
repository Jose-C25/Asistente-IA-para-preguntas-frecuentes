# DonJoséBot — Asistente Virtual Inteligente y Sistema POS

> Proyecto Final — Análisis de Sistemas II, Código 037
>
> Universidad Mariano Gálvez de Guatemala
>
> Docente: Ing. Edgar Raúl Molina Rey
>
> Desarrollador: José Roberto Chub Paau
>
> Fecha: Noviembre 2026
>
> Ubicación del Negocio: Zona 1, Barrio San Juan, San Juan Chamelco, Alta Verapaz

## Descripción del Proyecto

DonJoséBot es una solución enterprise que transforma la atención al cliente y la gestión de ventas de repuestos automotrices mediante la integración de Inteligencia Artificial Generativa y una Arquitectura Limpia por capas.

El sistema permite a los clientes realizar consultas de compatibilidad multimarca en lenguaje natural, cotizar repuestos y registrar pedidos bajo la modalidad Contra Entrega. Internamente, provee un punto de venta POS para el personal de caja y administración, sincronizando automáticamente los pedidos despachados con el arqueo diario de la Caja Chica.

## Stack Tecnológico

* Lenguaje Principal: Python 3.10 o superior

* Interfaz de Usuario: Streamlit Framework con estilo AETHER UI

* Motor de IA: Groq API con modelo llama-3.3-70b-versatile y conmutación dinámica hacia Google Gemini con modelos gemini-1.5-flash y gemini-2.0-flash

* Base de Datos: SQLite3 con consultas parametrizadas y vistas de seguridad

* Ciberseguridad: PBKDF2-HMAC-SHA256 con hashes y salt de 16 bytes, RBAC, Logging y Audit Trail

## Arquitectura del Sistema Clean Architecture

El proyecto está organizado de manera modular en la carpeta app para asegurar la separación estricta de responsabilidades:

```
PROYANALISIS/
├── app/
│   ├── core/               # Módulos transversales: Seguridad PBKDF2, Sanitización y Logger
│   ├── database/           # Capa de Persistencia: Repositorios Users, Inventory, Orders, Cash
│   ├── services/           # Lógica de Negocio: Orquestador LLM, Function Calling y Tools
│   ├── views/              # Capa de Presentación: Chat Público, Login, Dashboards Admin y Cajero
│   ├── __init__.py
│   └── config.py           # Carga centralizada de variables de entorno
├── data/                   # Directorio de persistencia SQLite
├── .env                    # Variables de entorno NO subir a control de versiones
├── .gitignore              # Reglas de exclusión de Git
├── app.py                  # Punto de entrada principal de la aplicación Streamlit
├── crear_bd.py             # Script de inicialización y sembrado de la base de datos
├── schema.sql              # Estructura de tablas y vistas de seguridad
└── seed.sql                # Datos iniciales catalogo de repuestos y usuarios por defecto
```

## Matriz de Ciberseguridad OWASP Top 10

| Estándar OWASP | Mecanismo de Protección Implementado | 
| ----- | ----- | 
| A01: Broken Access Control | Autenticación y RBAC estricto en la sesión st.session_state diferenciando vistas de admin y empleado. | 
| A02: Cryptographic Failures | Hasheado seguro con PBKDF2-HMAC-SHA256 y 16 bytes de salt aleatorio. Claves de API resguardadas en el archivo .env. | 
| A03: Injection SQL y Prompt | Consultas SQL 100% parametrizadas con el operador ?. Instrucciones de sistema blindadas contra Prompt Injection. | 
| A04: Insecure Design | La IA consulta únicamente vista_inventario_publica, omitiendo físicamente la columna precio_costo. | 
| A05: Security Misconfiguration | Captura centralizada de excepciones y redirección de errores a logs/app.log sin mostrar stack traces. | 
| A07: Identification Failures | Bloqueo automático de cuenta tras 5 intentos fallidos de login. Desbloqueo administrado por el rol admin. | 
| A09: Security Logging | Registro dual de auditoría en archivo de log local y en la tabla relacional logs_auditoria. | 

## Guía de Instalación y Ejecución

Sigue estos pasos para desplegar el proyecto en tu entorno local:

### 1. Requisitos Previos

* Tener instalado Python 3.10 o superior.

* Tener instalado Git.

### 2. Clonar el Repositorio

```bash
git clone https://github.com/Jose-C25/Asistente-IA-para-preguntas-frecuentes.git
cd Asistente-IA-para-preguntas-frecuentes
```

### 3. Crear y Activar Entorno Virtual

En Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

En Linux o macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Nota: En caso de no contar con el archivo requirements.txt, es posible instalar los paquetes directamente ejecutando pip install streamlit groq google-generativeai python-dotenv.

### 5. Configurar Variables de Entorno

Crea un archivo llamado .env en la raíz del proyecto y agrega tus API Keys:

```env
GROQ_API_KEY=tu_api_key_de_groq_aqui
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

### 6. Inicializar la Base de Datos

Ejecuta el script de construcción de la estructura de base de datos y poblado inicial:

```bash
python crear_bd.py
```

### 7. Iniciar la Aplicación

Ejecuta el servidor de Streamlit:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador web por defecto en la dirección http://localhost:8501.

## Credenciales por Defecto para Pruebas

Para acceder al área administrativa y panel de cajero, utiliza los siguientes usuarios de prueba:

* Administrador General:

  * Usuario: admin

  * Contraseña: admin123

  * Permisos: CRUD completo de inventario, visualización de precios de costo, desbloqueo de usuarios y auditoría.

* Cajero o Empleado:

  * Usuario: cajero

  * Contraseña: cajero123

  * Permisos: Procesamiento de pedidos de clientes, cambio de estados a Entregado y arqueo de Caja Chica.

## Pruebas de Resiliencia y Fallback

Para probar la conmutación automática de modelos de IA en caso de error en la API principal:

1. Altera intencionalmente la clave GROQ_API_KEY en tu archivo .env por un valor inválido.

2. Realiza cualquier consulta en el chat público.

3. Observa la consola del sistema: verás la alerta FALLO GROQ PRINCIPAL Activando Gemini Fallback. El chat responderá sin interrumpir el servicio utilizando el motor secundario.