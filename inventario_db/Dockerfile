# Usa la imagen oficial de MySQL 5.7
FROM mysql:5.7

# Copia el script de inicialización a la carpeta de init
COPY init.sql /docker-entrypoint-initdb.d/

# Establece variables de entorno
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_DATABASE=inventario

# Los puertos expuestos por defecto son 3306 en la imagen de MySQL
EXPOSE 3306
