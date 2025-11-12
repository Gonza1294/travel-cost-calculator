import openrouteservice
import json
import requests
from lxml import html
import re

def obtenerCoordenadas(lugar, client):
    try:
        # Realiza la búsqueda del lugar
        resultado_busqueda = client.pelias_search(text=lugar)

        # Extrae las coordenadas del primer resultado
        coordenadas = resultado_busqueda['features'][0]['geometry']['coordinates']

        return coordenadas
    except Exception as e:
        print(f"Error al obtener coordenadas: {e}")
        return None

def obtener_distancia(origen, destino, client):
    try:
        # Realiza la solicitud de la matriz de distancias
        route = client.directions(coordinates=[origen, destino], profile='driving-car', format='geojson')

        # Extrae la distancia en kilómetros
        distancia_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000

        return distancia_km
    except Exception as e:
        print(f"Error al obtener la distancia: {e}")
        return None

def cargar_datos_vehiculos(ruta_archivo):
    try:
        with open(ruta_archivo, 'r') as archivo:
            datos_vehiculos = json.load(archivo)
        return datos_vehiculos
    except Exception as e:
        print(f"Error al cargar los datos de vehículos desde el archivo: {e}")
        return None

def obtener_datos_vehiculo(vehiculo, datos_vehiculos):
    for vehiculo_data in datos_vehiculos:
        if vehiculo_data['vehiculo'] == vehiculo:
            return vehiculo_data
    return None

def calcular_costo_viaje(distancia_km, datos_vehiculo, iva_porcentaje):
    if distancia_km <= datos_vehiculo.get("umbral_km_inferior", float('inf')):
        tarifa_base = datos_vehiculo.get("tarifa_base")
        costo_por_km_adicional = datos_vehiculo.get("costo_por_km_adicional_inferior", 0)
    else:
        tarifa_base = datos_vehiculo.get("tarifa_base_superior", 0)
        costo_por_km_adicional = datos_vehiculo.get("costo_por_km_adicional_superior", 0)

    comision = datos_vehiculo.get("comision_porcentaje", datos_vehiculo.get("comision", 0))
    comision_total = (tarifa_base * comision) / 100
    costo_sin_iva = tarifa_base + (distancia_km * costo_por_km_adicional) + comision_total
    iva_total = (costo_sin_iva * iva_porcentaje) / 100
    costo_con_iva = costo_sin_iva + iva_total

    return costo_con_iva, comision_total, iva_total



def calcular_costo_viaje_2(distancia_km, datos_vehiculo, iva_porcentaje, precioDiesel):
    #print(f"DISTANCIA:: {distancia_km};; UMBRAL:: {datos_vehiculo.get('umbral_km')}")
    umbral_km = datos_vehiculo.get('umbral')
    

    
    if distancia_km > umbral_km:       
        iva_porcentaje = iva_porcentaje/100 + 1
        tarifa_base_gasoil = round(datos_vehiculo.get('tarifa_base_gasoil') * (round(precioDiesel,2)/iva_porcentaje),2)
        comision = datos_vehiculo.get('comision_largaDistancia')/100

        
        costo_km_sinIva = round(distancia_km * tarifa_base_gasoil, 2)
        #print(f"CostoKMsinIva:: {costo_km_sinIva}")
        comision = round((costo_km_sinIva*comision), 2)
        #print(f"Comision: {comision}")
        iva = round((costo_km_sinIva * iva_porcentaje)-costo_km_sinIva, 2)
        #print(f"IVA: {iva}")

        total_Completo = costo_km_sinIva + iva + comision
        #print(f"TOTAL COMPLETO: {total_Completo}")

        return total_Completo, costo_km_sinIva, comision, iva
    
    else:
        #print("DISTANCIA CORTA")
        iva_porcentaje = iva_porcentaje/100 + 1
        tarifa_base_cortaDistancia = datos_vehiculo.get('tarifa_base_cortaDistancia')
        comision = datos_vehiculo.get('comision_cortaDistancia')/100

        costo_km_sinIva = round(tarifa_base_cortaDistancia, 2)
        #print(f"CostoKMsinIva:: {costo_km_sinIva}")
        comision = round((costo_km_sinIva*comision), 2)
        #print(f"Comision: {comision}")
        iva = round((costo_km_sinIva * iva_porcentaje)-costo_km_sinIva, 2)
        #print(f"IVA: {iva}")

        total_Completo = costo_km_sinIva + iva + comision
        #print(f"TOTAL COMPLETO: {total_Completo}")

        return  total_Completo, costo_km_sinIva, comision, iva



def calcularDiesel():
    gasoil_url = "https://www.dieselogasolina.com/"
    gasoil_xpath = "/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div[3]/div/div[5]/table/tbody/tr[3]/td[2]"
    response = requests.get(gasoil_url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        resultado = tree.xpath(gasoil_xpath)
        precio = ",".join(re.findall(r'\d+\.\d+|\d+', resultado[0].text_content()))
        precio = precio.replace(',', '.')
        #print("Campo extraído:", precio)
        return float(precio)


def main(client, datos_vehiculos):
    #origen = input("Ingrese el lugar de origen: ")
    origen = "Humanes de Madrid"
    origen_coor = obtenerCoordenadas(origen, client)
    
    #destino = input("Ingrese el lugar de destino: ")
    destino = "Barcelona"
    destino_coor = obtenerCoordenadas(destino, client)

    distancia_km = obtener_distancia(origen_coor, destino_coor, client)

    if distancia_km is not None:
        #vehiculo = input("Ingrese el tipo de vehículo (furgoneta, camion, tractora, trailer, mudanza, moto): ")
        vehiculo = "trailer"
        datos_vehiculo = obtener_datos_vehiculo(vehiculo, datos_vehiculos)

        if datos_vehiculo:
            iva_porcentaje = 21  # Puedes ajustar el porcentaje de IVA según tus necesidades
            precioDiesel = calcularDiesel()
            costo_total, costo_sin_iva ,comision_total, iva_total = calcular_costo_viaje_2(distancia_km, datos_vehiculo, iva_porcentaje, precioDiesel)

            print(f"La distancia entre {origen} y {destino} es: {distancia_km:.2f} km")
            print(f"El precio actual del diesel en madrid es de {precioDiesel}€/l")
            print(f"El costo total para el cliente del viaje en {vehiculo} es: {costo_total:.2f}€")
            print(f"(Incluyendo {comision_total:.2f}€ de comisión, {iva_total:.2f}€ de IVA)")
            print(f"El precio sin IVA y sin comision del viaje es {costo_sin_iva:.2f}€")
        else:
            print(f"No se encontraron datos para el vehículo: {vehiculo}")
    else:
        print("No se pudo calcular la distancia.")

if __name__ == "__main__":
    api_key = "openrouteservice_api_key_here"
    client = openrouteservice.Client(key=api_key)
    
    ruta_archivo = "vehiculos"  # Reemplaza con la ruta real de tu archivo JSON
    datos_vehiculos = cargar_datos_vehiculos(ruta_archivo)

    if datos_vehiculos:
        main(client, datos_vehiculos)