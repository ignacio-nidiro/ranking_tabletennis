# Instalar dependencias de Python
install-deps:
	pip install -r requirements.txt

# Inicializar el proyecto (instalar dependencias y crear la base de datos)
init: install-deps

# Limpiar la base de datos (eliminar la base de datos)
clean-db:
	@echo "Eliminando la base de datos $(DB_NAME)..."
	[ ! -e liga_tenis_mesa.db ] || rm liga_tenis_mesa.db
	@echo "Base de datos eliminada."

# Limpiar el proyecto (eliminar la base de datos y archivos generados)
clean: clean-db
	@echo "Proyecto limpio."

#Correr el proyecto
run:
	python3 app.py

# Ayuda
help:
	@echo "Opciones disponibles:"
	@echo "  make install-deps      - Instalar dependencias de Python."
	@echo "  make init              - Inicializar el proyecto (instalar dependencias y crear la base de datos)."
	@echo "  make clean-db          - Eliminar la base de datos."
	@echo "  make clean             - Limpiar el proyecto (eliminar la base de datos)."
	@echo "  make help              - Mostrar esta ayuda."
	@echo "  make run               - Correr la app"

.PHONY: install-deps create-db create-tables init clean-db clean help