**Robot CNC para Caracterización de Antenas**

Este proyecto implementa una interfaz de control por consola para un robot CNC diseñado para la caracterización de antenas. El sistema permite mover los ejes de manera manual o automática, ejecutar recorridos predefinidos, y mostrar en tiempo real la posición y estado del robot.

**🚀 Características principales**

Menú interactivo en consola (navegable con flechas ↑/↓ y tecla Enter).

Control de los ejes:

X, Y (lineales, en mm).

Phi, Theta (rotacionales, en grados).

Modos de movimiento:

Relativo (desplazamientos incrementales).

Absoluto (posición destino).

Referencia de ejes (llevar a posición inicial segura).

Recorridos esféricos para mediciones circulares en torno a un punto.

Recorridos automáticos cargados desde archivos .txt en la carpeta /routes. (No implementado)

**Visualización en tiempo real de:**

Posiciones actuales de los ejes respecto al punto.

Coordenadas relativas al origen, a la fuente y a los topes.

Radio calculado respecto a la fuente.

**Ejecución**

Encender el robot y conectarse al router de la misma red del robot

Ejecutar en la terminal

**ssh debian@192.168.0.10**

Password:temppwd

Una vez adentro ejecutar comando **robot**

Esto ejecutará **sudo python ~/mmlab/robot_anecoica/main.py**

Se deberia desplegar una GUI en la terminal autoexplicativa, que contiene lo descrito anteriormente

**📝 Notas de uso**

**Límites de operación:**

El robot no está diseñado para alcanzar sus límites físicos de manera segura. Si durante la operación se observa que alguno de los ejes se aproxima a los bordes de su recorrido, se debe apagar manualmente de inmediato para evitar daños.

**Movimientos recomendados:**

Realizar siempre desplazamientos pequeños:

Menores a 1 metro en los ejes lineales.

Menores a 20 grados en los ejes angulares.
El sistema no está pensado para ejecutar movimientos de gran magnitud en distancia ni en ángulo.

**Apagado de emergencia:**

En caso de un apagado de emergencia, es necesario recalcular los parámetros contenidos en el archivo robotPosData.ini antes de volver a operar.

**Parámetros iniciales:**

Al inicio de main.py se definen parámetros que dependen del tipo de fuente utilizada. Estos valores son fundamentales para calcular correctamente la posición relativa del receptor respecto a la fuente, ver la imagen de mas abajo.

**Parametros de los motores en confiRobot.txt:**

Los parámetros contenidos en confiRobot.txt fueron obtenidos mediante fotogrametría y mediciones directas, por lo que no deben modificarse.
Cualquier ajuste o cambio en estos valores solo debe realizarse si existe un método de cálculo más preciso y validado que justifique la modificación.

Notas de los calculos

<img width="940" height="788" alt="Movimiento esferico" src="https://github.com/user-attachments/assets/f84f7018-9a31-4bdf-ab77-1145c445595c" />
