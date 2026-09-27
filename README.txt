CC3501 - Tarea 1: Perlin Peak

REQUISITOS Y EJECUCIÓN
Python 3.11 o superior, uv y soporte para OpenGL 3.3 o superior.
Desde esta carpeta:

    uv sync --locked
    uv run --locked python tarea1.py

La primera sincronización puede necesitar Internet para descargar dependencias.
Los shaders se buscan respecto de los archivos del proyecto.

CONTROLES
W/S: avanzar y retroceder.
A/D: desplazarse lateralmente.
Mouse: orientar la cámara.
1: alternar entre superficies rellenas y wireframe.
Escape: cerrar la ventana.

IMPLEMENTACIÓN
El terreno se genera con Perlin Noise en chunks de 25 x 25 cuadrados, con
normales para la iluminación y nieve según la altura. Se mantienen activos el
chunk bajo la cámara y sus ocho vecinos. Al cambiar de chunk se reconstruyen los nueve.

El bonus implementado es el sol orbital a distancia constante de la cámara.
La geometría del disco se crea en terrain.py. El cálculo de su transformación
está en tarea1.py y se actualiza desde update(). La órbita tiene un período de
30 segundos, distancia de 60 unidades y fase inicial de 0.2 radianes. Su plano
YZ mantiene la orientación de los ejes del mundo, mientras su centro acompaña
la posición de la cámara. El disco se orienta hacia ella.

Durante la vuelta, el sol puede quedar detrás de la cámara o bajo el terreno.
La distancia constante no significa que deba permanecer visible en pantalla.

USO DE IA
El alcance de la asistencia está descrito en DECLARACION_USO_IA.txt.
