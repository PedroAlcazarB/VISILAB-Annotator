// Script de inicialización para MongoDB
// Este script se ejecuta automáticamente cuando se crea la base de datos

// Crear base de datos y colecciones
db = db.getSiblingDB('visilab_annotator');

// Crear índices para mejorar el rendimiento
db.images.createIndex({ "project_id": 1 });
db.images.createIndex({ "filename": 1 });
db.images.createIndex({ "upload_date": -1 });

db.annotations.createIndex({ "image_id": 1 });
db.annotations.createIndex({ "category": 1 });
db.annotations.createIndex({ "type": 1 });
db.annotations.createIndex({ "created_date": -1 });

db.categories.createIndex({ "project_id": 1 });
db.categories.createIndex({ "name": 1, "project_id": 1 }, { unique: true });

print('Base de datos visilab_annotator inicializada correctamente');
print('Colecciones creadas: images, annotations, categories');
print('Índices creados para mejorar el rendimiento');