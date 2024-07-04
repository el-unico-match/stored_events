# match

> __Versión actual__
> * 0.0.11
> 
> __Funcionalidades actuales__
> * Creación de nuevo perfil (retorna el perfil creado)
> * Actualización de perfil solicitado (retorna el perfil actualizado)
> * Incorporación de un nuevo match
> * Consulta de todos los matchs correspondientes a un usuario
> * Consulta de todos los swipes mediante filtro
> * Consulta de perfil que coincida con el filtro
> * Agrega la fecha en que se registra un match en la base de datos
> * Incorpora cobertura de código mediante Coveralls
> * Notificación de envío de mensaje
> * Bloqueo de usuario
> * Cambio de estado del bloqueo por el usuario administrador
> * Notificación push
>
> __Cobertura de código__
> * [![Coverage Status](https://coveralls.io/repos/github/el-unico-match/match/badge.svg?branch=dev)](https://coveralls.io/github/el-unico-match/match?branch=dev)
>
> <br/>

# Archivo de ejemplo con varios perfiles de usuarios
https://github.com/el-unico-match/match/blob/dev/data/match-profiles-example.json

# Instrucciones

### Para iniciar el server: 
  1) Abrir la consola de comandos
  2) Navegar hasta la ubicación donde se encuentra el proyecto
  3) Escribir el siguiente comando: uvicorn main:app --reload <br />
     (main hace referencia al archivo main.py, app hace referencia a la variable app definida en main.py)
	 
### Para acceder a la documentación con swagger: 
  1) Abrir el navegador
  2) Escribir en la barra de direcciones: http://127.0.0.1:8000/api-docs 
  
### Para acceder a la documentación con Redocly: 
  1) Abrir el navegador
  2) Escribir en la barra de direcciones: http://127.0.0.1:8000/redoc 
  
### Para ejecutar la aplicación local

##### Base de Datos
Descargar el contenedor de la base de datos postgre:
```bash
  docker pull postgres:latest
```

Iniciar el contenedor de docker mediante la siguiente instrucción (puerto 5004 y contraseña asd123!)
```bash
  docker run --name match-database-postgres -p 5004:5432 -e POSTGRES_PASSWORD=asd123!
```

##### Código

Descargar código en el actual repositorio
```bash
  git clone git@github.com:el-unico-match/match.git
```

##### Crear venv en MacOS
```bash
  mkdir .venv
  python3 -m venv .venv
  source .venv/bin/activate
```

##### Visual Code

En el archivo **launch.config** de Visual Code agregar las siguientes líneas

```json
  {
      "name": "Match",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "justMyCode": true,
      "args": [
          "main:app",
          "--reload",
          "--port",
          "4004",
          "--host",
          "0.0.0.0"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/match",
      "python": "${workspaceFolder}/match/.venv/bin/python",
      "preLaunchTask": "Starts Matches Container Database"
  }
```

En el archivo **tasks.json** de Visual Code agregar la siguiente instrucción para levantar docker
```json
  {
      "label":"Starts Matches Container Database",
      "type": "shell",
      "command": "docker",
      "args": ["start", "match-database-postgres"] // Nombre del contenedor
  }
```

Crear el siguiente archivo **dev.env** y ubicarlo dentro de la carpeta match. 
```
  db_credentials=postgres:asd123!
  db_host=localhost
  db_port=5004
  db_name=postgres
```

##### Probar cobertura de código
Para probar la cobertura se puede ejecutar desde un .venv:
```bash
  pytest --cov=. 
```
