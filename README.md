# iteso-bdnr-mongodb

A place to share mongodb app code

### Setup a python virtual env with python mongodb installed
```
# If pip is not present in you system
sudo apt update
sudo apt install python3-pip

# Install and activate virtual env (Linux/MacOS)
python3 -m pip install virtualenv
python3 -m venv ./venv
source ./venv/bin/activate

# Install and activate virtual env (Windows)
python3 -m pip install virtualenv
python3 -m venv ./venv
.\venv\Scripts\Activate.ps1

# Install project python requirements
pip install -r requirements.txt
```

### To run the API service
```
python -m uvicorn main:app --reload --port 8000
```

### To load data
Ensure you have a running mongodb instance
i.e.:
```
docker run --name mongodb -d -p 27017:27017 mongo
```
Once your API service is running (see step above), run the populate script
```
cd data/
python populate.py
```

### Troubleshooting

1. Selecciona el intérprete correcto en VS Code:
	- Ctrl+Shift+P -> "Python: Select Interpreter" -> elige `.venv` dentro del proyecto.
2. Si Pylance marca `reportMissingImports` para `falcon`, `pymongo`, `requests` o `bson`:
	- Asegúrate de haber activado el entorno: `\.venv\Scripts\Activate.ps1`.
	- Reinstala dependencias: `pip install -r requirements.txt`.
	- No instales el paquete externo `bson`; viene incluido con `pymongo`.
3. MongoDB no accesible:
	- Verifica contenedor: `docker ps` y que el puerto 27017 esté escuchando.
4. Puerto 8000 en uso:
	- Cambia a otro puerto: `uvicorn main:app --reload --port 8001` y ajusta `BASE_URL` en scripts.
5. Verificar imports rápidamente:
	- `python -c "import falcon, pymongo, requests, uvicorn, bson; print('OK')"`

### Scripts útiles

- `data/populate.py`: carga libros desde CSV.
- `client.py`: prueba rápida de endpoints PUT/DELETE.
- `test_api.py`: inserta datos y prueba GET/PUT/DELETE vía HTTP.
- `test_direct.py`: pruebas directas sobre la base sin levantar el servidor.

