"""Read-only, offline verification of Lab 7 relation exports against schema.sql."""
import re,html,json
from pathlib import Path
from xml.etree import ElementTree as ET
from generate_diagrams import TABLES,TABLE_NOTES,fks
root=Path(__file__).resolve().parents[3]
sql=(root/'app/schema.sql').read_text(encoding='utf-8')
blocks=dict(re.findall(r'CREATE TABLE (\w+) \((.*?)\n\);',sql,re.S))
assert set(blocks)==set(TABLES)
cells=list(ET.parse(root/'docs/diagrams/relational-schema.drawio').iter('mxCell'))
labels=[html.unescape(re.sub('<[^>]+>','',c.get('value',''))) for c in cells]
joined='\n'.join(labels);count=0
for table,cols in TABLES.items():
 body=re.sub(r'--[^\n]*','',blocks[table])
 actual=dict(re.findall(r'^\s+(\w+)\s+((?:INT|VARCHAR|BOOLEAN|ENUM|DECIMAL|DATE|DATETIME|MEDIUMBLOB)\b(?:\([^)]*\))?[^\n]*)',body,re.M))
 assert set(actual)=={c[0] for c in cols},table
 assert table.upper() in labels
 for col,typ,key,null,ref in cols:
  declaration=actual[col];count+=1
  if 'see note' not in typ:assert typ.replace(' ','') in declaration.replace(' ',''),(table,col,typ)
  else:
   values=re.search(r'ENUM\((.*?)\)',declaration,re.S).group(1)
   for value in re.findall("'([^']+)'",values):assert value in ' '.join(TABLE_NOTES[table]),(table,col,value)
  assert ('NOT NULL' in declaration or 'PRIMARY KEY' in declaration)==(null=='NOT NULL'),(table,col,null)
  assert col+(' [UQ]' if 'UQ' in key else '') in labels
  if 'PK' in key:
   assert 'PRIMARY KEY' in declaration or re.search(r'PRIMARY KEY\s*\([^)]*\b'+col+r'\b',body)
   assert any('<u>'+col in c.get('value','') for c in cells)
  if 'UQ' in key:assert 'UNIQUE' in declaration
 for fk,par,target in re.findall(r'FOREIGN KEY\s*\((\w+)\)\s*REFERENCES\s*(\w+)\((\w+)\)',body):
  assert f'{fk} -> {par}.{target}' in joined,(table,fk)
 for check in re.findall(r'CONSTRAINT\s+(\w+)\s+CHECK',body):assert check in joined,check
assert len(list(fks()))==32
result={'tables':15,'columns':count,'foreign_keys':32,'named_checks':len(re.findall(r'CONSTRAINT\s+\w+\s+CHECK',sql)),'result':'pass','scope':'Offline DDL and exported XML; no DB tests executed'}
print(json.dumps(result,indent=2))
