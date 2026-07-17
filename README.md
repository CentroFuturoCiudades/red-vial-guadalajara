# red-vial-guadalajara
Construcción de la red en VISUM

## USEFUL Documentation‼️
- HIGHWAY tags nomenclature: https://wiki.openstreetmap.org/wiki/Key:highway
- OSMNX functions: https://osmnx.readthedocs.io/en/stable/user-reference.html

## Cleaning Files (no longer used) ❌
Cleaning of given TransCAD Network Files
- add_FromNode_toNode_toLinks: adding fromNode & toNode to TransCAD Links
- get_BRT_LinksAndLR: reading input LineRoutes & StopPoints (see which ones have no sequence)

## Import PuT 🚝Ⓜ️
TransCAD-based Visum Network ❌ (for ref. only)
- importing_SP_LineRoutes_TransCAD: creating SP & Line Route Objects in old TransCAD-based Visum network based on insumos IMEPLAN (just as a reference for how to create PuT objects)❗️
Current OSMNX Visum Network ✅
- 01_Snap_Bus_StopPoints: snap/find bus stop points (AMG_estrategia_de_puntos_de_parada_de_transporte_publico_A04) to nearest link using Visum links
- 02_Import_Bus_SP_Visum: create SP objects on Visum

## OSM Snap SP Tests ❌
- 01_OSM_Graph_Snap_Bus_Stops: snap/find bus stop points (AMG_estrategia_de_puntos_de_parada_de_transporte_publico_A04) to nearest link using OSM graph (prior to Visum import, is not exactly the same as post Visum import network)
- 02_OSM_Snapped_Stops_Analysis: analysis of snapped stops to OSM graph
  
## OSM-OSMNX ✅
- redOSMNX_withLimits: download graph from OSMNX (vial & tren ligero) with delimiting AMG polygon from IMEPLAN 
- insertingSP_Metro: insert SP of Tren Ligero in Visum (fall directly on nodes)
- add_TALA_municipality: download TALA network and inserting it on Visum already existing network (connectivity is manual)
  
## Updating Network ✅
- 01_velocidadesBuffer: give Capacity & Speed Limit attributes from TransCAD to OSM links where geometries match (only main avenues)
- 02_propagar_CapV0: longitudinal propagation to fill all avenues with the same name with the same Capacity & Speed attrs.
- 03_connectorTransfer: get the Capacity & Speed Limit atts for connectors (salidas, entradas, retornos) & Laterales from TransCAD main avenues and transfer them to OSM connectors on main avenues.
