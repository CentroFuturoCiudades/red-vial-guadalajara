# red-vial-guadalajara
Construcción de la red en VISUM

## USEFUL ‼️
- HIGHWAY tags nomenclature: https://wiki.openstreetmap.org/wiki/Key:highway 

## Cleaning Files
Cleaning of input files for Visum Net
- add_FromNode_toNode_toLinks: adding fromNode & toNode to Links ✅
- get_BRT_LinksAndLR: reading input LineRoutes & StopPoints (see which ones have no sequence)
- Remove_MetroFragments_RedIMEPLAN: attempt to remove links for Tren Ligero (TIPO=18) from original links but abandoned that idea
  
## Comparing with OSM
- insertingSP_Metro: insert SP of Tren Ligero in Visum ✅ (fall directly on nodes)
- osm_comparisson: 1st attempt to get graph from OSMNX
- redOSMNX_withLimits: get graph from OSMNX (vial & tren ligero) with delimiting AMG polygon from IMEPLAN ✅
- redOSMNX: get graph from OSMNX (vial & tren ligero) 1st attemp with municipalities names & re-assignation of IDs ✅
  
## Import PuT
- import_SP_LineRoutes: import SP & LR to Visum (original IMEPLAN 2024 net) ✅ 
