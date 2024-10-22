# Usa la imagen oficial de ArangoDB
FROM arangodb:latest

# Exponer el puerto para acceder a ArangoDB desde fuera del contenedor
EXPOSE 8529

# Establece la variable de entorno para la contraseña del root
ENV ARANGO_ROOT_PASSWORD=password123

# Comando para iniciar ArangoDB
CMD ["arangod"]
