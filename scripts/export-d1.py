#!/usr/bin/env python3
"""Export a freshly seeded local EmDash DB to safe D1 schema/data batches."""
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.deploy-transfer'
OUT.mkdir(exist_ok=True)
c=sqlite3.connect(ROOT/'cms-seed.db')
shadow={row[1] for row in c.execute('pragma table_list') if row[2]=='shadow'}
rows=c.execute("select type,name,sql from sqlite_master where sql is not null and name not like 'sqlite_%' order by rowid").fetchall()
schema=[]
indexes=[]
data=[]
counts={}

def quote(value):
    if value is None:return 'NULL'
    if isinstance(value,bytes):return "X'"+value.hex()+"'"
    if isinstance(value,(int,float)):return str(value)
    return "'"+str(value).replace("'","''")+"'"

for kind,name,sql in rows:
    if name in shadow:continue
    if kind=='table':schema.append(sql+';')
    else:indexes.append(sql+';')
for kind,name,sql in rows:
    if kind!='table' or name in shadow:continue
    columns=[row[1] for row in c.execute('pragma table_info("'+name+'")')]
    records=c.execute('SELECT '+','.join('"'+col+'"' for col in columns)+' FROM "'+name+'"').fetchall()
    if records:counts[name]=len(records)
    for row in records:
        data.append('INSERT INTO "'+name+'" ('+','.join('"'+col+'"' for col in columns)+') VALUES ('+','.join(quote(v) for v in row)+');')
all_statements=['PRAGMA defer_foreign_keys = ON;']+schema+data+indexes
(ROOT/'seed/d1-export.sql').write_text('\n'.join(all_statements)+'\n')
(OUT/'d1-seed.json').write_text(json.dumps({'schema':schema,'data':data,'indexes':indexes,'counts':counts},separators=(',',':')))
print(json.dumps({'tables':len(schema),'data_rows':len(data),'indexes_and_triggers':len(indexes),'max_statement_bytes':max(len(s.encode()) for s in all_statements),'total_sql_bytes':sum(len(s.encode()) for s in all_statements),'populated_tables':counts}))
