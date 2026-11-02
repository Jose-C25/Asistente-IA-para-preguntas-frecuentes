PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tienda_info (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    contacto TEXT,
    telefono TEXT,
    correo TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    proveedor_id INTEGER NOT NULL,
    precio_costo REAL NOT NULL,
    precio_venta REAL NOT NULL,
    equivalencia TEXT,
    stock INTEGER NOT NULL DEFAULT 0,
    ubicacion_estante TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE VIEW IF NOT EXISTS vista_inventario_publica AS
SELECT 
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    p.precio_venta,
    p.equivalencia,
    p.stock,
    p.ubicacion_estante
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id;