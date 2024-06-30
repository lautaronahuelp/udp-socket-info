import socket
from datetime import datetime

# INSTRUCCIONES DE USO:
# @mensaje:MSJ => eco MSJ y lo guarda en la lista
# @repetir:MSJ => igual que @mensaje: ademas repite el eco segun intervaloRepeticion
# @intervalo:TIEMPO => seguido de TIEMPO en ms, cambia intervaloRepeticion a TIEMPO
# si es mayor o igual a 50ms sino lo establece a INTERVALO_REP, echo y enlista @intervalo:tiempo~intervaloRepeticion
# @guardar! => guarda lista en archivo TXT, eco el mensaje de guardar
# @terminar! => termina ejecucion del servidor, eco el mensaje de terminar

INTERVALO_REP = 5000

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
repetirUltimo = False
ultimaRepeticion = datetime.now()
ultimoRecibido = []
intervaloRepeticion =  INTERVALO_REP

while(estaEscuchando):
    hayData = True
    momentoActual = datetime.now()

    try:
        parDireccionBytes = UDPSocketTest.recvfrom(tamBuffer)
    except:
        hayData = False

    restaTimeout = datetime.now() - ultimaRepeticion

    if repetirUltimo and (restaTimeout.total_seconds() * 1000) > intervaloRepeticion and not(hayData):
        mensajeProcesado = ("%s R %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), ultimoRecibido[1], ultimoRecibido[0]))
        UDPSocketTest.sendto(str.encode(mensajeProcesado), ultimoRecibido[1])
        ultimaRepeticion = datetime.now()
        print(mensajeProcesado)
        listaMensajesRecibidos.append(mensajeProcesado)

    if hayData:
        mensajeRecibido = parDireccionBytes[0]
        direccionRecibido = parDireccionBytes[1]

        mensajeDecodificado = mensajeRecibido.decode("utf-8")

        if mensajeDecodificado[0:9] == "@mensaje:":
            repetirUltimo = False
            mensajeProcesado = ("%s N %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[9:]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)
            listaMensajesRecibidos.append(mensajeProcesado)
        
        if mensajeDecodificado[0:9] == "@repetir:":
            repetirUltimo = True
            mensajeProcesado = ("%s N %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[9:]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            ultimoRecibido = [mensajeProcesado, parDireccionBytes[1]]
            ultimaRepeticion = datetime.now()
            print(mensajeProcesado)
            listaMensajesRecibidos.append(mensajeProcesado)
        
        if mensajeDecodificado[0:11] == "@intervalo:":
            repetirUltimo = False

            nuevoIntervalo = mensajeDecodificado[11:]

            if int(nuevoIntervalo) >= 50:
                intervaloRepeticion = int(nuevoIntervalo)
            else:
                intervaloRepeticion = INTERVALO_REP

            mensajeProcesado = ("%s N %s:%s~%d" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado, intervaloRepeticion))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)

            listaMensajesRecibidos.append(mensajeProcesado)
        
        if mensajeDecodificado[0:9] == "@guardar!":
            repetirUltimo = False
            estaGuardado = False
            mensajeProcesado = ("%s N %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[:9]))
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
            repetirUltimo = False
            estaEscuchando = False
            mensajeProcesado = ("%s N %s:%s" % (momentoActual.strftime("%d/%m/%y_%H:%M:%S"), direccionRecibido, mensajeDecodificado[:10]))
            UDPSocketTest.sendto(str.encode(mensajeProcesado), direccionRecibido)
            print(mensajeProcesado)

            print(">TERMINADO CON COMANDO!")
            UDPSocketTest.sendto(str.encode(">TERMINADO CON COMANDO!"), direccionRecibido)
