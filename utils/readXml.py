from xml.etree import ElementTree
import pandas

class xmlRead:
    def readHeadXmlGrupo1(self, urlFile):
        try:
            __xmlLabels = {
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "sac": "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1",
            }
             
            __xmlData = ElementTree.parse(urlFile).getroot()

            if "Invoice" not in __xmlData.tag:
                __xmlData = __xmlData.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")

            if __xmlData:
                __responseXML = {
                    "VENDORID": __xmlData.find("cac:AccountingSupplierParty", __xmlLabels)
                    .find("cac:Party", __xmlLabels)
                    .find("cac:PartyIdentification", __xmlLabels)
                    .find("cbc:ID", __xmlLabels)
                    .text,
                    "INVOICENUMBER": __xmlData.find("cbc:ID", __xmlLabels).text,
                    "INVOICEDATE": __xmlData.find("cbc:IssueDate", __xmlLabels).text,
                    "INVOICECURRENCY": __xmlData.find("cbc:DocumentCurrencyCode", __xmlLabels).text,
                    "URLFILE": urlFile,
                }
                return __responseXML

            else:
                return None
        
        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_invoice_header_ximesa: {str(e)}")
            return None
    
    def readProductsXmlGrupo1(self, urlFile):
            try:
    
                ns = {
                    'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
                }
    
                root = ElementTree.parse(urlFile).getroot()
                if "Invoice" not in root.tag:
                        root = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
    
                # Definir listas para almacenar los datos de cada columna
                __xmlData = {
                    "COD_PRODUCT": [],
                    "PRODUCT_QUANTITY": [],
                    "DESCRIPTION": [],
                    "UNIT_PRICE": [],
                    "SUB_TOTAL": [],
                    "IGV" : [],
                    "TOTAL": []
                }
    
                # Iterar sobre cada elemento <InvoiceLine> en el XML
                for items in root.findall('cac:InvoiceLine', ns):
                    # Codigo del producto
                    cod_val = items.find('cac:Item', ns).find('cac:SellersItemIdentification', ns)
                    codigo = str(cod_val.find('cbc:ID', ns).text if cod_val is not None else None)
            
                    # Cantidad del producto
                    productquantity = float(items.find('cbc:InvoicedQuantity', ns).text)
    
                    # Descripción del producto
                    descripcion = items.find('cac:Item', ns).find('cbc:Description', ns).text
    
                    #Validaciones
                    try:
                        primera = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                        primera_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cbc:TaxableAmount', ns).text)
                    except:
                        primera = ""
                
                    try:
                        segunda = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                        segunda_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cbc:TaxableAmount', ns).text)
                    except:
                        segunda = ''
            
                    if primera == "GRA":
                        subtotal = 0
                        subtotalIGV = 0
                        IGV = 0
                    else:
                        if primera == 'ISC':
                            # Subtotal del producto
                            subtotal = segunda_subtotal
                        elif segunda == 'ISC':
                            # Subtotal del producto
                            subtotal = primera_subtotal
                        else:
                            subtotal = float(items.find('cbc:LineExtensionAmount', ns).text)
                        #Validar si es que la FACTURA tiene IGV:
                        if primera == "IGV" or segunda == 'IGV':
                            IGV = subtotal*0.18
                        else:
                            IGV = 0
                
                        # Sub total con IGV
                        subtotalIGV = subtotal + IGV
    
                    # Agregar los datos a las listas
                    __xmlData["COD_PRODUCT"].append(codigo)
                    __xmlData["PRODUCT_QUANTITY"].append(productquantity)
                    __xmlData["DESCRIPTION"].append(descripcion)
                    __xmlData["UNIT_PRICE"].append(round(subtotal / productquantity, 4))
                    __xmlData["SUB_TOTAL"].append(round(subtotal, 4))
                    __xmlData["IGV"].append(round(IGV, 4))
                    __xmlData["TOTAL"].append(round(subtotalIGV, 4))
    
                # Crear un DataFrame con los datos
                df = pandas.DataFrame(__xmlData)
    
                return df
        
            except Exception as e:
                return None
    
    
    def readProductsXmlGrupo2(self, urlFile):
        try:
            ns = {
                'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
   
            root = ElementTree.parse(urlFile).getroot()
            if "Invoice" not in root.tag:
                    root = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
   
            # Definir listas para almacenar los datos de cada columna
            __xmlData = {
                "COD_PRODUCT": [],
                "PRODUCT_QUANTITY": [],
                "DESCRIPTION": [],
                "UNIT_PRICE": [],
                "SUB_TOTAL": [],
                "IGV" : [],
                "TOTAL": []
            }
   
            # Iterar sobre cada elemento <InvoiceLine> en el XML
            for items in root.findall('cac:InvoiceLine', ns):
                # Codigo del producto
                cod_val = items.find('cac:Item', ns).find('cac:SellersItemIdentification', ns)
                codigo = str(cod_val.find('cbc:ID', ns).text if cod_val is not None else None)
                codigoFormateado = codigo.lstrip('0')
 
                # Cantidad del producto
                productquantity = float(items.find('cbc:InvoicedQuantity', ns).text)
 
                # Descripción del producto
                descripcion = items.find('cac:Item', ns).find('cbc:Description', ns).text
 
                #Validaciones
                try:
                    primera = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                    primera_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cbc:TaxableAmount', ns).text)
                except:
                    primera = ""
               
                try:
                    segunda = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                    segunda_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cbc:TaxableAmount', ns).text)
                except:
                    segunda = ''
           
                if primera == "GRA":
                    subtotal = 0
                    subtotalIGV = 0
                    IGV = 0
                else:
                    if primera == 'ISC':
                        # Subtotal del producto
                        subtotal = segunda_subtotal
                    elif segunda == 'ISC':
                        # Subtotal del producto
                        subtotal = primera_subtotal
                    else:
                        subtotal = float(items.find('cbc:LineExtensionAmount', ns).text)
                    #Validar si es que la FACTURA tiene IGV:
                    if primera == "IGV" or segunda == 'IGV':
                        IGV = subtotal*0.18
                    else:
                        IGV = 0
               
                    # Sub total con IGV
                    subtotalIGV = subtotal + IGV
 
                # Agregar los datos a las listas
                __xmlData["COD_PRODUCT"].append(codigoFormateado)
                __xmlData["PRODUCT_QUANTITY"].append(productquantity)
                __xmlData["DESCRIPTION"].append(descripcion)
                __xmlData["UNIT_PRICE"].append(round(subtotal / productquantity, 4))
                __xmlData["SUB_TOTAL"].append(round(subtotal, 4))
                __xmlData["IGV"].append(round(IGV, 4))
                __xmlData["TOTAL"].append(round(subtotalIGV, 4))
   
            # Crear un DataFrame con los datos
            df = pandas.DataFrame(__xmlData)
   
            return df
 
        except Exception as e:
            return None
        
    def readProductsXmlGrupo3(self, urlFile):
        try:
 
            ns = {
                'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
   
            root = ElementTree.parse(urlFile).getroot()
            if "Invoice" not in root.tag:
                    root = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
   
            # Definir listas para almacenar los datos de cada columna
            __xmlData = {
                "COD_PRODUCT": [],
                "PRODUCT_QUANTITY": [],
                "DESCRIPTION": [],
                "UNIT_PRICE": [],
                "SUB_TOTAL": [],
                "IGV" : [],
                "TOTAL": []
            }
   
            # Iterar sobre cada elemento <InvoiceLine> en el XML
            for items in root.findall('cac:InvoiceLine', ns):
                # Codigo del producto
                cod_val = items.find('cac:Item', ns).find('cac:SellersItemIdentification', ns)
                codigo = str(cod_val.find('cbc:ID', ns).text if cod_val is not None else None)
           
                # Cantidad del producto
                productquantity = float(items.find('cbc:InvoicedQuantity', ns).text)
   
                # Descripción del producto
                descripcion = items.find('cac:Item', ns).find('cbc:Description', ns).text
   
                #Validaciones
                try:
                    primera = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                    primera_subtotal = float(items.find('cac:AllowanceCharge', ns).find('cbc:BaseAmount', ns).text)
                except:
                    primera = ""
           
                if primera == "GRA":
                    subtotal = 0
                    subtotalIGV = 0
                    IGV = 0
                else:
                    subtotal = primera_subtotal
 
                    #Validar si es que la FACTURA tiene IGV:
                    if primera == "IGV":
                        IGV = subtotal*0.18
                    else:
                        IGV = 0
               
                    # Sub total con IGV
                    subtotalIGV = subtotal + IGV
 
                # Agregar los datos a las listas
                __xmlData["COD_PRODUCT"].append(codigo)
                __xmlData["PRODUCT_QUANTITY"].append(productquantity)
                __xmlData["DESCRIPTION"].append(descripcion)
                __xmlData["UNIT_PRICE"].append(round(subtotal / productquantity, 4))
                __xmlData["SUB_TOTAL"].append(round(subtotal, 4))
                __xmlData["IGV"].append(round(IGV, 4))
                __xmlData["TOTAL"].append(round(subtotalIGV, 4))
   
            # Crear un DataFrame con los datos
            df = pandas.DataFrame(__xmlData)
   
            return df
       
        except Exception as e:
            return None
 
    def readProductsXmlGrupo4(self, urlFile):
        try:
 
            ns = {
                'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
   
            root = ElementTree.parse(urlFile).getroot()
            if "Invoice" not in root.tag:
                    root = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
   
            # Definir listas para almacenar los datos de cada columna
            __xmlData = {
                "COD_PRODUCT": [],
                "PRODUCT_QUANTITY": [],
                "DESCRIPTION": [],
                "UNIT_PRICE": [],
                "SUB_TOTAL": [],
                "IGV" : [],
                "TOTAL": []
            }
   
            # Iterar sobre cada elemento <InvoiceLine> en el XML
            for items in root.findall('cac:InvoiceLine', ns):
 
                # Código y descripción del producto
                codigo = items.find('cac:Item', ns).find('cbc:Description', ns).text.strip()
               
                # Eliminar corchetes y dividir el código y la descripción
                try:
                    numero, descripcion = codigo.strip('[]').split(' ', 1)
                    cod_fin = numero.replace("]","")
                    descrip_fin = descripcion.strip()
                except ValueError:
                    numero = "SIN_CODIGO"
           
                # Cantidad del producto
                productquantity = float(items.find('cbc:InvoicedQuantity', ns).text)
   
                #Validaciones
                try:
                    primera = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                    primera_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cbc:TaxableAmount', ns).text)
                except:
                    primera = ""
               
                try:
                    segunda = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                    segunda_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cbc:TaxableAmount', ns).text)
                except:
                    segunda = ''
           
                if primera == "GRA":
                    subtotal = 0
                    subtotalIGV = 0
                    IGV = 0
                else:
                    if primera == 'ISC':
                        # Subtotal del producto
                        subtotal = segunda_subtotal
                    elif segunda == 'ISC':
                        # Subtotal del producto
                        subtotal = primera_subtotal
                    else:
                        subtotal = float(items.find('cbc:LineExtensionAmount', ns).text)
                    #Validar si es que la FACTURA tiene IGV:
                    if primera == "IGV" or segunda == 'IGV':
                        IGV = subtotal*0.18
                    else:
                        IGV = 0
               
                    # Sub total con IGV
                    subtotalIGV = subtotal + IGV
 
                # Agregar los datos a las listas
                __xmlData["COD_PRODUCT"].append(cod_fin)
                __xmlData["PRODUCT_QUANTITY"].append(productquantity)
                __xmlData["DESCRIPTION"].append(descrip_fin)
                __xmlData["UNIT_PRICE"].append(round(subtotal / productquantity, 4))
                __xmlData["SUB_TOTAL"].append(round(subtotal, 4))
                __xmlData["IGV"].append(round(IGV, 4))
                __xmlData["TOTAL"].append(round(subtotalIGV, 4))
   
            # Crear un DataFrame con los datos
            df = pandas.DataFrame(__xmlData)
   
            return df
       
        except Exception as e:
            return None
        
    def readProductsXmlGrupo5(self, urlFile):
            try:
    
                ns = {
                    'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
                }
    
                root = ElementTree.parse(urlFile).getroot()
                if "Invoice" not in root.tag:
                        root = root.find(".//{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
    
                # Definir listas para almacenar los datos de cada columna
                __xmlData = {
                    "COD_PRODUCT": [],
                    "PRODUCT_QUANTITY": [],
                    "DESCRIPTION": [],
                    "UNIT_PRICE": [],
                    "SUB_TOTAL": [],
                    "IGV" : [],
                    "TOTAL": []
                }
    
                # Iterar sobre cada elemento <InvoiceLine> en el XML
                for items in root.findall('cac:InvoiceLine', ns):
    
                    # Código y descripción del producto
                    texto = items.find('cac:Item', ns).find('cbc:Description', ns).text.strip()
                
                    # Eliminar corchetes y dividir el código y la descripción
                    try:
                        textoFin = texto.split(' ', 1)
                        codigo = textoFin[0]
                        # Verificar si el código es un número
                        if codigo.isdigit():
                            descripcion = textoFin[1]  # Asignar la descripción si el código es un número
                        else:
                            # Si el código no es un número, se considera todo como descripción
                            codigo = "none"
                            descripcion = texto
                    except ValueError:
                        codigo = "none"
            
                    # Cantidad del producto
                    productquantity = float(items.find('cbc:InvoicedQuantity', ns).text)
    
                    #Validaciones
                    try:
                        primera = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                        primera_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[0].find('cbc:TaxableAmount', ns).text)
                    except:
                        primera = ""
                
                    try:
                        segunda = items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cac:TaxCategory', ns).find('cac:TaxScheme', ns).find('cbc:Name', ns).text
                        segunda_subtotal = float(items.find('cac:TaxTotal', ns).findall('cac:TaxSubtotal', ns)[1].find('cbc:TaxableAmount', ns).text)
                    except:
                        segunda = ''
            
                    if primera == "GRA":
                        subtotal = 0
                        subtotalIGV = 0
                        IGV = 0
                    else:
                        if primera == 'ISC':
                            # Subtotal del producto
                            subtotal = segunda_subtotal
                        elif segunda == 'ISC':
                            # Subtotal del producto
                            subtotal = primera_subtotal
                        else:
                            subtotal = float(items.find('cbc:LineExtensionAmount', ns).text)
                        #Validar si es que la FACTURA tiene IGV:
                        if primera == "IGV" or segunda == 'IGV':
                            IGV = subtotal*0.18
                        else:
                            IGV = 0
                
                        # Sub total con IGV
                        subtotalIGV = subtotal + IGV
    
                    # Agregar los datos a las listas
                    __xmlData["COD_PRODUCT"].append(codigo)
                    __xmlData["PRODUCT_QUANTITY"].append(productquantity)
                    __xmlData["DESCRIPTION"].append(descripcion)
                    __xmlData["UNIT_PRICE"].append(round(subtotal / productquantity, 4))
                    __xmlData["SUB_TOTAL"].append(round(subtotal, 4))
                    __xmlData["IGV"].append(round(IGV, 4))
                    __xmlData["TOTAL"].append(round(subtotalIGV, 4))
    
                # Crear un DataFrame con los datos
                df = pandas.DataFrame(__xmlData)
    
                return df
        
            except Exception as e:
                return None