<h1><center>CRONOSTAMPER</center></h1>
<h1><center>MANUAL DE USUARIO</center></h1>
<h1><center>Version 1</center></h1>

<h1>Indice</h1>

- [Introducción](#introducción)
- [Puesta en marcha](#puesta-en-marcha)
  - [Conexionado](#conexionado)
  - [Pantalla de control](#pantalla-de-control)
  - [Acceso a la marca de tiempo](#acceso-a-la-marca-de-tiempo)
- [Configuración](#configuración)
  - [Configuración de la Red](#configuración-de-la-red)
  - [Acceso a la consola](#acceso-a-la-consola)
      - [Configuración de la aplicación](#configuración-de-la-aplicación)
  - [Descrición general](#descrición-general)
    - [Hardware:](#hardware)
    - [Software:](#software)
    - [Funcionamiento](#funcionamiento)


# Introducción

El dispositivo **CRONOSTAMPER** tiene como función principal la obtención de marcas de tiempo de ultraprecisión. La marca se da en tiempo UTC y la precisión tipica es menor de 5 microsegundos.

El cronostamper fue desarrollado originalmente para el registro preciso de tiempo UTC de las imagenes astronomicas captadas por las camaras CCD de observatorios astronomicos. Éste sigue siendo su uso principal.

En su diseño se ha pretendido que sea lo mas sencillo de usar para su uso principal pero que admita todas las modificaciones que el usuario desee mediante el acceso completo al sistema operativo y al codigo fuente empleado. El el codigo de la aplicación es open source y la plataforma donde se ejecuta es la bien conocida Raspberry PI con el sistema operativo linux-debian Bookworm.

Funciones secundarias:

* Incorpora una función para activar una señal (un pulso) en un instante muy preciso del tiempo UTC. Asi por ejemplo es posible, usando dos cronostamper en ubicaciones distantes, realizar un disparo simultáneo con la garantia de que a lo sumo diferiran en 10 microsegundos en el tiempo UTC. **IMPORTANTE:** está función está programada en el software pero no está cableada en el hardware. Se cablea bajo demanda al fabricante.
* Puede actuar como servidor de tiempos NTP para la red a la que está conectado.

![Alt text](<vista_general.jpg>)

# Puesta en marcha

## Conexionado
Para instalar el cronostamper hay que realizar las siguientes conexiones:

* Cable Ethernet
* Cable de alimentación USB-C
* RP-SMA hembra (reverse polarity SMA): conexionado del cable de la señal a medir (SIGNAL). Por ejemplo la señal de 'trigger' de una cámara CCD. Esta señal debe ser de entre 3.3 y 5V
* SMA hembra: antena exterior GPS

**IMPORTANTE**: Los conectores son diferentes y puede ocurrir daño mecanico si se conectan equivocadamente.

## Pantalla de control
Una vez energizado y conectado a la red se pude acceder a la pantalla de estado mediante cualquier navegador en la dirección http://[ip del cronostamper]:5000

## Acceso a la marca de tiempo
Para acceder a los resultado de la marca de tiempos hay que conectarse al puerto TCP/IP definido en la variable socketsPort del archivo de configuracion config.py (puerto por defecto 9999)

Cada vez que se produce la activación de la señal SIGNAL la marca de tiempo es devuelta con el formato:
```
"%s %010.6f %01.0d %5.3e\r\n" % (msg['dateUTC'],msg['pulse'],ppsOK,clkError)
```

Este mismo mensaje tambien se envia mediante un publisher ZMQ en el puerto zmqShutterPort (por defecto el 5556) al que se puede acceder mediante cualquier software que integre este protocolo (pythom,C/C++, java, rust...practicamente todos)

A modo de ejemplo se muestra un programa basico de python:
```
  import zmq
  import json
  
  zmqShutterPort=5556
  ShutterFlange="SHUTTER_LOW"    
  # Socket to talk to server
  context = zmq.Context()
  socket = context.socket(zmq.SUB)
  socket.connect ("tcp://cronostamper:%s" % zmqShutterPort)
  topicfilter = ShutterFlange
  socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

  def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 

  # Process
  while True:
    topic, msg  = demogrify(socket.recv())
    print("%f" % msg['unixUTC'])
    #time.sleep(5)

```

# Configuración
Normalmente los cronostamper vienen configurados de fábrica no siendo necesario para su funcionamiento nada mas que realizar el cableado y conectarlo a la alimentación electrica. No obstante se explica aqui las acciones de configuración mas habituales que se puden realizar.

## Configuración de la Red
<a id="configuración-de-la-red"></a>
Los cronostamper normalmente viene configurados de fábrica con la dirección IP y demás datos de red proporcionados por el cliente. En esta sección se explica como cabiarla si fuese necesario.

El cronostamper gestiona su datos de conexión mediante la utilidad [NetworkManager](https://networkmanager.dev/) del linux. Se puede utilizar por tanto utilizando todos los comandos de esta herramienta. Se recomienda el uso del comando **"sudo nmtui"** desde una consola BASH ( ver [Acceso a la consola](#acceso-a-la-consola) ) para poderlo configurar comodamente mediante interface grafica de terminal. Mediante este metodo se puede configurar tanto la ethernet cableada como la WiFi **IMPORTANTE:** Esta información es valida solo para la ultima versión del cronostamper con sistema operativo rapberry OS Bookworm.

Adicionalmente los cronostampers están configurados para conectarse a cualquier punto de acceso WiFi, un telefono movil valdria, con nombre SSID cronostamper_net y password entregado en la tarjeta de claves con seguridad WPA-PKA. Esto es un mecanismo de backup en el caso de problemas de perdida de conectividad con la configuración de red. Se considera seguro porque el alcance WiFi de los cronostamper está bastante limitado (no mas de 10m) ya que el dispositivo está encapsulado en una caja metalica. No obstante el usuario puede desactivar este comportamiento utilizando la mencionada utilidad "sudo nmtui".

## Acceso a la consola
<a id="acceso-a-la-consola"></a>

Una vez que se tiene conectividad de red es posible acceder a la consola del sistema operativo para cualquier labor de mantenimento o reconfiguración. Para obtener conectividad de red ver [Configuración de la Red](#configuración-de-la-red)

La consola bash del sistema operativo Raspbian OS (realmente linux debian bookworm) es accesible mediante basicamente dos metodos
* Acceso mediante conexión mediante teclado(USB) y pantalla(HDMI), en este caso no es necesaria tener conectividad de red. Solo hay que loggarse con el usuario "pi" y el password entregado en la tarjeta de claves. Se considera seguro porque solo se permite el acceso local es decir a personas con acceso fisico al dispositivo.
* Acceso mediante SSH y clave privada. A los cronostamper se puede acceder mediante el protocolo ssh al puerto standard mediante la clave privada proporcionada "cronostamper_feet". Existen tres usuario cronos, root y pi todos configurados con la misma clave privada. Se recomienda el uso del usuario "pi" y la ejecución de los comandos privilegiados mediante "sudo" con este usuario.

#### Configuración de la aplicación
Existen varios aspectos configurables en la aplicación mediante la edición del fichero "config.py" contenido en la raiz de la aplicación. Normalmente en la ruta /home/cronos/cronostamper.

* Cambio en el flanco de activación de la señal. Descomentar **solo** la linea de aplicación:
  ```
  #for pulse on open shutter (direct logic)
  ShutterFlange="SHUTTER_LOW"
  #for pulse on close shutter (inverted logic)
  #ShutterFlange="SHUTTER_HIGH"
  ```
* Cambio del nombre/imagen visualizada en la consola web. Modificar la siguiente linea:
  ```
  camera={u'name': u'stamper00', u'jpg': u'moon_big_small.png'}
  ```

## Descrición general
NOTA: Esta sección se corresponde con la última versión del cronostamper. Versiones anteriores pueden tener diferentes hardware/software

### Hardware:
* Raspberry 4 B+
* Modulo GPS UBLOX M6 con generador de pulse per second (PPS)

### Software:
* Sistema operativo: [Raspberry OS Bookworm](https://www.raspberrypi.com/software/)
* Modulos de software principales:
  * [Chrony](https://chrony-project.org/) (NTP daemon)
  * [ZMQ](https://zeromq.org/) (mensajeria)
  * [PIGPIO](https://abyz.me.uk/rpi/pigpio/) (adquisición de señal)
  * La [aplicación cronostamper](https://github.com/nachoplus/cronoStamper) compuesta de varios demonios independientes comunicados entre si mediante ZMQ

### Funcionamiento

Las raspberrys tiene un reloj interno mantenido por un cristal de cuarzo con una precisión tipica del orden de 10 ppm (partes por millón). Esto es suficiente para las aplicaciones habituales incluso para el funcionamiento normal de cualquier PC.

Sin embargo 10ppm significa una deriva de 10 microsegundos por cada segundo (casi un 1 segundo por cada día). Al margen de esta deriva tambien existe la necesidad de sincronizar el tiempo con el tiempo UTC. Estos dos factores invalidan el uso de ordenadores generales para aplicaciones de marca de tiempo UTC de alta precisión.

Para solucionar la situación es necesario sincronizar con una fuente de tiempo externa y disciplinar el reloj interno para evitar su deriva. 

El cronostamper está configurado para actuar como un servidor NTP stratum 0 obteniendo el tiempo UTC de la señal GPS y discipliando su reloj interno utilizando las señal PPS (pulse per second) del modulo GPS.