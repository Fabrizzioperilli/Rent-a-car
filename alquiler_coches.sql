-- Autores: Diego Díaz Fernandez                alu0101130026@ull.edu.es 
--          Fabrizzio Daniell Perilli Martín    alu0101138589@ull.edu.es
-- Base de datos: alquiler_coches
-- Fecha: 12/01/2023


DROP SCHEMA public CASCADE;
CREATE SCHEMA public;


DROP TABLE IF EXISTS Agencia;
DROP TABLE IF EXISTS Empleado;
DROP TABLE IF EXISTS Garaje;
DROP TABLE IF EXISTS Vahiculo;
DROP TABLE IF EXISTS Involucra;
DROP TABLE IF EXISTS Reserva;
DROP TABLE IF EXISTS Cliente;
DROP TABLE IF EXISTS Factura;

----------Creación de tablas----------

CREATE TABLE Agencia (
    codigo_agencia INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    direccion VARCHAR(80) NOT null,
    telefono VARCHAR(9) NOT NULL,
    email VARCHAR(45) DEFAULT NULL CHECK (email LIKE '%@%.%')
);

CREATE TABLE Empleado(
    codigo_empleado INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_agencia INTEGER NOT NULL,
    dni VARCHAR(9) NOT NULL,
    nombre VARCHAR(45) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    telefono VARCHAR(9) NOT NULL,
    email VARCHAR(45) DEFAULT NULL CHECK (email LIKE '%@%.%'),
    FOREIGN KEY (codigo_agencia) REFERENCES Agencia(codigo_agencia)
);

CREATE TABLE Garaje(
    codigo_garaje INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_agencia INTEGER NOT NULL,
    direccion VARCHAR(80) NOT NULL,
    n_vehiculos INTEGER DEFAULT 0 CHECK (n_vehiculos >= 0),
    capacidad INTEGER NOT NULL CHECK (capacidad > 0 AND capacidad < 51),
    FOREIGN KEY (codigo_agencia) REFERENCES Agencia(codigo_agencia)
);

CREATE TABLE Vehiculo(
    matricula VARCHAR(7) PRIMARY KEY,
    codigo_garaje INTEGER NOT NULL,
    marca VARCHAR(45) NOT NULL,
    modelo VARCHAR(45) NOT NULL,
    color VARCHAR(45) NOT NULL,
    año INTEGER NOT NULL CHECK (año > 2010 AND año < 2023),
    kilometros FLOAT NOT NULL CHECK (kilometros > 0),
    tipo VARCHAR(45) NOT NULL CHECK (tipo IN ('Sedan','Todoterreno','Deportivo','Familiar')),
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (codigo_garaje) REFERENCES Garaje(codigo_garaje)
);

CREATE TABLE Cliente (
    codigo_cliente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_cliente_avalista INTEGER DEFAULT NULL,
    dni VARCHAR(9) NOT NULL,
    nombre VARCHAR(45) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    telefono VARCHAR(9) NOT NULL,
    direccion VARCHAR(80) NOT NULL,
    email VARCHAR(45) DEFAULT NULL CHECK (email LIKE '%@%.%'),
    FOREIGN KEY (codigo_cliente_avalista) REFERENCES Cliente(codigo_cliente)
);


CREATE TABLE Reserva(
    codigo_reserva INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_cliente INTEGER NOT NULL,
    precio_total FLOAT DEFAULT NULL,
    tipo_seguro VARCHAR(45) NOT NULL CHECK (tipo_seguro IN ('Completo', 'Terceros')),
    fecha_inicio DATE NOT NULL CHECK (fecha_inicio > CURRENT_DATE),
    fecha_fin DATE NOT NULL CHECK (fecha_fin > fecha_inicio),
    combustible_litros FLOAT NOT NULL CHECK (combustible_litros > 0),
    entregado BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (codigo_cliente) REFERENCES Cliente(codigo_cliente)
);

CREATE TABLE Involucra(
    codigo_reserva INTEGER NOT NULL,
    codigo_empleado INTEGER NOT NULL,
    matricula VARCHAR(7) NOT NULL,
    precio_alquiler FLOAT NOT NULL CHECK (precio_alquiler > 0),
    FOREIGN KEY (matricula) REFERENCES Vehiculo(matricula),
    FOREIGN KEY (codigo_empleado) REFERENCES Empleado(codigo_empleado),
    FOREIGN KEY (codigo_reserva) REFERENCES Reserva(codigo_reserva) ON DELETE CASCADE,
    PRIMARY KEY (codigo_reserva, codigo_empleado, matricula)
);

CREATE TABLE Factura(
    codigo_factura INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_reserva INTEGER NOT NULL,
    fecha DATE NOT NULL,
    importe FLOAT DEFAULT 0 CHECK (importe >= 0),
    FOREIGN KEY (codigo_reserva) REFERENCES Reserva(codigo_reserva) ON DELETE CASCADE
);

----------Creación de funciones----------

--Comprueba que el cliente avalista sea un cliente existente en la tabla cliente y que no sea el mismo cliente
CREATE OR REPLACE FUNCTION check_cliente_avalista() RETURNS TRIGGER AS $$ 
BEGIN
    IF NEW.codigo_cliente_avalista IS NOT NULL THEN
        IF NEW.codigo_cliente_avalista = NEW.codigo_cliente THEN
            RAISE EXCEPTION 'El cliente avalista no puede ser el mismo nuevo cliente';
        END IF;
        EXECUTE 'select codigo_cliente from cliente where codigo_cliente = ' || NEW.codigo_cliente_avalista;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--Al insertar un registro en involucra comprueba que el vehículo esté disponible y si está disponible lo marca como no disponible
CREATE OR REPLACE FUNCTION check_vehiculo_disponible() RETURNS TRIGGER AS $$
    DECLARE
        vehiculo_disponible BOOLEAN;
    BEGIN
        SELECT disponible INTO vehiculo_disponible FROM vehiculo WHERE matricula = NEW.matricula;
        IF vehiculo_disponible = FALSE THEN
            RAISE EXCEPTION 'El vehículo no está disponible';
        END IF;
        UPDATE vehiculo SET disponible = FALSE WHERE matricula = NEW.matricula;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

-- Actualiza el precio total de la reserva al insertar un registro en involucra sumando los precios de los vehículos involucrados
CREATE OR REPLACE FUNCTION check_precio_total() RETURNS TRIGGER AS $$
    DECLARE
        precio_total_aux FLOAT;
    BEGIN
        SELECT SUM(precio_alquiler) INTO precio_total_aux FROM involucra WHERE codigo_reserva = NEW.codigo_reserva;
        UPDATE reserva SET precio_total = precio_total_aux WHERE codigo_reserva = NEW.codigo_reserva;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

--Al actulizar al actulizar la columna entregado de la tabla reserva actualiza la columna disponible de la tabla vehiculo a true
CREATE OR REPLACE FUNCTION check_entregado() RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.entregado = TRUE THEN
            UPDATE vehiculo SET disponible = TRUE WHERE matricula IN (SELECT matricula FROM involucra WHERE codigo_reserva = NEW.codigo_reserva);
        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

--Al insertar un vehiculo aumenta el contador de n_vehiculos de la tabla garaje y si el contador es mayor que el número de capacidad del garaje lanza una excepción
CREATE OR REPLACE FUNCTION check_n_vehiculos() RETURNS TRIGGER AS $$
    DECLARE
        n_vehiculos_aux INTEGER;
    BEGIN
        SELECT n_vehiculos INTO n_vehiculos_aux FROM garaje WHERE codigo_garaje = NEW.codigo_garaje;
        IF n_vehiculos_aux >= (SELECT capacidad FROM garaje WHERE codigo_garaje = NEW.codigo_garaje) THEN
            RAISE EXCEPTION 'La capacidad del garaje está completa';
        END IF;
        UPDATE garaje SET n_vehiculos = n_vehiculos_aux + 1 WHERE codigo_garaje = NEW.codigo_garaje;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

-- Al eliminar un vehiculo disminuye el contador de n_vehiculos de la tabla garaje
CREATE OR REPLACE FUNCTION check_n_vehiculos_delete() RETURNS TRIGGER AS $$
    DECLARE
        n_vehiculos_aux INTEGER;
    BEGIN
        SELECT n_vehiculos INTO n_vehiculos_aux FROM garaje WHERE codigo_garaje = OLD.codigo_garaje;
        UPDATE garaje SET n_vehiculos = n_vehiculos_aux - 1 WHERE codigo_garaje = OLD.codigo_garaje;
        RETURN OLD;
    END;
$$ LANGUAGE plpgsql;


-- Al crear una reserva se crea una nueva factura con el precio total de la reserva como el importe de la factura, el codigo de la reserva y la fecha actual del sistema
CREATE OR REPLACE FUNCTION check_factura_reserva_insert() RETURNS TRIGGER AS $$
    DECLARE
        fecha_actual DATE;
    BEGIN
        SELECT CURRENT_DATE INTO fecha_actual;
        INSERT INTO factura (importe, codigo_reserva, fecha) VALUES (NEW.precio_total * 1.07, NEW.codigo_reserva, fecha_actual);
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;


-- Al actulizar el precio total de una reserva actulizar tambien en el importe de la factura
CREATE OR REPLACE FUNCTION check_factura_reserva_update() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE factura SET importe = NEW.precio_total * 1.07 WHERE codigo_reserva = NEW.codigo_reserva;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

----------Creación de disparadores----------

CREATE TRIGGER check_cliente_avalista
    BEFORE INSERT OR UPDATE ON Cliente
    FOR EACH ROW
    EXECUTE PROCEDURE check_cliente_avalista();

CREATE TRIGGER check_vehiculo_disponible
    BEFORE INSERT OR UPDATE ON Involucra
    FOR EACH ROW
    EXECUTE PROCEDURE check_vehiculo_disponible();

CREATE TRIGGER check_precio_total
    AFTER INSERT OR UPDATE ON Involucra
    FOR EACH ROW
    EXECUTE PROCEDURE check_precio_total();

CREATE TRIGGER check_entregado
    AFTER INSERT OR UPDATE ON Reserva
    FOR EACH ROW
    EXECUTE PROCEDURE check_entregado();

CREATE TRIGGER check_n_vehiculos
    AFTER INSERT ON Vehiculo
    FOR EACH ROW
    EXECUTE PROCEDURE check_n_vehiculos();

CREATE TRIGGER check_n_vehiculos_delete
    AFTER DELETE ON Vehiculo
    FOR EACH ROW
    EXECUTE PROCEDURE check_n_vehiculos_delete();

CREATE TRIGGER check_factura_reserva_insert
    AFTER INSERT ON Reserva
    FOR EACH ROW
    EXECUTE PROCEDURE check_factura_reserva_insert();

CREATE TRIGGER check_factura_reserva_update
    AFTER UPDATE ON Reserva
    FOR EACH ROW
    EXECUTE PROCEDURE check_factura_reserva_update();


----------Inserción de registros correctos----------

INSERT INTO Agencia (direccion, telefono, email) VALUES ('Calle 1, Santa Cruz de Tenerife','123456789','user@email.com');
INSERT INTO Agencia (direccion, telefono, email) VALUES ('Calle 2, La Orotava','123456789','user@email.com');
INSERT INTO Agencia (direccion, telefono, email) VALUES ('Calle 3, Adeje','123456789','user@email.com');

select * from agencia;

INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678A', 1, 'Juan', 'Pérez Pérez', '123456789', NULL);
INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678B', 1, 'Pedro', 'González González', '123456789', 'user@gmail.com');
INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678C', 2, 'Luis', 'García García', '123456789', NULL);
INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678D', 2, 'Ana', 'Martínez Martínez', '123456789', 'email@hotmail.com');
INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678E', 3, 'María', 'Rodríguez Rodríguez', '123456789', NULL);
INSERT INTO Empleado (dni, codigo_agencia, nombre, apellidos, telefono, email) VALUES ('12345678R', 3, 'Antonio', 'Sánchez Sánchez', '123456789', 'correo@gmail.com');

select * from empleado;

INSERT INTO Garaje (codigo_agencia, direccion, n_vehiculos, capacidad) VALUES (1, 'Calle 20, Santa Cruz de Tenerife', 0, 20);
INSERT INTO Garaje (codigo_agencia, direccion, n_vehiculos, capacidad) VALUES (1, 'Calle 21, La Laguna', 0, 40);
INSERT INTO Garaje (codigo_agencia, direccion, n_vehiculos, capacidad) VALUES (2, 'Calle 31, Puerto de la Cruz', 0, 30);
INSERT INTO Garaje (codigo_agencia, direccion, n_vehiculos, capacidad) VALUES (2, 'Calle 32, La Orotava', 0, 20);
INSERT INTO Garaje (codigo_agencia, direccion, n_vehiculos, capacidad) VALUES (3, 'Calle 41, Adeje', 0, 45);

select * from garaje;

INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABC', 1, 'Seat', 'Ibiza', 'Rojo', 2015, 10000, 'Sedan', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABD', 1, 'Seat', 'Ibiza', 'Azul', 2015, 10000, 'Familiar', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABE', 2, 'Seat', 'Ibiza', 'Verde', 2015, 10000, 'Sedan', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABF', 3, 'Fiat', '500', 'Verde', 2020, 15000, 'Familiar', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABG', 3, 'Fiat', '500', 'Rojo', 2016, 15000, 'Sedan', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABH', 4, 'Audi', 'A7', 'Negro', 2018, 15000, 'Sedan', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABI', 4, 'Jeep', 'Cherokee', 'Blanco', 2020, 15000, 'Todoterreno', true);
INSERT INTO Vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES ('1234ABJ', 5, 'Porsche', 'Panamera', 'Amarillo', 2020, 15000, 'Deportivo', true);


select * from vehiculo;

INSERT INTO Cliente (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email) VALUES (NULL, '12345678A', 'Juan', 'Perez', '123456789', 'Calle 1, Santa Cruz de Tenerife', 'email@gmail.com');
INSERT INTO Cliente (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email) VALUES (1, '12345678B', 'Pedro', 'Gonzalez', '123456789', 'Calle 2, La Orotava', NULL);
INSERT INTO Cliente (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email) VALUES (1, '12345678C', 'Luis', 'Garcia', '123456789', 'Calle 3, Adeje', NULL);
INSERT INTO Cliente (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email) VALUES (2, '12345678D', 'Ana', 'Martinez', '123456789', 'Calle 4, Santa Cruz de Tenerife', 'correoo@hola.com');

select * from cliente;

INSERT INTO Reserva (codigo_cliente, precio_total, tipo_seguro, fecha_inicio, fecha_fin, combustible_litros, entregado) VALUES (1, 100, 'Completo', '2025-12-12', '2025-12-20', 10, FALSE);
INSERT INTO Reserva (codigo_cliente, precio_total, tipo_seguro, fecha_inicio, fecha_fin, combustible_litros, entregado) VALUES (2, 100, 'Completo', '2025-11-11', '2025-11-21', 10, FALSE);
INSERT INTO Reserva (codigo_cliente, precio_total, tipo_seguro, fecha_inicio, fecha_fin, combustible_litros, entregado) VALUES (3, 100, 'Terceros', '2025-10-10', '2025-10-22', 10, FALSE);
select * from reserva;

INSERT INTO Involucra (codigo_reserva, codigo_empleado, matricula, precio_alquiler) VALUES (1, 1, '1234ABC', 100);
INSERT INTO Involucra (codigo_reserva, codigo_empleado, matricula, precio_alquiler) VALUES (1, 2, '1234ABD', 150);
INSERT INTO Involucra (codigo_reserva, codigo_empleado, matricula, precio_alquiler) VALUES (2, 3, '1234ABF', 200);
INSERT INTO Involucra (codigo_reserva, codigo_empleado, matricula, precio_alquiler) VALUES (3, 1, '1234ABG', 250);

select * from involucra;

UPDATE reserva SET entregado = true WHERE codigo_reserva = 1;

DELETE FROM Vehiculo WHERE matricula = '1234ABG';

select * from factura;