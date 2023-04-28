Aquí te presento una redacción mejorada del markdown:

# Despliegue del proyecto utilizando Docker

A continuación, se presentan las instrucciones para desplegar el proyecto utilizando Docker.

## Prerrequisitos

Antes de continuar, asegúrate de tener instalado Docker en tu sistema.

## Paso 1: Clonar el repositorio

Clona el repositorio del proyecto en tu equipo utilizando el siguiente comando:

```
git clone <url del repositorio>
```

## Paso 2: Configurar variables de entorno

En el archivo `docker-compose.yml`, configura las siguientes variables de entorno:

- `MONGO_INITDB_ROOT_USERNAME`: nombre de usuario de la base de datos MongoDB.
- `MONGO_INITDB_ROOT_PASSWORD`: contraseña de la base de datos MongoDB.
- `ME_CONFIG_MONGODB_ADMINUSERNAME`: nombre de usuario de administrador de la interfaz de administración de MongoDB.
- `ME_CONFIG_MONGODB_ADMINPASSWORD`: contraseña de administrador de la interfaz de administración de MongoDB.
- `ME_CONFIG_MONGODB_SERVER`: nombre del servicio MongoDB en Docker Compose.
- `ME_CONFIG_BASICAUTH_USERNAME`: nombre de usuario para acceder a la interfaz de administración de MongoDB.
- `ME_CONFIG_BASICAUTH_PASSWORD`: contraseña para acceder a la interfaz de administración de MongoDB.

## Paso 3: Iniciar los contenedores

Para iniciar los contenedores, ejecuta el siguiente comando en la raíz del proyecto:

```
docker-compose up
```

Este comando descargará las imágenes necesarias, construirá la imagen de la aplicación y levantará los contenedores.

## Paso 4: Acceder a la aplicación

Una vez que los contenedores estén en funcionamiento, podrás acceder a la aplicación en tu navegador web en la dirección `http://localhost:8000`.

## Paso 5: Acceder a la interfaz de administración de MongoDB

Para acceder a la interfaz de administración de MongoDB, abre tu navegador web y visita la dirección `http://localhost:8081`. Ingresa el nombre de usuario y la contraseña configurados en las variables de entorno.

# Ejecución del proceso de scraping

Para ejecutar el proceso de scraping, primero se deben instalar los requisitos con el siguiente comando:

```
pip3 install -r requirements.txt
```

Una vez instalados los requisitos, ejecuta el siguiente comando para iniciar el proceso de scraping:

```
python3  ./SCRAPING/index.py
```

Este proceso generará un archivo JSON con la información recuperada y subirá la información al servidor de MongoDB alojado en el contenedor de Docker.

# Documentación de la API

La documentación de la API se encuentra en la dirección `http://127.0.0.1:8000/docs`. Se requiere una autenticación de usuario mediante token "Barer" para acceder a los endpoints de la API. 

Para acceder a los endpoints de la API, puedes utilizar el usuario "johndoe" con la contraseña "secret". Agrega el header `Authorization: Bearer <token>` para autenticarte y acceder a los endpoints.

# Acceso a la base de datos

Para acceder a la base de datos, se habilitó un contenedor con mongo_express en la dirección `http://127.0.0.1:8081`. Utiliza las credenciales configuradas en las variables de entorno para acceder a la interfaz de administración de MongoDB.