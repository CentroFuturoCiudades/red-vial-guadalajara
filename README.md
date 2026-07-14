# red-vial-guadalajara
Construcción de la red en VISUM

## USEFUL ‼️
- HIGHWAY tags nomenclature: https://wiki.openstreetmap.org/wiki/Key:highway 

## Cleaning Files (no longer used)
Cleaning of given TransCAD Network Files
- add_FromNode_toNode_toLinks: adding fromNode & toNode to TransCAD Links ✅
- get_BRT_LinksAndLR: reading input LineRoutes & StopPoints (see which ones have no sequence)
  
## Comparing with OSM
- insertingSP_Metro: insert SP of Tren Ligero in Visum ✅ (fall directly on nodes)
- osm_comparisson: 1st attempt to get graph from OSMNX
- redOSMNX_withLimits: get graph from OSMNX (vial & tren ligero) with delimiting AMG polygon from IMEPLAN ✅
- redOSMNX: get graph from OSMNX (vial & tren ligero) 1st attemp with municipalities names & re-assignation of IDs ✅
  
## Import PuT
- import_SP_LineRoutes: import SP & LR to Visum (original IMEPLAN 2024 net) ✅ 
