"""Build the review PDFs without importing the app or connecting to a database."""
import argparse
from collections import Counter
import hashlib
import html
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = 'docs/report/input-manifest.json'
INPUTS = ['docs/diagrams/conceptual-er.pdf', 'docs/diagrams/relational-schema.pdf',
          'docs/diagrams/conceptual-er.drawio', 'docs/diagrams/relational-schema.drawio',
          'docs/evidence/track-a/remaining-checks.json', 'docs/evidence/track-a/gui-flow.json',
          'docs/evidence/fixes-2026-11-17/backend.json',
          'docs/evidence/fixes-2026-11-17/gui-flow.json',
          'docs/evidence/fixes-2026-11-17/assistant.json',
          'docs/evidence/fixes-2026-11-17/summary.json',
          'docs/evidence/live-ai-results.json']
GREEN, DARK, INK = '#2E7D32', '#1B5E20', '#1F2933'


def rich(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#1B5E20">\1</link>', text)


def style(size=9.6, **kw):
    return ParagraphStyle('text', fontName='Helvetica', fontSize=size, leading=size*1.3,
                          textColor=colors.HexColor(INK), spaceAfter=6, **kw)


def flows(markdown, width):
    # ponytail: only the Markdown constructs used by this report, not a general converter.
    lines = markdown.strip().splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', x) for x in cells):
                    rows.append(cells)
                i += 1
            count = len(rows[0])
            assert all(len(r) == count for r in rows), 'Malformed Markdown table'
            proportions = ([.52,.25,.23] if rows[0][0].startswith('ID and') else
                           [.31,.30,.39] if count == 3 else [.38,.62] if count == 2 else [.58,.14,.14,.14])
            data = [[Paragraph(rich(x), style(8.2 if count==3 else 8.7)) for x in row] for row in rows]
            table = Table(data, colWidths=[width*x for x in proportions], hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F5E9')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F6F4')]),
                ('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),6),
                ('RIGHTPADDING',(0,0),(-1,-1),6), ('TOPPADDING',(0,0),(-1,-1),4),
                ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            out.extend([table,Spacer(1,7)])
            continue
        if line == '```':
            i += 1
            while i < len(lines) and lines[i] != '```':
                out.append(Paragraph(escape(lines[i]), style(8.2)))
                i += 1
            i += 1
            continue
        if line.startswith('# '):
            out.append(Paragraph(rich(line[2:]),ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=23,leading=28,spaceAfter=12,textColor=colors.HexColor(INK))))
        elif line.startswith('### '):
            out.append(Paragraph(rich(line[4:]),ParagraphStyle('subheading',fontName='Helvetica-Bold',fontSize=10.2,leading=13,spaceBefore=5,spaceAfter=4,textColor=colors.HexColor(DARK))))
        elif line.startswith('## '):
            out.append(Paragraph(rich(line[3:]),ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=12.5,leading=16,spaceBefore=7,spaceAfter=5,textColor=colors.HexColor(DARK))))
        else:
            chunk=[line]
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','```')):
                i += 1
                chunk.append(lines[i].strip())
            out.append(Paragraph(rich(' '.join(chunk)),style()))
        i += 1
    return out


def footer(c, w, page, total, label='Review candidate | 18 November 2026'):
    c.setFillColor(colors.HexColor('#56645B'))
    c.setFont('Helvetica',8)
    c.drawString(38,21,label)
    c.drawRightString(w-38,21,f'Farm-to-Market | B1 | {page} / {total}')


def report(input_dir, out_dir):
    sections=(ROOT/'docs/report/technical-report.md').read_text(encoding='utf-8').split('<!-- page -->')
    assert len(sections)==5
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=A4,invariant=1)
    c.setTitle('Farm to Market technical report - review candidate')
    w,h=A4
    for number,section in enumerate(sections,1):
        y=h-38
        for f in flows(section,w-76):
            y-=getattr(f,'spaceBefore',0)
            fw,fh=f.wrap(w-76,y-42)
            if y-fh < 43:
                raise ValueError(f'Report page {number} overflows by {43-y+fh:.1f} pt')
            f.drawOn(c,38,y-fh)
            y-=fh+getattr(f,'spaceAfter',0)
        footer(c,w,number,13)
        c.showPage()
    c.save()
    writer=PdfWriter()
    writer.append(PdfReader(buf))
    titles=['ER attributes 1','ER attributes 2','ER relationships 1','ER relationships 2','ER relationships 3','Relations 1','Relations 2','Relations 3']
    source_pages=list(PdfReader(input_dir/INPUTS[0]).pages)+list(PdfReader(input_dir/INPUTS[1]).pages)
    assert len(source_pages)==8
    for idx,source in enumerate(source_pages):
        sw,sh=float(source.mediabox.width),float(source.mediabox.height)
        b=io.BytesIO(); cc=canvas.Canvas(b,pagesize=(sw+40,sh+92),invariant=1)
        cc.setFont('Helvetica-Bold',18);cc.setFillColor(colors.HexColor(DARK))
        cc.drawString(20,sh+63,titles[idx])
        cc.setFont('Helvetica',10)
        cc.drawString(20,sh+46,'Source hashes are recorded in docs/report/input-manifest.json | Review pending')
        footer(cc,sw+40,idx+6,13)
        cc.save()
        page=PdfReader(b).pages[0]
        page.merge_transformed_page(source,Transformation().translate(20,36))
        writer.add_page(page)
    manifest=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))
    writer.add_metadata({'/Title':'Farm to Market technical report - review candidate',
                         '/Author':'Mohammad Arwani with Codex; diagrams by Ali Alshamsi with Claude',
                         '/Subject':'COSC444 B1 | review candidate | Track A '+manifest['track_a_commit']+' | fixes '+manifest['fix_commit']})
    for page,title in enumerate(['Overview','Transactions','Test evidence','Live assistant','Limitations and references']+titles):
        writer.add_outline_item(title,page)
    with (out_dir/'technical-report.pdf').open('wb') as f:writer.write(f)


def poster_check(config, input_dir):
    cells=list(ET.parse(input_dir/'docs/diagrams/conceptual-er.drawio').iter('mxCell'))
    labels={html.unescape(re.sub('<[^>]+>','',c.get('value',''))) for c in cells}
    for node in config['nodes']: assert node['name'] in labels,node['name']
    for rel in config['relationships']: assert rel['label'].upper() in labels,rel['label']


def poster(config,input_dir,out_dir):
    poster_check(config,input_dir)
    w,h=1920,1080
    c=canvas.Canvas(str(out_dir/'poster.pdf'),pagesize=(w,h),invariant=1)
    c.setTitle('Farm-to-Market poster - review candidate')
    c.setAuthor('Mohammad Arwani with Codex; ER derived from Track A')
    def rect(x,top,ww,hh,color):
        c.setFillColor(colors.HexColor(color));c.rect(x,h-top-hh,ww,hh,fill=1,stroke=0)
    def text(txt,x,top,ww,size=24,color=INK,bold=False):
        st=ParagraphStyle('poster',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.25,textColor=colors.HexColor(color))
        p=Paragraph(escape(txt),st);_,hh=p.wrap(ww,1000);p.drawOn(c,x,h-top-hh)
        assert x>=0 and x+ww<=w and top+hh<=h,(txt,'outside poster')
        return hh
    rect(0,0,w,h,'#FFFFFF');rect(0,0,w,194,DARK)
    text(config['title'],48,24,1500,57,'#FFFFFF',True)
    text(config['subtitle'],50,93,1750,27,'#FFFFFF')
    text(config['course'],50,143,1750,20,'#E8F5E9')
    text('REVIEW CANDIDATE',1510,40,365,23,'#FFFFFF',True)
    for i,member in enumerate(config['team']):text(member,50+i*625,211,610,23,INK,True)
    text(config['context'],50,257,1810,22)
    for i,item in enumerate(config['workflow']):
        x=50+i*468;rect(x,323,448,64,'#E8F5E9');text(f'{i+1}  {item}',x+14,340,420,22,DARK,True)
    text('Rules that keep stock explainable',50,420,625,30,DARK,True)
    y=472
    for item in config['rules']:
        text('- '+item,50,y,600,24);y+=69 if len(item)>53 else 54
    text('Core application',50,725,610,28,DARK,True)
    text(config['features'],50,769,610,22)
    # Separate ER area; coordinates in source are offset down to sit below workflow.
    text('Database design',740,420,1100,30,DARK,True)
    nodes={n['id']:n for n in config['nodes']}
    keys=['farm_id','cycle_id','lot_id','market_id','request_id','allocation_id','receipt_id']
    keymap={n['id']:k for n,k in zip(config['nodes'],keys)}
    def erbox(label,x,y,ww,hh,oval=False,diamond=False,underline=False):
        c.setFillColor(colors.white);c.setStrokeColor(colors.HexColor(DARK));c.setLineWidth(1.3)
        if oval:c.ellipse(x,h-y-hh,x+ww,h-y,fill=1)
        elif diamond:
            p=c.beginPath();p.moveTo(x,h-y-hh/2);p.lineTo(x+ww/2,h-y);p.lineTo(x+ww,h-y-hh/2);p.lineTo(x+ww/2,h-y-hh);p.close();c.drawPath(p,fill=1)
        else:c.rect(x,h-y-hh,ww,hh,fill=1)
        size=15 if diamond else 17
        c.setFont('Helvetica',size);c.setFillColor(colors.HexColor(INK))
        c.drawCentredString(x+ww/2,h-y-hh/2-5,label)
        if underline:
            tw=c.stringWidth(label,'Helvetica',size);c.line(x+(ww-tw)/2,h-y-hh/2-7,x+(ww+tw)/2,h-y-hh/2-7)
    for i,rel in enumerate(config['relationships']):
        x=740+(i%2)*565;y=480+(i//2)*160
        for ident,xx in [(rel['a'],x),(rel['b'],x+370)]:
            erbox(keymap[ident],xx+10,y,145,36,oval=True,underline=True)
            c.line(xx+82,h-y-36,xx+82,h-y-62)
            erbox(nodes[ident]['label'],xx,y+62,165,42)
        erbox(rel['label'],x+209,y+57,115,52,diamond=True)
        c.line(x+165,h-y-83,x+209,h-y-83);c.line(x+324,h-y-83,x+370,h-y-83)
        # Right-side record must belong to exactly one left-side record.
        c.line(x+324,h-y-86,x+370,h-y-86)
        # Lab 7 maximum cardinalities, with optionality retained explicitly below.
        text('N' if 'N' in rel['a_card'] else '1',x+175,y+53,32,17)
        text('N' if 'N' in rel['b_card'] else '1',x+337,y+53,32,17)
        text(rel['a_card']+' : '+rel['b_card'],x+210,y+118,150,16)
    text('Core relationships; double line = mandatory. Repeated names = same entity. Full model: report.',740,967,1100,17)
    # Advanced feature on a second band, left bottom; keeps prose large.
    rect(50,904,625,130,'#E8F5E9')
    text(config['advanced'][0],65,915,590,27,DARK,True)
    text(config['advanced'][1],65,954,590,20)
    text(config['evidence'],740,1010,1100,15)

    text(config['caveat'],50,1049,1810,18,'#9A3412',True)
    c.showPage();c.save()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,default=ROOT,
                   help='checkout or extracted source tree containing the hash-verified inputs')
    args=p.parse_args()
    out=ROOT/'submission';out.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))
    assert manifest['track_a_commit']=='80529fbfddf58b58735963f6a35847e22dedeadc'
    assert manifest['fix_commit']=='e1ea45b'
    for path in INPUTS:
        file=args.input_dir/path
        actual=hashlib.sha256(file.read_bytes()).hexdigest()
        assert actual==manifest['inputs_sha256'][path], f'Input hash mismatch: {path}'
    for path,expected in manifest['tested_source_lf_sha256'].items():
        actual=hashlib.sha256((args.input_dir/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        assert actual==expected, f'Tested source mismatch: {path}'
    ai=json.loads((args.input_dir/'docs/evidence/live-ai-results.json').read_text(encoding='utf-8'))
    markdown=(ROOT/'docs/report/technical-report.md').read_text(encoding='utf-8')
    assert len(ai['cases'])==14
    for case in ai['cases']:assert case['question'] in markdown,case['id']
    backend=json.loads((args.input_dir/'docs/evidence/track-a/remaining-checks.json').read_text(encoding='utf-8'))
    assert backend['summary']=={'Pass':163,'Fail':4,'Info':1}, 'Historical Track A observations changed'
    gui=json.loads((args.input_dir/'docs/evidence/track-a/gui-flow.json').read_text(encoding='utf-8'))
    assert Counter(r['outcome'] for r in gui['results'])=={'Pass':21,'Fail':1}, 'Historical GUI observations changed'
    current_backend=json.loads((args.input_dir/'docs/evidence/fixes-2026-11-17/backend.json').read_text(encoding='utf-8'))
    assert current_backend['summary']=={'Pass':173}, 'Follow-up backend evidence changed'
    current_gui=json.loads((args.input_dir/'docs/evidence/fixes-2026-11-17/gui-flow.json').read_text(encoding='utf-8'))
    assert Counter(r['outcome'] for r in current_gui['results'])=={'Pass':22}, 'Follow-up GUI evidence changed'
    current_ai=json.loads((args.input_dir/'docs/evidence/fixes-2026-11-17/assistant.json').read_text(encoding='utf-8'))
    assert current_ai['database_unchanged'] and len(current_ai['results'])==7
    followup=json.loads((args.input_dir/'docs/evidence/fixes-2026-11-17/summary.json').read_text(encoding='utf-8'))
    assert followup['original_suite']=={'Pass':65} and followup['diagram_checker']=={'Pass':851,'Fail':0}
    preview=ROOT/'output/documents';preview.mkdir(parents=True,exist_ok=True)
    images=[(p.as_posix().split('/app/')[-1],p.read_bytes()) for p in sorted((ROOT/'app/sample_images').glob('*.jpg'))]
    sql=(ROOT/'app/schema.sql').read_text(encoding='utf-8')
    images += [(f'SQL lot {lot}: {name}',bytes.fromhex(data)) for lot,name,data in re.findall(r"VALUES \((\d+),'([^']+)','image/jpeg',X'([0-9a-fA-F]+)'",sql)]
    assert len(images)==16
    inventory=[]
    for name,data in images:
        im=Image.open(io.BytesIO(data))
        inventory.append({'asset':name,'bytes':len(data),'size':list(im.size),'sha256':hashlib.sha256(data).hexdigest(),'exif_keys':list(im.getexif())})
    (preview/'image-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
    config=json.loads((ROOT/'docs/poster/poster.json').read_text(encoding='utf-8'))
    report(args.input_dir,out);poster(config,args.input_dir,out)
    checks={}
    for name,count in [('technical-report',13),('poster',1)]:
        path=out/(name+'.pdf');r=PdfReader(path)
        assert len(r.pages)==count
        assert all(len(p.extract_text() or '')>50 for p in r.pages)
        text='\n'.join(p.extract_text() or '' for p in r.pages)
        for member in ['Abd Alrahman Ismaik','Ali Alshamsi','Mohammad Arwani']:assert member in text
        checks[name]={'pages':len(r.pages),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    checks['track_a_commit']=manifest['track_a_commit']
    checks['fix_commit']=manifest['fix_commit']
    checks['inputs']={path:hashlib.sha256((args.input_dir/path).read_bytes()).hexdigest() for path in INPUTS}
    checks['checks']=['14 historical AI questions retained','original Track A failures retained and follow-up pass totals verified','7 poster entity names and 6 relationship names verified against Draw.io','tested application/test source hashes verified','13 report pages and 1 poster page','team identities in both PDFs','overflow guard passed']
    (preview/'build-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
