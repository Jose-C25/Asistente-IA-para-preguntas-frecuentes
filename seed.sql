INSERT OR IGNORE INTO tienda_info (clave, valor) VALUES 
('nombre_local', 'Repuestos Don José'),
('direccion', '1ra Calle 3-15, Zona 1, Barrio El Centro'),
('horario', 'Lunes a Viernes: 8:00 a 17:30 hrs | Sábados: 8:00 a 13:00 hrs'),
('telefono', '7951-0000');

INSERT OR IGNORE INTO categorias (id, nombre, descripcion) VALUES
(1, 'Filtros y Mantenimiento', 'Filtros de aire y aceite'),
(2, 'Sistema de Frenos', 'Pastillas, discos y tambores'),
(3, 'Encendido y Eléctrico', 'Bujías y bobinas');

INSERT OR IGNORE INTO proveedores (id, nombre, contacto, telefono, correo) VALUES
(1, 'Importadora Central S.A.', 'Carlos Mendoza', '2211-4455', 'cmendoza@central.com');

INSERT OR IGNORE INTO productos (codigo, nombre, categoria_id, proveedor_id, precio_costo, precio_venta, equivalencia, stock, ubicacion_estante) VALUES
('FR-2024', 'Pastillas de Freno Delanteras Cerámica', 2, 1, 140.00, 225.00, 'Honda Civic 2016-2021, HR-V 2018', 8, 'B-04'),
('UJ-1998', 'Filtro de Aceite Alto Rendimiento', 1, 1, 35.00, 55.00, 'Toyota Yaris 2015-2022, Corolla 2018', 15, 'A-01'),
('BU-8812', 'Bujía de Iridio Premium', 3, 1, 45.00, 75.00, 'Nissan Sentra 2017-2023, Versa 2020', 30, 'C-02');
