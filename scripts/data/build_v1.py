"""Reproducible B1 pipeline. Originals are immutable; all writes are B1-owned."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import sys

from inspect_datasets import ROOT, sha256, tables
from build_municipal_context import BOOKS as MUNICIPAL_BOOKS, build_context

META = ROOT / 'data/metadata'
INTER = ROOT / 'data/intermediate'
OUT = ROOT / 'data/processed/v1'
DOC = ROOT / 'docs/data'
CONTRACT = ROOT / 'data/contracts'
SCOPE = {'Celaya': '007', 'Irapuato': '017'}
CORE_NAME = 'irapuato_celaya_dataset_ml_geoespacial (2).xlsx'
RENAME = {'CVEGEO': 'id', 'MUN': 'municipality_code', 'NOM_MUN': 'municipality',
          'LOC': 'locality_code', 'NOM_LOC': 'locality', 'LONGITUD': 'longitude',
          'LATITUD': 'latitude', 'ALTITUD': 'altitude_m'}
INTEGER_CORE = {'CVEGEO', 'MUN', 'LOC', 'ALTITUD', 'POBTOT', 'POB15_64', 'PEA',
                'POCUPADA', 'VIVTOT', 'TVIVHAB', 'FRECUENCIA_EST_2014',
                'TIEMPO_EST_MIN_2014', 'RIESGO_INUNDACION_2014', 'RIESGO_SEQUIA_2014',
                'RIESGO_HELADA_2014', 'RIESGO_INCENDIO_2014', 'MUNICIPIO_OBJETIVO'}
STATE_EXTRA = ['VPH_C_ELEC', 'VPH_S_ELEC', 'VPH_AGUADV', 'VPH_DRENAJ', 'VPH_NODREN',
               'VPH_AUTOM', 'TRANSPRIN_2014', 'FRECUENCIA_2014', 'TIEMPO_2014',
               'DRENAJECOB_2014', 'ALUMBCOB_2014', 'RECUBCOB_2014',
               'INUNDACION_2014', 'SEQUIA_2014', 'HELADA_2014', 'INCENDIO_2014',
               'TEMBLOR_2014', 'CICLON_2014', 'RIESGO_TEMBLOR_2014',
               'RIESGO_CICLON_2014', 'MATCH_LOCALIDADES_2014']


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        value = value.encode('utf-8')
    # Atomic replacement for generated files only; never called on incoming or raw.
    temp = path.with_name('.' + path.name + '.b1.tmp')
    temp.write_bytes(value)
    temp.replace(path)


def dump(path, obj):
    put(path, json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    put(path, stream.getvalue())


def read_sheet(path, title):
    for name, rows in tables(path):
        if name == title:
            assert len(set(rows[0])) == len(rows[0]), 'Duplicate column names'
            return [dict(zip(rows[0], row)) for row in rows[1:]]
    raise ValueError(f'Missing sheet {title}: {path}')


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-10)
    return a == b


def immutable_copy(profile, municipality):
    source = ROOT / profile['path']
    dest = ROOT / 'data/raw' / municipality / source.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    assert sha256(source) == profile['sha256'], f'Input changed: {source}'
    if dest.exists():
        if sha256(dest) != profile['sha256']:
            raise ValueError(f'RAW_CONFLICT: {dest}; original is never overwritten')
    else:
        # Exclusive creation prevents overwriting another process's raw copy.
        with source.open('rb') as src, dest.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    assert sha256(dest) == profile['sha256']
    return dest


def policy(p):
    name = p['name']
    common = dict(source='UNKNOWN', date='UNKNOWN', temporal_scope='UNKNOWN',
                  crs='CRS_UNKNOWN', municipality='UNKNOWN', coverage='UNKNOWN',
                  status='PENDING_INSPECTION', usage='NO_OPERATIONAL_USE',
                  limitations='Unclassified input; requires manual policy review.', raw_area=None)
    if name in [CORE_NAME, 'irapuato_celaya_dataset_ml_geoespacial (1).xlsx']:
        common.update(source='INEGI declarado por libro; compilación entregada por equipo',
                      temporal_scope='2020/2014; fecha vectorial UNKNOWN',
                      municipality='Irapuato;Celaya', coverage='755 localidades',
                      crs='Coordenadas CRS_UNKNOWN; distancias EPSG:6372 declarado',
                      status='CANONICAL_SOURCE' if name == CORE_NAME else 'EXACT_DUPLICATE',
                      usage='LOCALITY_ANALYSIS' if name == CORE_NAME else 'RETAIN_ONLY',
                      limitations='No geometrías originales ni script original de distancias; datum de coordenadas no identificado; sin variable objetivo ML.',
                      raw_area='shared' if name == CORE_NAME else None)
    elif name in {filename for _, filename, _ in MUNICIPAL_BOOKS}:
        common.update(source='UNKNOWN: compilación municipal entregada por equipo',
                      temporal_scope='UNKNOWN; años incluidos en nombres de indicadores no autentican la fuente',
                      municipality='Irapuato;Celaya', coverage='755 localidades; indicadores constantes por municipio',
                      status='PARTIAL', usage='MUNICIPAL_CONTEXT', raw_area='municipal_context',
                      limitations='Indicadores municipales repetidos por localidad; no son mediciones del predio, amenaza local ni condición actual validada. Fuente original, fecha y licencia pendientes.')
    elif name == 'guanajuato_dataset_ml_limpio.xlsx':
        common.update(source='INEGI declarado; fuentes censales listadas en libro',
                      temporal_scope='2014/2015/2020', municipality='46 municipios; MVP filtra 007 y 017',
                      coverage='Guanajuato; extracción MVP validada por CVEGEO',
                      status='PARTIAL', usage='FILTERED_LOCALITY_ENRICHMENT',
                      limitations='EIC2015 tiene tres indicadores siempre cero: no utilizados. Manzanas sin geometría no se unen a localidades. CRS censal no identificado.', raw_area='shared')
    elif name.startswith('Clima_') and name in ['Clima_Celaya_2024_2026.xlsx','Clima_Irapuato_2024_2026.xlsx']:
        mun = 'Celaya' if 'Celaya' in name else 'Irapuato'
        common.update(source='CSV aportados por usuario; institución/URL UNKNOWN',
                      temporal_scope='2024-01 a 2026-01, mensual', municipality=mun,
                      coverage='Una estación puntual por municipio; 25 meses únicos',
                      status='PARTIAL', usage='CONTEXT_ONLY',
                      limitations='Marzo 2025 repetido con distinto archivo de origen; no superficie homogénea, temperatura ausente, institución y datum sin verificar.', raw_area=mun.lower())
    elif name == '02_terreno_DEM_Irapuato_Celaya.xlsx':
        common.update(source='UNKNOWN: tabla derivada entregada por equipo',
                      temporal_scope='Fecha de valores DEM/pendiente UNKNOWN; altitud censal coincide con maestro',
                      municipality='Irapuato;Celaya', coverage='755 puntos; no ráster', status='PARTIAL',
                      usage='EXPERIMENTAL_REFERENCE_ONLY',
                      limitations='No identifica fuente DEM, resolución, datum vertical, fecha ni algoritmo. Pendiente no validada; rugosidad ausente. Excluido de análisis V1.', raw_area='shared')
    elif name.startswith('subcuencas_') and name in ['subcuencas_Guanajuato_RNA(1).xlsx','subcuencas_hidrograficas_RNA(2).xlsx']:
        national = 'hidrograficas' in name
        common.update(source='INEGI/CONABIO declarado en libro nacional; redsub84gw.zip',
                      coverage='México' if national else '23 subcuencas reportadas para Guanajuato',
                      crs='EPSG:4326 declarado' if national else 'CRS_UNKNOWN', status='PARTIAL',
                      usage='REFERENCE_ONLY', limitations='GEOMETRY_LIMITATION: faltan polígonos; puntos representativos/BBOX no permiten asignación municipal precisa.', raw_area='shared')
    elif name == 'datos_ferroviarios_para_RNA(2).xlsx':
        common.update(source='Institución no declarada en libro; UNKNOWN', date='2025-07-18 (FECHA_ACT)',
                      temporal_scope='2025-07-18', coverage='México',
                      crs='EPSG:6372 original; EPSG:4326 derivado (declarados)', status='PARTIAL',
                      usage='REFERENCE_ONLY', limitations='No municipio ni líneas completas; sin límites municipales no se publica filtro espacial aproximado. Fuente/licencia sin identificar.', raw_area='shared')
    elif name in ['uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx','uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx']:
        common.update(source='INEGI declarado en README interno',
                      temporal_scope='Serie I histórica, año UNKNOWN' if 'serie_I_historico' in name else 'Serie IV, año UNKNOWN; no condición actual verificada',
                      coverage='Cartas F14-7/F14-8', status='PARTIAL', usage='REFERENCE_ONLY',
                      limitations='GEOMETRY_LIMITATION: faltan geometrías de polígonos. DMS en puntos Serie IV con datum no declarado. No asignar uso de suelo a localidades.', raw_area='shared')
    return common


def normalized_core(core, state):
    state = {str(r['CVEGEO']).zfill(9): r for r in state if r['NOM_MUN'] in SCOPE}
    assert len(state) == 755
    result = []
    for raw in core:
        assert raw['NOM_MUN'] in SCOPE
        key = str(raw['CVEGEO']).zfill(9)
        ref = state[key]
        assert str(raw['MUN']).zfill(3) == SCOPE[raw['NOM_MUN']]
        assert key == '11' + SCOPE[raw['NOM_MUN']] + str(raw['LOC']).zfill(4)
        for name, val in raw.items():
            if name in ref and name not in ['CVEGEO','MUN','LOC']:
                assert same(val, ref[name]), f'Cross-source conflict: {key}/{name}'
        row = {}
        for name, val in raw.items():
            field = RENAME.get(name, name.lower())
            if name in ['CVEGEO', 'MUN', 'LOC']:
                val = str(val).zfill({'CVEGEO':9, 'MUN':3, 'LOC':4}[name])
            elif val is not None and name in INTEGER_CORE:
                assert int(val) == val
                val = int(val)
            elif val is not None and not isinstance(val, str):
                val = float(val)
            row[field] = val
        for name in STATE_EXTRA:
            row[name.lower()] = ref[name]
        row.update(analysis_unit='locality', coordinate_crs='CRS_UNKNOWN',
                   source_id='core_geospatial', supplement_source_id='statewide_census')
        assert -180 <= row['longitude'] <= 180 and -90 <= row['latitude'] <= 90
        assert all(v is None or v >= 0 for k,v in row.items() if k.startswith('dist_'))
        result.append(row)
    assert Counter(r['municipality'] for r in result) == {'Celaya':321,'Irapuato':434}
    assert len({r['id'] for r in result}) == len(result) == 755
    return sorted(result, key=lambda r:r['id'])


def climate(paths):
    groups = defaultdict(list)
    original = []
    for mun, path in paths:
        for row in read_sheet(path, 'Precipitacion_mensual'):
            assert row['CLAVE'] == {'Celaya':'CLYGJ','Irapuato':'IRPGJ'}[mun]
            assert row['PERIODO'] == f"{row['ANIO']:04d}-{row['MES']:02d}"
            assert row['PRECIPITACION_MM'] is None or row['PRECIPITACION_MM'] >= 0
            assert -180 <= row['LONGITUD'] <= 180 and -90 <= row['LATITUD'] <= 90
            row['municipality'] = mun
            original.append(row)
            groups[(row['CLAVE'],row['PERIODO'])].append(row)
    output = []
    for (station, period), rows in sorted(groups.items()):
        first = rows[0]
        # Consolidate only an identical station-period observation; conflicting values abort.
        for row in rows:
            assert all(same(row[f],first[f]) for f in first if f!='ARCHIVO_ORIGEN'), 'Climate conflict'
        output.append(dict(station_id=station, station_name=first['ESTACION'],
                           municipality=first['municipality'], period=period, year=first['ANIO'],
                           month=first['MES'], longitude=first['LONGITUD'], latitude=first['LATITUD'],
                           precipitation_mm=first['PRECIPITACION_MM'],
                           origin_files=';'.join(sorted({r['ARCHIVO_ORIGEN'] for r in rows})),
                           original_rows=len(rows), source_id='climate_'+first['municipality'].lower(),
                           coordinate_crs='CRS_UNKNOWN', usage='CONTEXT_ONLY'))
    return original, output


def field_info(name, values, original):
    present = [v for v in values if v is not None]
    typ = 'string' if present and isinstance(present[0],str) else 'integer' if present and all(isinstance(v,int) for v in present) else 'number'
    unit, meaning, temporal, role, limit = 'UNSPECIFIED', original, 'UNKNOWN', 'context', 'No extrapolar fuera de la unidad de localidad.'
    source = 'core_geospatial' if original not in STATE_EXTRA else 'statewide_census'
    if name in ['id','municipality_code','municipality','locality_code','locality']:
        unit,meaning,temporal,role = 'not_applicable', {'id':'Clave CVEGEO de localidad, 9 caracteres','municipality_code':'Clave municipal de 3 caracteres: 007/017','municipality':'Nombre municipal','locality_code':'Clave de localidad de 4 caracteres','locality':'Nombre censal de localidad'}[name], '2020', 'identifier'
    elif name in ['latitude','longitude']:
        unit, meaning, temporal, role = 'decimal_degrees', 'Coordenada de localidad recibida en grados decimales; no reproyectada', '2020', 'location'
        limit = 'Datum original y método de conversión pendientes; CRS_UNKNOWN. No declarar EPSG:4326.'
    elif name=='altitude_m':
        unit,meaning,temporal,role='m','Altitud censal de la localidad respecto al nivel medio del mar (ITER 2020)','2020','terrain_context'
        limit='No equivale a un DEM ni a elevación precisa del predio; no derivar pendiente de puntos censales.'
    elif name.startswith('dist_'):
        unit,meaning,role='m','Distancia euclidiana precalculada a '+name[5:-2].replace('_',' '),'infrastructure_context'
        limit='EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial.'
    elif name.startswith('riesgo_'):
        unit,meaning,temporal,role='binary_code','Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato','2014','historical_damage'
        limit='Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad.'
    elif original in ['INUNDACION_2014','SEQUIA_2014','HELADA_2014','INCENDIO_2014','TEMBLOR_2014','CICLON_2014']:
        unit,meaning,temporal,role='category','Etiqueta de daño histórico original: Con daño / Sin daño','2014','historical_damage'
        limit='Daño histórico reportado; no condición actual ni etiqueta ML validada.'
    elif name.startswith('pob') or name in ['pea','pocupada']:
        unit,temporal='persons','2020'
        meaning={'pobtot':'Población total','pob15_64':'Población de 15 a 64 años','pea':'Población económicamente activa','pocupada':'Población ocupada'}.get(name,original)
    elif name in ['vivtot','tvivhab'] or name.startswith('vph_'):
        unit,temporal='dwellings','2020'
        meaning={'vivtot':'Viviendas totales','tvivhab':'Viviendas habitadas','vph_c_elec':'Viviendas particulares habitadas con electricidad','vph_s_elec':'Viviendas particulares habitadas sin electricidad','vph_aguadv':'Viviendas particulares habitadas con agua entubada según variable ITER','vph_drenaj':'Viviendas particulares habitadas con drenaje','vph_nodren':'Viviendas particulares habitadas sin drenaje','vph_autom':'Viviendas particulares habitadas con automóvil'}.get(name,original)
    elif name in ['cob_electrica','cob_drenaje','autos_por_100_viv']:
        temporal='2020'
        unit='ratio_0_1' if name.startswith('cob_') else 'per_100_dwellings'
        meaning='Indicador derivado de disponibilidad de servicios o automóvil en viviendas'
        limit='No es amenaza ni índice de calidad estructural; denominadores reproducidos del archivo estatal.'
    elif name.endswith('_2014'):
        temporal='2014'
        if 'score' in name:
            unit='ordinal_score_0_1'; meaning='Codificación ordinal preexistente de cobertura descrita en etiqueta original';limit='No porcentaje medido ni probabilidad; escala heredada, no diseñada por ATLAS.'
        elif name=='tiempo_est_min_2014':
            unit='minutes_approximate'; meaning='Tiempo aproximado ya derivado de categoría de transporte'
        elif name=='frecuencia_est_2014':
            unit='estimated_departures'; meaning='Frecuencia ya aproximada a partir de intervalos categóricos';limit='Periodicidad exacta debe confirmarse con cuestionario fuente; no frecuencia medida.'
        elif name=='match_localidades_2014':
            unit='binary_code';meaning='Coincidencia de clave en la unión censal original, 1=sí/0=no'
        else: unit='category';meaning='Categoría original: '+original
    elif name=='municipio_objetivo':
        unit,meaning='binary_code','Marcador original de pertenencia al subconjunto recibido; siempre 1'
    else:
        unit='not_applicable';meaning={'analysis_unit':'Unidad soportada: locality','coordinate_crs':'CRS declarado o CRS_UNKNOWN','source_id':'Dataset fuente del maestro','supplement_source_id':'Dataset fuente de las variables complementarias'}.get(name,name)
        source='pipeline_v1';role='metadata'
    return dict(name=name,type=typ,unit=unit,nullable=any(v is None for v in values),
                meaning=meaning,source=source,original_field=original,temporal_scope=temporal,
                coverage='Irapuato/Celaya; 755 localidades',available_records=len(present),
                missing_records=len(values)-len(present),role=role,limitations=limit)


def main():
    profiles=json.loads((META/'inventory.json').read_text())
    incoming_files={str(p.relative_to(ROOT)) for p in (ROOT/'data/incoming').rglob('*') if p.is_file() and p.name!='.gitkeep'}
    assert incoming_files == {p['path'] for p in profiles}, 'New arrivals: rerun inventory before publication'
    by_name={p['name']:p for p in profiles}
    # A repeated basename in different reception folders requires an explicit resolution.
    assert len(by_name)==len(profiles), 'Repeated original filename in incoming'
    core_profile=by_name[CORE_NAME]
    duplicate=by_name['irapuato_celaya_dataset_ml_geoespacial (1).xlsx']
    assert core_profile['sha256']==duplicate['sha256']
    assert [(s['name'],s['semantic_sha256']) for s in core_profile['sheets']] == [(s['name'],s['semantic_sha256']) for s in duplicate['sheets']]
    raw={}
    registry=[]
    ids={CORE_NAME:'core_geospatial',duplicate['name']:'core_exact_duplicate',
         'guanajuato_dataset_ml_limpio.xlsx':'statewide_census',
         '02_terreno_DEM_Irapuato_Celaya.xlsx':'terrain_candidate',
         'Clima_Celaya_2024_2026.xlsx':'climate_celaya','Clima_Irapuato_2024_2026.xlsx':'climate_irapuato',
         'subcuencas_Guanajuato_RNA(1).xlsx':'subbasins_state',
         'subcuencas_hidrograficas_RNA(2).xlsx':'subbasins_national',
         'datos_ferroviarios_para_RNA(2).xlsx':'rail_national',
         'uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx':'landuse_series_i',
         'uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx':'landuse_series_iv'}
    ids.update({filename: source_id for source_id, filename, _ in MUNICIPAL_BOOKS})
    for p in profiles:
        pol=policy(p)
        if p['error']:pol.update(status='PENDING_INSPECTION',raw_area=None,limitations=p['error'])
        rawpath=immutable_copy(p,pol['raw_area']) if pol['raw_area'] else None
        if rawpath:raw[p['name']]=rawpath
        main_sheets=[s for s in p['sheets'] if s['name'] not in ['Resumen','Diccionario','Notas','Fuentes','README','Notas_metodologicas']]
        registry.append(dict(dataset_id=ids.get(p['name'],'new_'+p['sha256'][:12]),dataset_name=p['name'],
                             source=pol['source'],original_file=p['path'],category=p['path'].split('/')[2],
                             format=p['format'],municipality=pol['municipality'],coverage=pol['coverage'],date=pol['date'],
                             temporal_scope=pol['temporal_scope'],crs=pol['crs'],
                             records=sum(s['records'] for s in main_sheets),status=pol['status'],usage=pol['usage'],
                             limitations=pol['limitations'],sha256=p['sha256'],bytes=p['bytes'],
                             sheets=';'.join(s['name'] for s in p['sheets']),raw_file=str(rawpath.relative_to(ROOT)) if rawpath else '',
                             download_date='UNKNOWN',license_or_terms='PENDING_SOURCE_PROVENANCE'))
    write_csv(META/'dataset_registry.csv',registry)
    write_csv(META/'source_manifest.csv',[dict(source_id=r['dataset_id'],file_name=r['dataset_name'],institution=r['source'],
              source_year=r['temporal_scope'],download_date=r['download_date'],coverage=r['coverage'],crs=r['crs'],
              geometry_type='Tabular; no polygon geometry',license_or_terms=r['license_or_terms'],status=r['status'],
              processing_script='scripts/data/build_v1.py',limitations=r['limitations'],sha256=r['sha256']) for r in registry])
    core=read_sheet(raw[CORE_NAME],'Dataset_ML')
    state=read_sheet(raw['guanajuato_dataset_ml_limpio.xlsx'],'Localidades_ML')
    state_mvp=[r for r in state if r['NOM_MUN'] in SCOPE]
    write_csv(INTER/'core_original.csv',core)
    write_csv(INTER/'statewide_localities_mvp.csv',state_mvp)
    units=normalized_core(core,state)
    # Verify binary history against original labels: inherited "RIESGO" names encode damage.
    for r in units:
        for event in ['inundacion','sequia','helada','incendio','temblor','ciclon']:
            code=r[f'riesgo_{event}_2014']; label=r[f'{event}_2014']
            assert label == ({0:'Sin daño',1:'Con daño'}.get(code))
        for ratio,count in [('cob_electrica','vph_c_elec'),('cob_drenaje','vph_drenaj')]:
            if r[ratio] is not None:assert same(r[ratio],r[count]/r['tvivhab'])
        if r['autos_por_100_viv'] is not None:assert same(r['autos_por_100_viv'],100*r['vph_autom']/r['tvivhab'])
    original_climate,monthly=climate([(mun,raw[f'Clima_{mun}_2024_2026.xlsx']) for mun in SCOPE])
    write_csv(INTER/'climate_received_rows.csv',original_climate)
    terrain=read_sheet(raw['02_terreno_DEM_Irapuato_Celaya.xlsx'],'Datos')
    write_csv(INTER/'terrain_candidate_unvalidated.csv',terrain)
    by_id={str(r['CVEGEO']).zfill(9):r for r in terrain}
    assert len(by_id)==len(units)
    for r in units:
        t=by_id[r['id']]
        for key,tk in [('municipality','NOM_MUN'),('locality','NOM_LOC'),('latitude','LATITUD'),('longitude','LONGITUD'),('altitude_m','ALTITUD')]:
            assert same(r[key],t[tk]), f'Terrain identity mismatch {r["id"]}/{key}'
        assert t['DIF_ALTITUD_CENSO_DEM_M']==t['ALTITUD']-t['ELEVACION_DEM_M']
    dictionary=[]
    inverse={v:k for k,v in RENAME.items()}
    for field in units[0]:
        original=inverse.get(field,field.upper())
        dictionary.append(field_info(field,[r[field] for r in units],original))
    layers=[]
    for f in dictionary:
        if f['role'] in ['identifier','location','metadata']:continue
        layers.append(dict(code=f['name'],title=f['meaning'],category=f['role'],source_id=f['source'],
                           date=f['temporal_scope'],crs='EPSG:6372 (distance computation declared)' if f['name'].startswith('dist_') else 'CRS_UNKNOWN',
                           coverage=f['coverage'],unit=f['unit'],limitation=f['limitations'],
                           status='AVAILABLE' if f['missing_records']==0 else 'PARTIAL',available=f['available_records'],expected=755,
                           analysis_unit='locality',continuous_geometry=False))
    pending=[('dem','PENDING','No raster; 755-point table has no source, resolution, date or algorithm.'),
             ('dem_elevation','PARTIAL','Values present for 755 points but unvalidated; not published as usable DEM elevation.'),
             ('slope','PENDING','Derived values present; source/resolution/algorithm missing; do not use operationally.'),
             ('roughness','PENDING','No roughness column or raster.'),
             ('geology_faults','PENDING','No fault/fracture geometry received.'),
             ('landslides','PENDING','No susceptibility geometry received.'),
             ('anp','PENDING','No protected-area geometry received.'),
             ('modern_flood_surface','PENDING','Historical 2014 damage is not a modern flood surface.'),
             ('precipitation','PARTIAL','CONTEXT_ONLY: 2 stations/25 months; institution/CRS unverified.'),
             ('precipitation_spatial','PENDING','No validated homogeneous spatial precipitation layer.'),
             ('temperature','PENDING','No temperature column in received climate workbooks.'),
             ('soils','PENDING','No complete soil dataset received.'),
             ('potential_land_use','PENDING','No potential-land-use dataset received.'),
             ('landuse_current','PENDING','Series I/IV attributes do not establish current point coverage without geometries.'),
             ('subbasin_assignment','PENDING','GEOMETRY_LIMITATION: representative point/BBOX is not a polygon.')]
    availability=[dict(code=c,status=s,reason=r) for c,s,r in pending]
    dump(META/'field_dictionary.json',dictionary)
    dump(META/'availability.json',availability)
    dump(META/'duplicate_comparison.json',dict(canonical=core_profile['path'],duplicate=duplicate['path'],sha256=core_profile['sha256'],
          bytes_equal=True,sha256_equal=True,sheet_content_equal=True,internal_metadata_equal=core_profile['workbook_metadata']==duplicate['workbook_metadata'],
          decision='Use (2) only after exact comparison; both incoming files retained.'))
    # Validate the municipal extension before publishing products. Read only raw
    # copies whose hashes matched inventory; never reuse a stale JSON extension.
    municipal_context = build_context(units, raw)
    write_csv(OUT/'analysis_units.csv',units)
    dump(OUT/'analysis_units.json',units)
    write_csv(OUT/'climate_station_monthly.csv',monthly)
    dump(OUT/'climate_station_monthly.json',monthly)
    dump(OUT/'layer_manifest.json',layers)
    dump(OUT/'municipal_context.json',municipal_context)
    dump(OUT/'sources_catalog.json',[dict(id=r['dataset_id'],name=r['dataset_name'],
         institution=r['source'],dataset=r['original_file'],date_or_version=r['temporal_scope'],
         coverage_note=r['coverage'],verification_status='SOURCE_PROVENANCE_PARTIAL',
         usage=r['usage'],limitations=r['limitations'],sha256=r['sha256'],
         original_url='UNKNOWN',license_or_terms=r['license_or_terms']) for r in registry if r['status']!='EXACT_DUPLICATE'])
    write_schema(dictionary)
    document(profiles,registry,dictionary,availability,units,monthly)
    document_sources(profiles,registry)
    # Verify every received file remains unchanged, including ones not copied to raw.
    for p in profiles:assert sha256(ROOT/p['path'])==p['sha256'], f'INCOMING_MUTATED: {p["path"]}'
    products={p.name:dict(sha256=sha256(p),bytes=p.stat().st_size) for p in OUT.iterdir() if p.is_file() and not p.name.startswith('.') and p.name!='manifest.json'}
    dump(OUT/'manifest.json',dict(contract_version='1.0.0',status='READY',
         generated_at=datetime.now(timezone.utc).isoformat(),scope=list(SCOPE),records=len(units),
         municipality_counts=dict(Counter(r['municipality'] for r in units)),
         climate_records=len(monthly),inputs={p['path']:p['sha256'] for p in profiles},outputs=products,
         municipal_context_records=len(municipal_context['values_by_id']),
         municipal_context_fields=len(municipal_context['fields']),
         limitations=['LOCALITY_ONLY','CRS_UNKNOWN_COORDINATES','SOURCE_PROVENANCE_PARTIAL','NO_VALIDATED_DEM_OR_SLOPE','NO_ML_TARGET'],
         processing_script='scripts/data/build_v1.py'))
    print(f'Published {len(units)} locality records, {len(monthly)} station-month records and {len(municipal_context["fields"])} municipal-context fields. Incoming/raw unchanged.')


def write_schema(dictionary):
    properties={f['name']:dict(type=[f['type'],'null'] if f['nullable'] else f['type'],description=f['meaning']) for f in dictionary}
    properties['id'].update(pattern='^11(007|017)[0-9]{4}$')
    properties['municipality'].update(enum=list(SCOPE))
    properties['municipality_code'].update(enum=list(SCOPE.values()))
    properties['analysis_unit'].update(const='locality')
    properties['coordinate_crs'].update(const='CRS_UNKNOWN')
    properties['latitude'].update(minimum=-90,maximum=90)
    properties['longitude'].update(minimum=-180,maximum=180)
    for f in dictionary:
        if f['name'].startswith('riesgo_'):properties[f['name']]['enum']=[0,1,None]
        if f['name'].startswith('dist_'):properties[f['name']]['minimum']=0
    dump(CONTRACT/'analysis_unit.schema.json',dict(**{'$schema':'https://json-schema.org/draft/2020-12/schema'},
         title='ATLAS Data Contract V1 analysis unit',type='object',additionalProperties=False,
         required=list(properties),properties=properties))
    layer_props={k:dict(type='string') for k in ['code','title','category','source_id','date','crs','coverage','unit','limitation','status','analysis_unit']}
    layer_props.update(available=dict(type='integer',minimum=0),expected=dict(type='integer',const=755),continuous_geometry=dict(type='boolean',const=False))
    dump(CONTRACT/'layer_manifest.schema.json',dict(**{'$schema':'https://json-schema.org/draft/2020-12/schema'},
         title='ATLAS layer manifest item V1',type='object',additionalProperties=False,required=list(layer_props),properties=layer_props))


def document(profiles,registry,fields,availability,units,monthly):
    header='# Inventario de datasets — Bloque 1\n\nInventario recursivo de todos los archivos de `data/incoming/`. Los originales permanecen inmutables.\n\n'
    header+='## AVAILABLE_DATASETS\n\nMaestro canónico de 755 localidades (434 Irapuato, 321 Celaya): identificadores, coordenadas numéricas, altitud censal, contexto y distancias recibidas. Disponible para análisis por localidad; la procedencia de las compilaciones es parcial y las coordenadas tienen CRS_UNKNOWN.\n\n'
    header+='## PARTIAL_DATASETS\n\nComplemento estatal filtrado por claves; precipitación de estación CONTEXT_ONLY; terreno EXPERIMENTAL_REFERENCE_ONLY; subcuencas, ferrocarril y uso/vegetación REFERENCE_ONLY; cuatro libros de contexto municipal con 57 campos, conservados separados del maestro. La completitud de atributos no valida automáticamente su procedencia científica.\n\n'
    header+='## Duplicados\n\nLos maestros (1) y (2) tienen el mismo SHA256, tamaño, hojas, columnas, tipos, valores y metadatos internos. Se elige (2) como CANONICAL_SOURCE por continuidad con Plan Maestro, después de comparar contenido; (1) es EXACT_DUPLICATE y se conserva íntegro. Comparación: `data/metadata/duplicate_comparison.json`.\n\n'
    header+='## PENDING_DATASETS\n\n'+ '\n'.join(f'- `{a["code"]}`: {a["status"]}. {a["reason"]}' for a in availability)+'\n\n'
    for p,r in zip(profiles,registry):
        header+=f'## {r["dataset_id"]}\n\n- Archivo original: `{p["path"]}`\n- Formato: {p["format"]}; tamaño: {p["bytes"]} bytes; SHA256: `{p["sha256"]}`.\n'
        for k in ['source','municipality','coverage','date','temporal_scope','crs','status','usage','limitations','raw_file']:
            header+=f'- {k}: {r[k] or "NO COPIADO"}\n'
        header+=f'- Metadatos internos exactos: `{json.dumps(p.get("workbook_metadata",{}),ensure_ascii=False)}`. No equivalen a fecha de observación o descarga.\n\n'
        header+='| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |\n|---|---:|---:|---:|\n'
        header+=''.join(f'| {s["name"]} | {s["records"]} | {s["columns"]} | {s["duplicate_rows"]} |\n' for s in p['sheets'])
        header+='\nDetalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.\n\n'
    pending_new=[r['original_file'] for r in registry if r['status']=='PENDING_INSPECTION']
    header+='## Recepción continua\n\nPendientes de inspección específica: '+(', '.join(pending_new) if pending_new else 'ninguno')+'. Cada ejecución vuelve a inspeccionar incoming recursivamente; un archivo sin política queda PENDING_INSPECTION y no pasa automáticamente a raw/processed. No usar Git para coordinar.\n'
    put(DOC/'datasets.md',header)
    quality='# Calidad y limitaciones — Data V1\n\n'
    quality+='Informe verificable de pruebas, conservación de originales y reconstrucción determinista: `data/metadata/validation_report.json`, generado por `python3 scripts/data/verify_v1.py`. La fecha del manifiesto es el único elemento variable permitido al reconstruir.\n\n'
    quality+='## Comprobaciones ejecutadas\n\n- 755 claves únicas con correspondencia entidad/municipio/localidad; 434 Irapuato y 321 Celaya.\n- Coordenadas numéricas dentro del rango global; esto no confirma datum ni pertenencia por límites municipales.\n- Distancias no negativas y sin nulos; EPSG:6372 solo es CRS declarado de su cálculo original.\n- Filtrado estatal: 755 claves; todos los campos compartidos coinciden dentro de tolerancia numérica 1e-10 absoluta/1e-12 relativa.\n- Razones de servicios y automóvil reproducen los numeradores recibidos y TVIVHAB; no se recalculan ni rellenan nulos.\n- Códigos históricos 0/1 coinciden con Sin daño/Con daño en todas las filas enlazadas.\n- Tabla de terreno enlaza 755 claves: altitud censal y coordenadas coinciden; diferencia de alturas aritmética correcta. Esto no valida DEM ni pendiente.\n- Integridad SHA256 de incoming y copias raw verificada antes y después.\n\n'
    quality+='## Terreno\n\nTabla Datos: 755 filas, 9 columnas; ambas municipalidades. Elevación DEM recibida 1692–2202 m; pendiente 0–15.99993592924168 grados, 22 valores distintos. Las notas la llaman pendiente local aproximada. No hay raster, resolución, datum vertical, fuente, fecha, algoritmo ni rugosidad. DEM=PENDING; elevación DEM=PARTIAL solo como referencia; pendiente=PENDING; rugosidad=PENDING. Únicamente altitude_m censal se publica para contexto. El cálculo original no puede reproducirse con estos insumos.\n\n'
    quality+='## Clima y precipitación\n\nCada libro tiene 26 registros/25 meses, 2024-01 a 2026-01, sin nulos en la tabla recibida. Una estación fija por municipio: CLYGJ y IRPGJ. Variable única de clima: PRECIPITACION_MM; no temperatura. Marzo 2025 se repite con igual valor y distinto ARCHIVO_ORIGEN. Se consolida solo la observación idéntica, conservando ambas procedencias y original_rows=2. Resultado: 50 registros; no imputación, interpolación, superficie ni asignación a todas las localidades. Utilidad CONTEXT_ONLY; precipitación temporal=PARTIAL y precipitación espacial=PENDING. El promedio/acumulado original incluye la fila repetida y no se usa. Institución, licencia y CRS desconocidos.\n\n'
    quality+='## Geometría y procedencia\n\nGEOMETRY_LIMITATION: subcuencas y uso del suelo sin polígonos. Libro estatal de subcuencas dice punto del centro de BBOX; nacional dice punto interior representativo: no son equivalentes ni garantizan una relación espacial. No realizar asignaciones precisas. Ferrocarril tiene coordenadas y fecha 2025-07-18, pero carece de municipio y fuente identificada: no se filtra mediante una caja aproximada. Series I/IV no demuestran estado actual.\n\n'
    quality+='## Contexto municipal\n\nLos cuatro libros adicionales están inventariados y copiados de forma inmutable a raw/municipal_context. Se validan 755 claves por libro, sin duplicados, nombres/códigos/coordenadas coincidentes con el maestro y constancia de cada indicador dentro de su municipio. Se publican 57 campos en municipal_context.json, separado del maestro. NIVEL_FUENTE se conserva como texto de procedencia. Los grados municipales no son mediciones del predio ni sustituyen las capas espaciales pendientes. Institución, fecha, licencia y URL original siguen sin verificar; no se deducen de los nombres de indicadores.\n\n'
    quality+='## Hallazgo de archivo estatal\n\nEIC_Municipal_2015 tiene electricidad, automóvil e Internet en cero para los 46 municipios. Es una anomalía de compilación pendiente, no ausencia demostrada de servicios; esa hoja se excluye. Urbano_2020 y Entorno_2015 se mantienen separados para no multiplicar localidades. Temblor: 9 antecedentes positivos/145 faltantes; ciclón: 0 positivos/145 faltantes en MVP, sin interpretación predictiva.\n\n'
    quality+='## Nulos del dataset consumible\n\n| Campo | Disponibles | Faltantes |\n|---|---:|---:|\n'
    quality+=''.join(f'| {f["name"]} | {f["available_records"]} | {f["missing_records"]} |\n' for f in fields)
    quality+='\nLos 145 nulos históricos siguen siendo nulos; 0 no equivale a seguridad. No se rellenan los 312 faltantes comunes de ciertas variables censales. Las probabilidades y precisión ML no son parte del contrato.\n'
    put(DOC/'data_quality.md',quality)
    dictionary='# Diccionario de campos — analysis_units V1\n\nCampos y metadatos exactos de `data/processed/v1/analysis_units.csv` y JSON. Nulos CSV: vacío; JSON: null. No renombrar ni alterar los originales.\n\n'
    dictionary+='| Nombre | Tipo JSON | Unidad | Nullable | Significado | Fuente / columna original | Temporalidad | Cobertura | Limitaciones |\n|---|---|---|---|---|---|---|---|---|\n'
    for f in fields:
        dictionary+=f'| {f["name"]} | {f["type"]} | {f["unit"]} | {str(f["nullable"]).lower()} | {f["meaning"]} | {f["source"]} / {f["original_field"]} | {f["temporal_scope"]} | {f["available_records"]}/755 localidades | {f["limitations"]} |\n'
    put(META/'field_dictionary.md',dictionary)
    put(DOC/'data_dictionary.md',dictionary)
    contract='# DATA CONTRACT V1 — Bloque 1 → Bloque 2\n\nVersión: **1.0.0**. Estado: listo para consumir una vez que `coordination/status/BLOQUE_1.md` indique READY_FOR_BLOCK_2.\n\n'
    contract+='## Archivos y lectura\n\n- `data/processed/v1/analysis_units.json`: lista de 755 objetos tipados; opción recomendada para evitar inferencia CSV.\n- `data/processed/v1/analysis_units.csv`: UTF-8, separador coma, encabezados, punto decimal, nulos como celdas vacías, identificadores como cadenas.\n- `data/processed/v1/climate_station_monthly.json` y `.csv`: 50 observaciones de estación/mes, separadas del maestro.\n- `data/processed/v1/layer_manifest.json`: metadatos de variables, disponibles/esperados, fuente y limitación. Son atributos por localidad, no polígonos descargables.\n- `data/processed/v1/sources_catalog.json`: lista de fuentes recibidas y atribuciones declaradas, con SOURCE_PROVENANCE_PARTIAL; no equivale a autenticar cada compilación. Campos: id, name, institution, dataset, date_or_version, coverage_note, verification_status, usage, limitations, sha256, original_url, license_or_terms. Todos son strings. No ocultar UNKNOWN ni PENDING.\n- `data/processed/v1/manifest.json`: versión, hashes, entradas y conteos. Verificar antes de integrar.\n- `data/metadata/dataset_registry.csv`, `source_manifest.csv`, `field_dictionary.json` y `availability.json`: procedencia y capacidades.\n- Schemas: `data/contracts/analysis_unit.schema.json` y `layer_manifest.schema.json`.\n\n'
    contract+='## Semántica y cobertura\n\nUnidad única = locality; 434 Irapuato, 321 Celaya. Identificador CVEGEO, 9 caracteres. Coordenadas recibidas numéricas con CRS_UNKNOWN; no se emite GeoJSON ni se inventa EPSG:4326. Altitud censal en metros; no DEM. Las distancias son precalculadas en EPSG:6372 según el libro, sin reprocesar geometría original. No aplicar datos de localidad a coordenada arbitraria, promediar clima sobre municipios ni inferir una superficie.\n\n'
    contract+='Los indicadores `riesgo_*_2014` conservan nombre heredado, pero significan daño histórico reportado: 1=Con daño, 0=Sin daño, null=Sin información suficiente. No son probabilidad ni condición actual. No se crea variable objetivo ML. Los scores de cobertura son codificaciones ordinales heredadas y no porcentajes medidos. Fuente/temporalidad de distancias incompleta.\n\n'
    contract+='## Campos de análisis\n\nLa tabla siguiente es normativa para nombres, tipos, unidades, nullable, significado, fuente, temporalidad, cobertura y limitaciones.\n\n'
    contract+=dictionary[dictionary.index('| Nombre'):]
    contract+='\n## Serie climática independiente\n\n| Campo | Tipo | Unidad | Nullable | Significado / fuente | Temporalidad / cobertura / limitación |\n|---|---|---|---|---|---|\n'
    climate_specs=[('station_id','string','identifier','Clave original CLAVE'),('station_name','string','not_applicable','Nombre original ESTACION'),('municipality','string','not_applicable','Municipio indicado en el libro, sin intersección geométrica'),('period','string','YYYY-MM','Mes original PERIODO'),('year','integer','year','Año original ANIO'),('month','integer','month','Mes original MES'),('longitude','number','decimal_degrees','LONGITUD original'),('latitude','number','decimal_degrees','LATITUD original'),('precipitation_mm','number','mm','PRECIPITACION_MM original, sin imputación'),('origin_files','string','not_applicable','ARCHIVO_ORIGEN; múltiples separados por punto y coma'),('original_rows','integer','rows','Número de filas idénticas consolidadas'),('source_id','string','identifier','climate_celaya o climate_irapuato'),('coordinate_crs','string','identifier','CRS_UNKNOWN'),('usage','string','not_applicable','CONTEXT_ONLY')]
    for n,t,u,m in climate_specs:contract+=f'| {n} | {t} | {u} | false | {m} | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |\n'
    contract+='\n## Capacidades que NO habilita V1\n\nDEM, pendiente, rugosidad, fallas, laderas, ANP, suelo, uso potencial, inundación moderna, uso de suelo actual por punto y subcuenca por intersección permanecen pendientes. Consultar availability.json. No sustituir por cero ni inferir seguridad.\n\n'
    contract+='## Extensión de contexto municipal\n\n`data/processed/v1/municipal_context.json` se reconstruye desde los cuatro libros de raw/municipal_context durante build_v1. Contiene `limitation` (string), `sources` (4 fuentes con metadatos), `fields` (57 objetos con code, column, label, source_id) y `values_by_id` (755 claves CVEGEO con valores string, number o null). Los indicadores son constantes por municipio; no modifican los 64 campos del maestro ni habilitan evaluación espacial del predio. El motor debe conservar PARTIAL_DATA y temporalidad UNKNOWN. Los hashes de entradas y extensión están incluidos en manifest.json.\n\n'
    contract+='## Ejemplos reales\n\n```json\n'+json.dumps([units[0],next(r for r in units if r['municipality']=='Irapuato'),units[1]],ensure_ascii=False,indent=2)+'\n```\n\n'
    contract+='## Reproducción y cambios\n\n```bash\npython3 scripts/data/inspect_datasets.py\npython3 scripts/data/build_v1.py\npython3 -m unittest discover -s tests/data -v\n```\n\nDependencia existente: openpyxl. Versiones exactas en `scripts/data/requirements.txt`. Nunca se sobrescribe raw; una colisión de hash aborta. No se edita incoming. Cada ejecución detecta nuevas entradas; las no reconocidas quedan pendientes de inspección. Los cambios de semántica deben solicitarse en coordination/requests/from_block_1/; no usar Git para coordinación.\n'
    put(CONTRACT/'DATA_CONTRACT_V1.md',contract)


def document_sources(profiles,registry):
    text='# Fuentes de datos — ATLAS V1\n\nRegistro de todos los archivos entregados. Se distingue fuente declarada en el libro de descarga original autenticada. Fecha de descarga, URL exacta y licencia de las compilaciones no se inventan: UNKNOWN/PENDING donde faltan.\n\n'
    text+='| Dataset | Institución | URL | Tipo de archivo | Fecha del dataset | Fecha de descarga | Cobertura geográfica | CRS | Variables | Uso dentro de ATLAS | Limitaciones | Licencia / condiciones de uso |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n'
    for p,r in zip(profiles,registry):
        themes='; '.join(s['name'] for s in p['sheets'] if s['name'] not in ['Diccionario','Resumen','Notas','README','Fuentes','Notas_metodologicas'])
        text+=f'| {r["dataset_id"]}: {r["dataset_name"]} | {r["source"]} | UNKNOWN (descarga original) | {r["format"]} | {r["temporal_scope"]} | UNKNOWN | {r["coverage"]} | {r["crs"]} | {themes} | {r["usage"]} | {r["limitations"]} | {r["license_or_terms"]} |\n'
    text+='\n## Documentación primaria consultada\n\n'
    text+='- [Descriptor ITER 2020 de INEGI](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_iter_cpv2020.pdf): sustenta la unidad de la altitud censal en metros; no autentica el XLSX recibido ni identifica su transformación de coordenadas.\n'
    text+='- [Características de localidades y entorno urbano 2014](https://www.inegi.org.mx/programas/cleu/2014/): referencia del levantamiento histórico declarado en los libros. No se confunde año del levantamiento con fecha exacta de cada episodio de daño.\n'
    text+='- [Términos de libre uso de INEGI](https://www.inegi.org.mx/contenidos/inegi/doc/terminos_info.pdf): marco de uso para información de esa institución; falta verificar procedencia/condiciones de cada compilación y de las fuentes de clima/terreno.\n'
    text+='\nLas fuentes internas, archivos de origen y notas de cada libro se conservaron en `data/metadata/inventory.json` (metadata_rows). La URL de IPLANEG declarada en el libro de subcuencas es una referencia de contexto, no la descarga de polígonos ni prueba de asignación espacial. No se incorporó información externa al dataset procesado.\n'
    put(ROOT/'data/sources.md',text)


if __name__=='__main__':
    main()
