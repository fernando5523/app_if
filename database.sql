-- por proveedores
SELECT 
    p.businessName,
    COUNT(i.invoiceId) AS cantidad_facturas
FROM 
    [dbo].[InvoiceTable] i
INNER JOIN 
    [dbo].[Proveedores] p ON i.vendorId = p.ruc
GROUP BY 
    i.vendorId, p.businessName
ORDER BY 
    cantidad_facturas DESC;



-- ahora solo fechas y cantidad de ingresos
SELECT 
    i.invoiceCreated,
    COUNT(i.invoiceId) AS cantidad_ingresos
FROM 
    [dbo].[InvoiceTable] i
GROUP BY 
    i.invoiceCreated
ORDER BY 
    i.invoiceCreated DESC;




-- PROCEDIMIENTOS

-- Este procedimiento almacenado crea un nuevo registro en la tabla de comprobantes
-- @purchId: ID de compra
-- @vendorId: ID del proveedor
-- @invoiceNumber: Número de factura
-- @invoiceDate: Fecha de la factura
-- @purchDate: Fecha de compra
-- @purchCurrency: Moneda de compra
-- @purchPayment: Método de pago de la compra
-- @siteId: ID del sitio
-- @warehouseId: ID del almacén
-- @pdfFile: Ruta del archivo PDF adjunto
-- @xmlFile: Ruta del archivo XML adjunto
CREATE   PROCEDURE [dbo].[InvoiceCreate]
    @purchId VARCHAR(100),
    @vendorId VARCHAR(100),
    @invoiceNumber VARCHAR(50),
    @invoiceDate DATE,
    @purchDate DATE,
    @purchCurrency VARCHAR(10),
    @purchPayment VARCHAR(20),
    @siteId VARCHAR (20),
    @warehouseId VARCHAR (20),
    @pdfFile VARCHAR(300),
    @xmlFile VARCHAR(300),
	@userId INT
AS
BEGIN
    -- Establece que no se devuelvan filas de resultados
    SET NOCOUNT ON;

    -- Intenta realizar la inserción en la tabla de comprobantes
    BEGIN TRY
        INSERT INTO InvoiceTable VALUES (
            @purchId,
            @vendorId,
            @invoiceNumber,
            @invoiceDate,
            @purchDate,
            @purchCurrency,
            @purchPayment,
            @siteId,
            @warehouseId,
            null,
            @xmlFile,
            @userId,
            null, -- Creado por
            '1', -- Estado (1 = Activo)
            CONVERT(DATE, GETDATE()), -- Fecha de creación
            CONVERT(DATE, GETDATE()) -- Fecha de modificación
        );

        -- Si la inserción es exitosa, devuelve 'True'
        SELECT 'True' AS RSPDB;
    END TRY
    BEGIN CATCH
        -- Si hay un error, devuelve 'False'
        SELECT 'False' AS RSPDB;
    END CATCH;
END;
GO


-- INVOICE UPDATE
CREATE PROCEDURE [dbo].[InvoiceUpdate]
    @purchId VARCHAR(100),
    @vendorId VARCHAR(100),
    @invoiceNumber VARCHAR(50),
    @invoiceDate DATE,
    @pdfFile VARCHAR(300),
    @xmlFile VARCHAR(300),
    @userId INT
AS
BEGIN
    -- Establece que no se devuelvan filas de resultados
    SET NOCOUNT ON;

    DECLARE @invoiceId INT;

    -- Busca el comprobante en la tabla de comprobantes
    SELECT @invoiceId = invoiceId
    FROM InvoiceTable
    WHERE invoiceNumber = @invoiceNumber
        AND purchId = @purchId
        AND vendorId = @vendorId
        AND invoiceState = '1';

    -- Actualiza los datos en la tabla de comprobantes
    BEGIN TRY
        IF @invoiceId IS NOT NULL
        BEGIN
            UPDATE InvoiceTable
            SET
                invoiceDate = @invoiceDate,
                pdfFile = @pdfFile,
                xmlFile = @xmlFile,
                userModified = @userId,
                invoiceModified = CONVERT(DATE, GETDATE())
            WHERE invoiceId = @invoiceId;

            -- Comprobante actualizado con éxito
            SELECT 'True' AS RSPDB;
        END
        ELSE
        BEGIN
            -- Si no se encuentra el comprobante, devuelve 'False'
            SELECT 'False' AS RSPDB;
        END
    END TRY
    BEGIN CATCH
        -- Si ocurre un error, devuelve 'False'
        SELECT 'False' AS RSPDB;
    END CATCH;
END;
GO


-- INVOICE VALIDATE
CREATE PROCEDURE [dbo].[InvoiceValidate]
    @purchId VARCHAR(100),
    @vendorId VARCHAR(100),
    @invoiceNumber VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @invoiceId INT;

    -- Busca el comprobante en la tabla de comprobantes
    SELECT @invoiceId = invoiceId
    FROM InvoiceTable
    WHERE purchId = @purchId
        AND vendorId = @vendorId
        AND invoiceNumber = @invoiceNumber
        AND invoiceState = '1';  -- Estado 1 significa activo

    -- Valida si el comprobante está registrado
    IF @invoiceId IS NOT NULL
    BEGIN
        -- Comprobante validado con éxito
        SELECT 'True' AS RSPDB;
    END
    ELSE
    BEGIN
        -- Comprobante no validado
        SELECT 'False' AS RSPDB;
    END;
END;
GO


-- PROVEEDORES UPDATE

CREATE PROCEDURE [dbo].[ProveedorUpdate]
    @id INT,
    @ruc VARCHAR(20),
    @businessName VARCHAR(255),
    @state VARCHAR(50),
    @readXmlHeadGroup VARCHAR(MAX),
    @readXmlBodyGroup VARCHAR(MAX),
    @dataSource VARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Actualizar la fila del proveedor con el ID especificado
        UPDATE Proveedores
        SET 
            ruc = @ruc,
            businessName = @businessName,
            state = @state,
            readXmlHeadGroup = @readXmlHeadGroup,
            readXmlBodyGroup = @readXmlBodyGroup,
            dataSource = @dataSource
        WHERE id = @id;

        -- Si la actualización fue exitosa, devuelve 'True'
        SELECT 'True' AS RSPDB;
    END TRY
    BEGIN CATCH
        -- Si ocurre un error, devuelve 'False'
        SELECT 'False' AS RSPDB;
    END CATCH;
END;
GO



-- USER CREATED
CREATE   PROCEDURE [dbo].[UserCreate]
    @userDocument VARCHAR(10),
    @userName VARCHAR(500)
AS
BEGIN
    SET NOCOUNT ON;

    -- Intenta registrar los datos en la tabla de usuarios
    BEGIN TRY
        INSERT INTO UserTable VALUES (
            @userDocument,
            @userName,
            '1' -- Estado del usuario (1 = Activo)
        );

        -- Usuario registrado con éxito
        SELECT 'True' AS RSPDB;
    END TRY
    BEGIN CATCH
        -- Usuario no registrado
        SELECT 'False' AS RSPDB;
    END CATCH;
END;
GO


-- USER UPDATE
CREATE PROCEDURE [dbo].[UserUpdate]
	@userId INT,
    @userDocument VARCHAR(10),
    @userName VARCHAR(500),
	@userState VARCHAR
AS
BEGIN
    SET NOCOUNT ON;

    -- Intenta registrar los datos en la tabla de usuarios
    BEGIN TRY
	UPDATE UserTable
	SET USERDOCUMENT = @userDocument,
	USERNAME = @userName,
	USERSTATE = @userState
	WHERE USERID = @userId;
	
        -- Usuario registrado con éxito
        SELECT 'True' AS RSPDB;
    END TRY
    BEGIN CATCH
        -- Usuario no registrado
        SELECT 'False' AS RSPDB;
    END CATCH;
END;
GO


-- USER VALÑIDATE
CREATE   PROCEDURE [dbo].[UserValidate]
    @userDocument VARCHAR(10),
    @userEmail VARCHAR(200)
AS
BEGIN
    DECLARE @userId INT;

    -- Buscamos el usuario en la tabla de usuarios
