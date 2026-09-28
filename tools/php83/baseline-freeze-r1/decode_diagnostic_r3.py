"""Closed ffprobe shape/numeric facts only; not a decoder acceptance predicate."""
from fractions import Fraction
import re
FIELDS={'width':4096,'height':2160,'nb_read_frames':1000000,'sample_rate':384000,'channels':64}
def integer(value,maximum):
 if value is None:return {'state':'MISSING','value':None}
 if type(value) not in (str,int) or len(str(value))>16 or not str(value).isascii() or not str(value).isdigit() or str(int(value))!=str(value):return {'state':'INVALID','value':None}
 number=int(value)
 if number>maximum:return {'state':'OUT_OF_RANGE','value':None}
 return {'state':'NUMBER','value':number}
def ratio(value):
 if value is None:return {'state':'MISSING','numerator':None,'denominator':None}
 if type(value) is not str or re.fullmatch(r'(?:[0-9]{1,9}/[0-9]{1,9}|[0-9]{1,6}(?:\.[0-9]{1,9})?)',value) is None:return {'state':'INVALID','numerator':None,'denominator':None}
 try:n=Fraction(value)
 except (ValueError,ZeroDivisionError):return {'state':'INVALID','numerator':None,'denominator':None}
 if n<0 or n.numerator>1000000000 or n.denominator>1000000000:return {'state':'OUT_OF_RANGE','numerator':None,'denominator':None}
 return {'state':'NUMBER','numerator':n.numerator,'denominator':n.denominator}
def project(value):
 out={'schema':1,'root_object':type(value) is dict,'streams_array':False,'stream_count':None,'video_count':0,'audio_count':0,'data_count':0,'other_count':0,'streams':[],'duration':ratio(None),'raw_values_exported':False}
 if type(value) is not dict:return out
 fmt=value.get('format');out['duration']=ratio(fmt.get('duration') if type(fmt) is dict else None)
 rows=value.get('streams')
 if type(rows) is not list:return out
 out['streams_array']=True
 if len(rows)>32:return out
 out['stream_count']=len(rows)
 for row in rows:
  kind=row.get('codec_type') if type(row) is dict else None
  kind=kind if kind in ('video','audio','data') else 'other';out[kind+'_count']+=1
  if len(out['streams'])>=4:continue
  row=row if type(row) is dict else {};codec=row.get('codec_name')
  item={'kind':kind.upper(),'codec':codec.upper() if codec in ('h264','aac','timed_id3') else 'MISSING' if codec is None else 'OTHER','avg_frame_rate':ratio(row.get('avg_frame_rate'))}
  item.update({k:integer(row.get(k),m) for k,m in FIELDS.items()});out['streams'].append(item)
 return out

def validate(v):
 def need(ok):
  if not ok:raise ValueError('DECODE_DIAGNOSTIC_SCHEMA')
 need(type(v) is dict and set(v)=={'schema','root_object','streams_array','stream_count','video_count','audio_count','data_count','other_count','streams','duration','raw_values_exported'} and type(v['schema']) is int and v['schema']==1 and v['raw_values_exported'] is False)
 need(type(v['root_object']) is bool and type(v['streams_array']) is bool and (v['stream_count'] is None or type(v['stream_count']) is int and 0<=v['stream_count']<=32))
 need(all(type(v[k]) is int and 0<=v[k]<=32 for k in ('video_count','audio_count','data_count','other_count')))
 need(type(v['streams']) is list and len(v['streams'])<=4)
 def checked_ratio(row):
  need(type(row) is dict and set(row)=={'state','numerator','denominator'} and row['state'] in ('MISSING','INVALID','OUT_OF_RANGE','NUMBER'))
  if row['state']=='NUMBER':need(type(row['numerator']) is int and 0<=row['numerator']<=1000000000 and type(row['denominator']) is int and 1<=row['denominator']<=1000000000)
  else:need(row['numerator'] is None and row['denominator'] is None)
 checked_ratio(v['duration'])
 for row in v['streams']:
  need(type(row) is dict and set(row)==set(FIELDS)|{'kind','codec','avg_frame_rate'} and row['kind'] in ('VIDEO','AUDIO','DATA','OTHER') and row['codec'] in ('H264','AAC','TIMED_ID3','OTHER','MISSING'));checked_ratio(row['avg_frame_rate'])
  for k,maximum in FIELDS.items():
   d=row[k];need(type(d) is dict and set(d)=={'state','value'} and d['state'] in ('MISSING','INVALID','OUT_OF_RANGE','NUMBER'))
   need(type(d['value']) is int and 0<=d['value']<=maximum if d['state']=='NUMBER' else d['value'] is None)
 return v
