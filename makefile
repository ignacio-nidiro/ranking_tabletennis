# Variables
DB_NAME = tenis_mesa
DB_USER = postgres
DB_PASSWORD = postgres
DB_HOST = localhost
DB_PORT = 5432

# Comando para ejecutar psql
PSQL = psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME)

# Instalar dependencias de Python
install-deps:
	pip install -r requirements.txt

# Crear la base de datos
create-db:
	@echo "Creando la base de datos $(DB_NAME)..."
	createdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -O $(DB_USER) $(DB_NAME)
	@echo "Base de datos creada."

# Crear las tablas en la base de datos
create-tables:
	@echo "Creando tablas en la base de datos $(DB_NAME)..."
	$(PSQL) -f sql/create_tables.sql
	@echo "Tablas creadas."

# Inicializar el proyecto (instalar dependencias y crear la base de datos)
init: install-deps create-db create-tables

# Limpiar la base de datos (eliminar la base de datos)
clean-db:
	@echo "Eliminando la base de datos $(DB_NAME)..."
	dropdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) --if-exists $(DB_NAME)
	@echo "Base de datos eliminada."

# Limpiar el proyecto (eliminar la base de datos y archivos generados)
clean: clean-db
	@echo "Proyecto limpio."

# Ayuda
help:
	@echo "Opciones disponibles:"
	@echo "  make install-deps      - Instalar dependencias de Python."
	@echo "  make create-db         - Crear la base de datos."
	@echo "  make create-tables     - Crear las tablas en la base de datos."
	@echo "  make init              - Inicializar el proyecto (instalar dependencias y crear la base de datos)."
	@echo "  make clean-db          - Eliminar la base de datos."
	@echo "  make clean             - Limpiar el proyecto (eliminar la base de datos)."
	@echo "  make help              - Mostrar esta ayuda."

.PHONY: install-deps create-db create-tables init clean-db clean help