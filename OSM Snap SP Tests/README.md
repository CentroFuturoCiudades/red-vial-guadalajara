# OSM Snap Stop Points (Bus) Tests (1st attempt)

- lee los stop points (Insumos IMEPLAN/Transporte Publico/amg_estategia_puntos_de_parada/AMG_estrategia_de_puntos_de_parada_de_transporte_publico_A04) que paso Daniel Rodríguez (IMEPLAN) 
- los snappea al nearest link usando los links del grafo directamente descargado de OSMNX (__mal porque al importar a Visum se agregan links__)
- analiza cuales deben ir a service links y living streets

## Primera idea del pipeline pero el error fue usar el grafo de OSMNX previo a la importación a Visum

## Versión corregida y final en Import Put -> OSM Visum Network -> 01_Snap_Bus_StopPoints
- Este hace algo similar pero usando la el grafo de visum para hacer el snap al nearest link