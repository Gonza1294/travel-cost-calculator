# Travel Cost Calculator

Calculadora de costes de viaje en carretera basada en la API de **OpenRouteService**.

## 🧩 Descripción
Este script permite calcular la distancia y el coste total de un trayecto entre dos lugares.  
Utiliza las coordenadas reales proporcionadas por OpenRouteService y aplica un modelo de precios configurable según el tipo de vehículo (definido en el archivo `vehiculos`).

## ⚙️ Requisitos
- Python 3.8 o superior
- Librerías necesarias:
  - openrouteservice
  - requests
  - lxml

Instálalas con:
```bash
pip install openrouteservice requests lxml
```

## ▶️ Uso
1. Asegúrate de tener una **API key** de OpenRouteService.
2. Modifica el archivo `vehiculos` con tus tipos de vehículo y tarifas.
3. Ejecuta el script:

```bash
python main.py
```

Introduce el origen y destino cuando el programa lo pida.

## 📊 Resultados
El programa mostrará:
- Distancia entre origen y destino (km)
- Tarifa base
- Comisión e IVA aplicados
- Coste total del viaje

## 🧠 Notas
- El archivo `vehiculos` contiene las tarifas, comisiones y parámetros de cada tipo de vehículo.
- La API key debe configurarse dentro del script (o mediante variable de entorno si lo prefieres).

## 📜 Licencia
MIT
