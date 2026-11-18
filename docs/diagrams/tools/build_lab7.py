"""Lab 7 diagram exports: editable Draw.io, vector PDF and SVG from one layout.
Reuses Track A's SQL transcription; no database connection or mutation.
"""
from pathlib import Path
import math, html, re, json, hashlib
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from generate_diagrams import TABLES, TABLE_NOTES, fks, Page, write_file, build_conceptual
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[1]
W,H=1190,842
class Sheet:
 def __init__(self,title,ident,w=W,h=H):
  self.w,self.h=w,h; self.page=Page(title,ident);self.items=[]
 def text(self,t,x,y,w,h=30,size=12,under=False):
  return self.shape(t,x,y,w,h,'text',size,under)
 def shape(self,t,x,y,w,h,kind='rect',size=11,under=False,fill='#FFFFFF'):
  assert x>=0 and y>=0 and x+w<=self.w and y+h<=self.h,(t,x,y,w,h)
  st=f'html=1;whiteSpace=wrap;fontFamily=Helvetica;fontSize={size};fillColor={fill};strokeColor=#222222;'
  st+= ('dashed=1;' if kind=='derived' else '')
  st+= 'shape=rhombus;' if kind=='diamond' else 'ellipse;' if kind in ('ellipse','derived') else 'text;strokeColor=none;' if kind=='text' else ''
  label='<u>'+html.escape(t)+'</u>' if under else html.escape(t)
  ident=self.page.vertex(label,x,y,w,h,st)
  self.items.append(('shape',t,x,y,w,h,kind,size,under,fill));return ident
 def line(self,x1,y1,x2,y2,source,target,double=False):
  self.page.edge(source,target,'endArrow=none;startArrow=none;strokeColor=#222222;'+('shape=link;' if double else ''))
  self.items.append(('line',x1,y1,x2,y2,double))
 def paint(self,c):
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>']
  for a in self.items:
   c.setStrokeColor(colors.HexColor('#222222'));c.setLineWidth(.8)
   if a[0]=='line':
    _,x,y,xx,yy,double=a
    for off in ([-1.5,1.5] if double else [0]):
     c.line(x,self.h-y+off,xx,self.h-yy+off)
     svg.append(f'<path d="M{x},{y-off} L{xx},{yy-off}" stroke="#222" fill="none"/>')
    continue
   _,t,x,y,w,h,k,size,u,fill=a
   c.setFillColor(colors.HexColor(fill))
   if k=='rect':c.rect(x,self.h-y-h,w,h,fill=1);svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#222"/>')
   if k in ('ellipse','derived'):
    c.setDash(3,2) if k=='derived' else c.setDash()
    c.ellipse(x,self.h-y-h,x+w,self.h-y,fill=1);svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="#222"'+(' stroke-dasharray="3 2"' if k=='derived' else '')+'/>')
    c.setDash()
   if k=='diamond':
    p=c.beginPath();p.moveTo(x,self.h-y-h/2);p.lineTo(x+w/2,self.h-y);p.lineTo(x+w,self.h-y-h/2);p.lineTo(x+w/2,self.h-y-h);p.close();c.drawPath(p,fill=1)
    svg.append(f'<polygon points="{x},{y+h/2} {x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h}" fill="{fill}" stroke="#222"/>')
   # Paragraph handles wrapped labels consistently; SVG uses those same line fragments.
   p=Paragraph(('<u>' if u else '')+html.escape(t).replace('\n','<br/>')+('</u>' if u else ''),ParagraphStyle('label',fontName='Helvetica',fontSize=size,leading=size*1.15,alignment=1))
   aw=w-8 if k!='diamond' else w*.72
   _,hh=p.wrap(aw,h);assert hh<=h-2,(t,hh,h)
   p.drawOn(c,x+(w-aw)/2,self.h-y-(h+hh)/2)
   plain=Paragraph(html.escape(t).replace('\n','<br/>'),ParagraphStyle('svg',fontName='Helvetica',fontSize=size,leading=size*1.15,alignment=1));plain.wrap(aw,h)
   for i,line in enumerate(plain.blPara.lines):
    words=line[1] if isinstance(line,tuple) else [getattr(v,'text','') for v in line.words]
    s=' '.join(words);sy=y+(h-hh)/2+size+i*size*1.15
    svg.append(f'<text x="{x+w/2}" y="{sy}" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="{size}"'+(' text-decoration="underline"' if u else '')+'>'+html.escape(s)+'</text>')
  return ''.join(svg)+'</svg>'
def export(name,sheets):
 c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(W,H),invariant=1)
 for i,s in enumerate(sheets):
  c.setPageSize((s.w,s.h));svg=s.paint(c);c.showPage()
  (OUT/(name+('' if i==0 else f'-p{i+1}')+'.svg')).write_text(svg,encoding='utf-8')
 c.save();write_file(str(OUT/(name+'.drawio')),[s.page for s in sheets])
def heading(s,title,note):
 s.text(title,20,14,W-40,32,20);s.text(note,20,50,W-40,32,10)
# Capture Track A conceptual attributes and relationships without changing their meaning.
old=ET.fromstring(build_conceptual()[0].xml());cells={e.get('id'):e for e in old.iter('mxCell')}
entities={};relations=[]
for ident,e in cells.items():
 if 'swimlane;' in e.get('style',''):
  name=html.unescape(e.get('value')); child=next(c for c in cells.values() if c.get('parent')==ident)
  attrs=[]
  for a in child.get('value').split('<br>'):
   attrs.append((html.unescape(re.sub('<[^>]+>','',a)),'<u>' in a))
  entities[ident]=(name,attrs)
for ident,e in cells.items():
 if 'shape=rhombus' in e.get('style',''):
  edges=[v for v in cells.values() if v.get('target')==ident and v.get('source') in entities]
  if len(edges)==2:relations.append((e.get('value'),[(entities[v.get('source')][0],v.get('value')) for v in edges]))
# Stored discrepancy is a regular attribute, not a non-stored derived quantity.
for _,attrs in entities.values():
 for i,(a,u) in enumerate(attrs):
  if a.startswith('/discrepancy ='):attrs[i]=('discrepancy_quantity',u)
concept=[];elist=list(entities.values())
for p in range(2):
 s=Sheet(f'Entity attributes {p+1}',f'ea{p}')
 heading(s,f'Conceptual ER | entity attributes {p+1}/2','Lab 7 notation: rectangle = entity; oval = attribute; underline = identifier; dashed oval = derived. Relationships continue on sheets 3–5.')
 for i,(name,attrs) in enumerate(elist[p*7:p*7+7]):
  x=25+(i%3)*390;y=105+(i//3)*235
  eid=s.shape(name,x+78,y+88,224,32,size=11)
  n=len(attrs)
  for j,(a,u) in enumerate(attrs):
   top=j<4;k=j if top else j-4;count=min(n,4) if top else n-4
   ax=x+k*(370/count);ay=y+10 if top else y+165;aw=370/count-6
   aid=s.shape(a.lstrip('/'),ax,ay,aw,48,'derived' if a.startswith('/') else 'ellipse',8.5,u)
   s.line(x+190,y+(88 if top else 120),ax+aw/2,ay+(48 if top else 0),eid,aid)
 concept.append(s)
# Make all actor and unit relationships explicit; repeated entities reference attribute sheets.
mapnames={'crop_cycles':'CROP_CYCLE','harvest_lots':'HARVEST_LOT','harvest_lot_images':'LOT_IMAGE','market_requests':'MARKET_REQUEST','request_status_history':'REQUEST_STATUS_CHANGE','allocations':'ALLOCATION','delivery_receipts':'DELIVERY_RECEIPT','stock_movements':'STOCK_MOVEMENT'}
for child,col,parent,nullable,unique in fks():
 if parent=='users' and child in mapnames:relations.append((col.replace('_',' ').upper(),[(mapnames[child],'(1,1)'),('USER','(0,N)')]))
 if parent=='units' and child in ['allocations','delivery_receipts','stock_movements']:relations.append(('MEASURED IN',[(mapnames[child],'(1,1)'),('UNIT','(0,N)')]))
for p in range(3):
 s=Sheet(f'Relationships {p+1}',f'rel{p}')
 heading(s,f'Conceptual ER | relationships {p+1}/3','1 / N = maximum cardinality at the entity end; double line = mandatory participation. Same entity name = same entity across sheets.')
 for i,(name,pair) in enumerate(relations[p*11:p*11+11]):
  x=25+(i%2)*590;y=100+(i//2)*115
  a,ca=pair[0];b,cb=pair[1]
  ai=s.shape(a,x,y+30,180,35,size=10);bi=s.shape(b,x+365,y+30,180,35,size=10)
  di=s.shape(name,x+220,y+20,105,55,'diamond',9)
  s.line(x+180,y+47.5,x+220,y+47.5,ai,di,ca.startswith('(1'))
  s.line(x+325,y+47.5,x+365,y+47.5,di,bi,cb.startswith('(1'))
  s.text('N' if 'N' in cb else '1',x+180,y+15,35,20,12)
  s.text('N' if 'N' in ca else '1',x+330,y+15,35,20,12)
  s.text(f'{a}: {ca}   |   {b}: {cb}',x,y+(0 if name=='ASSIGNED TO' else 72),545,20,9)
  if name=='ASSIGNED TO':
   at=s.shape('assigned_at',x+235,y+85,80,24,'ellipse',9);s.line(x+272,y+75,x+275,y+85,di,at)
 s.text('* Minimum guaranteed by application transaction, not FK alone. USER role restricts farm assignment and market membership. See DATABASE_DESIGN.md.',25,803,1140,22,9)
 concept.append(s)
export('conceptual-er',concept)
# Lab 7 relations: one horizontal attribute row per relation; types and constraints below.
schemas=[]
for page in range(3):
 s=Sheet(f'Relations {page+1}',f'lr{page}')
 heading(s,f'Relational schema | {page+1}/3','Underlined = primary key; blue cell = foreign key. Each FK target is explicitly listed below its relation. UQ = UNIQUE. Types, nullability, defaults and constraints are retained.')
 for row,(name,cols) in enumerate(list(TABLES.items())[page*5:page*5+5]):
  y=92+row*143;s.text(name.upper(),25,y,1140,20,12)
  cw=1140/len(cols)
  for i,(col,typ,key,null,ref) in enumerate(cols):
   s.shape(col+(' [UQ]' if 'UQ' in key else ''),25+i*cw,y+23,cw,30,'rect',9,'PK' in key,'#DCECF7' if 'FK' in key else '#FFFFFF')
   s.text(typ+'\n'+null,25+i*cw,y+54,cw,42,8)
  refs='; '.join(c[0]+' -> '+c[4].split('→ ')[1] for c in cols if 'FK' in c[2])
  notes='; '.join(TABLE_NOTES.get(name,[]))
  defaults='; '.join(c[0]+': '+c[4] for c in cols if 'DEFAULT' in c[4])
  s.text(' | '.join(v for v in [refs,notes,defaults] if v).replace('≥','>=').replace('−','-').replace('∈','in'),25,y+97,1140,43,8.3)
 schemas.append(s)
export('relational-schema',schemas)
print('Built 5 conceptual sheets, 3 relational sheets; 14 entities,',len(relations),'relationships, 15 relations and',len(list(fks())),'FK references.')
