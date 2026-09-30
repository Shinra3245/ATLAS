"""Contract, immutability and scientific semantics checks against real supplied data."""
import copy
import csv
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/data'))
import build_v1 as pipeline
import build_municipal_context as municipal
from inspect_datasets import sha256


def validate_schema_subset(test, obj, schema):
    """Checks every keyword used by our object schemas (not a general JSON validator)."""
    test.assertEqual(set(obj),set(schema['required']))
    test.assertFalse(schema['additionalProperties'])
    for name, spec in schema['properties'].items():
        value=obj[name]
        allowed=spec['type'] if isinstance(spec['type'],list) else [spec['type']]
        actual='null' if value is None else 'boolean' if isinstance(value,bool) else 'integer' if isinstance(value,int) else 'number' if isinstance(value,float) else 'string'
        test.assertTrue(actual in allowed or (actual=='integer' and 'number' in allowed),(name,value,spec))
        if 'const' in spec:test.assertEqual(value,spec['const'])
        if 'enum' in spec:test.assertIn(value,spec['enum'])
        if value is None:continue
        if 'pattern' in spec:test.assertRegex(value,spec['pattern'])
        if 'minimum' in spec:test.assertGreaterEqual(value,spec['minimum'])
        if 'maximum' in spec:test.assertLessEqual(value,spec['maximum'])


class PublishedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.units=json.loads((ROOT/'data/processed/v1/analysis_units.json').read_text())
        cls.climate=json.loads((ROOT/'data/processed/v1/climate_station_monthly.json').read_text())
        cls.inventory=json.loads((ROOT/'data/metadata/inventory.json').read_text())
        cls.manifest=json.loads((ROOT/'data/processed/v1/manifest.json').read_text())

    def test_scope_keys_and_counts(self):
        self.assertEqual(len(self.units),755)
        self.assertEqual(len({r['id'] for r in self.units}),755)
        self.assertEqual(sum(r['municipality']=='Celaya' for r in self.units),321)
        self.assertEqual(sum(r['municipality']=='Irapuato' for r in self.units),434)
        for row in self.units:
            self.assertEqual(row['id'],'11'+row['municipality_code']+row['locality_code'])
            self.assertEqual(row['analysis_unit'],'locality')
            self.assertEqual(row['coordinate_crs'],'CRS_UNKNOWN')

    def test_full_schema_on_real_rows(self):
        schema=json.loads((ROOT/'data/contracts/analysis_unit.schema.json').read_text())
        for row in self.units:validate_schema_subset(self,row,schema)
        schema=json.loads((ROOT/'data/contracts/layer_manifest.schema.json').read_text())
        for row in json.loads((ROOT/'data/processed/v1/layer_manifest.json').read_text()):
            validate_schema_subset(self,row,schema)

    def test_nulls_preserved(self):
        for f in ['riesgo_inundacion_2014','riesgo_sequia_2014','riesgo_helada_2014','riesgo_incendio_2014','riesgo_temblor_2014','riesgo_ciclon_2014']:
            self.assertEqual(sum(r[f] is None for r in self.units),145)
        for f in ['pob15_64','pea','pocupada','cob_electrica','cob_drenaje','autos_por_100_viv']:
            self.assertEqual(sum(r[f] is None for r in self.units),312)

    def test_historical_damage_not_current_risk(self):
        for row in self.units:
            for event in ['inundacion','sequia','helada','incendio','temblor','ciclon']:
                self.assertEqual(row[event+'_2014'],{0:'Sin daño',1:'Con daño',None:None}[row['riesgo_'+event+'_2014']])
        self.assertEqual(sum(r['riesgo_temblor_2014']==1 for r in self.units),9)
        self.assertEqual(sum(r['riesgo_ciclon_2014']==1 for r in self.units),0)

    def test_csv_json_round_trip(self):
        fields=json.loads((ROOT/'data/metadata/field_dictionary.json').read_text())
        specs={f['name']:f for f in fields}
        with (ROOT/'data/processed/v1/analysis_units.csv').open(newline='') as stream:
            for actual,expected in zip(csv.DictReader(stream),self.units,strict=True):
                parsed={}
                for k,v in actual.items():
                    parsed[k]=None if v=='' else int(v) if specs[k]['type']=='integer' else float(v) if specs[k]['type']=='number' else v
                self.assertEqual(parsed,expected)

    def test_incoming_and_raw_integrity(self):
        actual={str(p.relative_to(ROOT)) for p in (ROOT/'data/incoming').rglob('*') if p.is_file() and p.name!='.gitkeep'}
        self.assertEqual(actual,{p['path'] for p in self.inventory})
        for p in self.inventory:self.assertEqual(sha256(ROOT/p['path']),p['sha256'])
        with (ROOT/'data/metadata/dataset_registry.csv').open() as stream:
            registry=list(csv.DictReader(stream))
        self.assertEqual(len(registry),len(self.inventory))
        for row in registry:
            if row['raw_file']:self.assertEqual(sha256(ROOT/row['raw_file']),row['sha256'])

    def test_exact_duplicates_retained(self):
        dupe=json.loads((ROOT/'data/metadata/duplicate_comparison.json').read_text())
        self.assertTrue(dupe['sha256_equal'])
        self.assertTrue(dupe['sheet_content_equal'])
        self.assertTrue(dupe['internal_metadata_equal'])
        self.assertEqual(sha256(ROOT/dupe['canonical']),sha256(ROOT/dupe['duplicate']))

    def test_climate_station_granularity(self):
        self.assertEqual(len(self.climate),50)
        self.assertEqual(len({(r['station_id'],r['period']) for r in self.climate}),50)
        for row in self.climate:
            self.assertEqual(row['usage'],'CONTEXT_ONLY')
            self.assertEqual(row['coordinate_crs'],'CRS_UNKNOWN')
            self.assertGreaterEqual(row['precipitation_mm'],0)
            self.assertGreaterEqual(row['period'],'2024-01')
            self.assertLessEqual(row['period'],'2026-01')
        repeated=[r for r in self.climate if r['original_rows']==2]
        self.assertEqual(len(repeated),2)
        self.assertTrue(all(r['period']=='2025-03' for r in repeated))
        self.assertTrue(all(len(r['origin_files'].split(';'))==2 for r in repeated))

    def test_no_unvalidated_terrain_or_climate_in_localities(self):
        self.assertFalse(set(self.units[0]) & {'slope','slope_deg','pendiente_local_grados','roughness','elevacion_dem_m','precipitation_mm','temperature'})
        status={a['code']:a['status'] for a in json.loads((ROOT/'data/metadata/availability.json').read_text())}
        for key in ['dem','slope','roughness','precipitation_spatial','landuse_current','subbasin_assignment']:
            self.assertEqual(status[key],'PENDING')

    def test_layers_coverage_matches_real_values(self):
        for layer in json.loads((ROOT/'data/processed/v1/layer_manifest.json').read_text()):
            self.assertEqual(layer['available'],sum(r[layer['code']] is not None for r in self.units))
            self.assertEqual(layer['expected'],755)
            self.assertFalse(layer['continuous_geometry'])

    def test_manifest_hashes(self):
        for name,info in self.manifest['outputs'].items():
            self.assertEqual(sha256(ROOT/'data/processed/v1'/name),info['sha256'])
        for path,digest in self.manifest['inputs'].items():self.assertEqual(sha256(ROOT/path),digest)

    def test_sources_catalog_is_declared_not_authenticated(self):
        catalog=json.loads((ROOT/'data/processed/v1/sources_catalog.json').read_text())
        self.assertEqual(len(catalog),14)
        self.assertEqual(len({r['id'] for r in catalog}),14)
        for row in catalog:
            self.assertEqual(row['verification_status'],'SOURCE_PROVENANCE_PARTIAL')
            self.assertEqual(row['original_url'],'UNKNOWN')
            self.assertEqual(row['license_or_terms'],'PENDING_SOURCE_PROVENANCE')
            self.assertEqual(row['sha256'],sha256(ROOT/row['dataset']))

    def test_municipal_inputs_have_immutable_registered_copies(self):
        with (ROOT/'data/metadata/dataset_registry.csv').open() as stream:
            registry={row['dataset_name']:row for row in csv.DictReader(stream)}
        self.assertEqual(len(self.inventory),15)
        for source_id,filename,_ in municipal.BOOKS:
            row=registry[filename]
            self.assertEqual(row['dataset_id'],source_id)
            self.assertEqual(row['usage'],'MUNICIPAL_CONTEXT')
            self.assertEqual(row['status'],'PARTIAL')
            self.assertEqual(sha256(ROOT/row['raw_file']),row['sha256'])
            self.assertEqual(self.manifest['inputs'][row['original_file']],row['sha256'])

    def test_municipal_publication_matches_raw_and_is_deterministic(self):
        paths={filename:municipal.RAW/filename for _,filename,_ in municipal.BOOKS}
        actual=json.loads((ROOT/'data/processed/v1/municipal_context.json').read_text())
        expected=municipal.build_context(self.units,paths)
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual['fields']),57)
        self.assertEqual(len(actual['values_by_id']),755)
        self.assertEqual(self.manifest['municipal_context_fields'],57)
        self.assertEqual(set(actual['values_by_id']),{row['id'] for row in self.units})
        self.assertEqual(list(actual['values_by_id']),sorted(actual['values_by_id']))
        by_id={row['id']:row for row in self.units}
        for field in actual['fields']:
            for municipality in ['Celaya','Irapuato']:
                values={str(row[field['code']]) for key,row in actual['values_by_id'].items()
                        if by_id[key]['municipality']==municipality}
                self.assertEqual(len(values),1,(municipality,field['code']))


    def test_workbook_dates_are_only_actual_metadata(self):
        from zipfile import ZipFile
        for dataset in self.inventory:
            with ZipFile(ROOT/dataset['path']) as archive:
                if 'docProps/core.xml' not in archive.namelist():
                    self.assertEqual(dataset['workbook_metadata'],{})

    def test_climate_conflict_aborts(self):
        rows=pipeline.read_sheet(ROOT/'data/raw/celaya/Clima_Celaya_2024_2026.xlsx','Precipitacion_mensual')
        conflicting=copy.deepcopy(rows)
        march=[r for r in conflicting if r['PERIODO']=='2025-03']
        march[1]['PRECIPITACION_MM']=999
        with patch.object(pipeline,'read_sheet',return_value=conflicting):
            with self.assertRaisesRegex(AssertionError,'Climate conflict'):
                pipeline.climate([('Celaya',Path('not-read.xlsx'))])

    def test_raw_conflict_is_never_overwritten(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(dir=ROOT/'tests/data') as temp:
            fake=Path(temp)
            incoming=fake/'data/incoming/example.xlsx';incoming.parent.mkdir(parents=True)
            incoming.write_bytes(b'original')
            raw=fake/'data/raw/shared/example.xlsx';raw.parent.mkdir(parents=True)
            raw.write_bytes(b'different-existing')
            with patch.object(pipeline,'ROOT',fake):
                with self.assertRaisesRegex(ValueError,'RAW_CONFLICT'):
                    pipeline.immutable_copy({'path':'data/incoming/example.xlsx','sha256':sha256(incoming)},'shared')
            self.assertEqual(raw.read_bytes(),b'different-existing')
            self.assertEqual(incoming.read_bytes(),b'original')


class MunicipalValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.units=json.loads((ROOT/'data/processed/v1/analysis_units.json').read_text())
        cls.filename=municipal.BOOKS[0][1]
        cls.header,cls.rows=municipal._load_sheet(municipal.RAW/cls.filename)
        cls.paths={filename:municipal.RAW/filename for _,filename,_ in municipal.BOOKS}

    def assert_rejected(self,rows,error,header=None):
        with patch.object(municipal,'_load_sheet',return_value=(header or self.header,rows)):
            with self.assertRaisesRegex(ValueError,error):
                municipal.build_context(self.units,self.paths)

    def mutated(self,column,value):
        rows=[list(row) for row in self.rows]
        rows[0][self.header.index(column)]=value
        return rows

    def test_duplicate_locality_is_rejected(self):
        self.assert_rejected([*self.rows,self.rows[0]],'MUNICIPAL_DUPLICATE')

    def test_missing_locality_is_rejected(self):
        self.assert_rejected(self.rows[1:],'MUNICIPAL_MISSING')

    def test_outside_locality_is_rejected(self):
        self.assert_rejected(self.mutated('CVEGEO',999999999),'MUNICIPAL_OUTSIDE_MASTER')

    def test_municipality_conflict_is_rejected(self):
        self.assert_rejected(self.mutated('NOM_MUN','Irapuato'),'MUNICIPAL_IDENTITY_CONFLICT')

    def test_coordinate_conflict_is_rejected(self):
        self.assert_rejected(self.mutated('LATITUD',19.4326),'MUNICIPAL_COORDINATE_CONFLICT')

    def test_non_finite_coordinate_is_rejected(self):
        self.assert_rejected(self.mutated('LONGITUD',float('nan')),'MUNICIPAL_COORDINATE_CONFLICT')

    def test_local_values_cannot_masquerade_as_municipal_context(self):
        self.assert_rejected(self.mutated('GP_INUNDAC_MUN_CONTEXT','Otro valor'),'MUNICIPAL_RESOLUTION_CONFLICT')

    def test_non_finite_indicator_is_rejected(self):
        self.assert_rejected(self.mutated('GP_INUNDAC_MUN_CONTEXT',float('inf')),'MUNICIPAL_NON_FINITE')

    def test_non_municipal_field_is_rejected(self):
        from tempfile import TemporaryDirectory
        import openpyxl
        with TemporaryDirectory() as temp:
            path=Path(temp)/'invalid.xlsx'
            book=openpyxl.Workbook();sheet=book.active;sheet.title='Localidades'
            sheet.append([*sorted(municipal.IDENTITY),'risk_score']);book.save(path);book.close()
            with self.assertRaisesRegex(ValueError,'MUNICIPAL_FIELD_SCOPE'):
                municipal._load_sheet(path)

    def test_duplicate_header_is_rejected(self):
        from tempfile import TemporaryDirectory
        import openpyxl
        with TemporaryDirectory() as temp:
            path=Path(temp)/'invalid.xlsx'
            book=openpyxl.Workbook();sheet=book.active;sheet.title='Localidades'
            sheet.append([*sorted(municipal.IDENTITY),'CVEGEO']);book.save(path);book.close()
            with self.assertRaisesRegex(ValueError,'MUNICIPAL_HEADER'):
                municipal._load_sheet(path)


if __name__=='__main__':unittest.main()
