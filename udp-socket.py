import socket
from datetime import datetime


IPLocal = "192.168.100.200"
puertoLocal= 54000
tamBuffer = 1024
estaEscuchando = True

listaMensajesRecibidos = []

#CREO UN SOCKET PARA DATAGRAMA
UDPSocketTest = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#BINDEO LA DIRECCION Y EL PUERTO
UDPSocketTest.bind((IPLocal, puertoLocal))

#DECLARO SOCKET SIN BLOQUEO
UDPSocketTest.setblocking(False)

print(">UDP SERVER ESCUCHANDO:")

#ESCUCHO DATAGRAMAS ENTRANTES

while(estaEscuchando):
    hayData = True
    momentoActual = datetime.now()

    try:
        parDireccionBytes = UDPSocketTest.recvfrom(tamBuffer)
    except:
        hayData = False

    if hayData:
        mensajeRecibido = parDireccionBytes[0]
        direccionRecibido = parDireccionBytes[1]

        mensajeDecodificado = mensajeRecibido.decode("utf-8")

        if mensajeDecodificado[0:9] == "@mensaje:":
            mensajeProcesado = ("%s %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[9:]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)
            listaMensajesRecibidos.append(mensajeProcesado)
        
        if mensajeDecodificado[0:9] == "@guardar!":
            estaGuardado = False
            mensajeProcesado = ("%s %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[:9]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)
            listaMensajesRecibidos.append(mensajeProcesado)

            #HACER QUE GUARDE EN ARCHIVO LA LISTA
            #cada vez que recibe guardar crea un nuevo archivo,
            #  con fecha+hora+LOG.txt
            nombreLog = "%s-LOG.txt" % momentoActual.strftime("%y%m%d%H%M%S")
            try:
                archivoGuardado = open(nombreLog, 'w')

                for mensajeLista in listaMensajesRecibidos:
                    archivoGuardado.write("%s\n" % mensajeLista)

                archivoGuardado.close()

                estaGuardado = True

                listaMensajesRecibidos.clear()

            except Exception as exception:
                errorString = ">ERROR DE GUARDARDO!%s" % type(exception).__name__
                print(errorString)
                UDPSocketTest.sendto(str.encode(errorString), direccionRecibido)

            #TERMINA GUARDADO
            if estaGuardado:
                mensajeDeGuardado = ">GUARDADO OK!(%s)" % nombreLog
                print(mensajeDeGuardado)
                UDPSocketTest.sendto(str.encode(mensajeDeGuardado), direccionRecibido)
            

        if mensajeDecodificado[0:10] == "@terminar!":
            estaEscuchando = False
            mensajeProcesado = ("%s %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[:10]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)

            print(">TERMINADO CON COMANDO!")
            UDPSocketTest.sendto(str.encode(">TERMINADO CON COMANDO!"), direccionRecibido)
