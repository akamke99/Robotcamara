Robot CNC para Caracterización de Antenas

Este proyecto implementa una interfaz de control por consola para un robot CNC diseñado para la caracterización de antenas. El sistema permite mover los ejes de manera manual o automática, ejecutar recorridos predefinidos, y mostrar en tiempo real la posición y estado del robot.

🚀 Características principales

Menú interactivo en consola (navegable con flechas ↑/↓ y tecla Enter).

Control de los ejes:

X, Y (lineales, en mm).

Phi, Theta, Gamma (rotacionales, en grados).

Modos de movimiento:

Relativo (desplazamientos incrementales).

Absoluto (posición destino).

Referencia de ejes (llevar a posición inicial segura).

Recorridos automáticos cargados desde archivos .txt en la carpeta /routes.

Recorridos esféricos para mediciones circulares en torno a un punto.

Visualización en tiempo real de:

Posiciones actuales de los ejes.

Coordenadas relativas al origen y a la fuente.

Radio calculado respecto a la fuente.

Acción en curso.
<img width="940" height="788" alt="Movimiento esferico" src="https://github.com/user-attachments/assets/f84f7018-9a31-4bdf-ab77-1145c445595c" />
