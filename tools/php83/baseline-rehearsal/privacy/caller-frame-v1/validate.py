"""Typed observations contract: original/repaired useful caller, overlay negative."""
import json
EMITTERS=[('UsefulEmitter','emit'),('OtherStream','_write'),('KalturaSerializableStreamSibling','_write')]
def validate(body,variant,expected_sources):
 if variant not in ('original','overlay','repaired'):raise ValueError('Variant')
 if not expected_sources or body.get('loaded')!=expected_sources:raise ValueError('Loaded closure')
 expected=[]
 for c,f in EMITTERS:
  for kind in ('string','throwable'):
   expected.append(dict(case=c+'::'+f+'/'+kind,caller='KalturaSerializableStream->_write' if variant=='overlay' else c+'->'+f,extra='SYNTHETIC_EXTRA',priority='3',message_present=True,observer_same_message=True,observer_extra='SYNTHETIC_EXTRA',observer_logMethod_class='LogMethod',message_unchanged=True,writer_class='KalturaSerializableStream',formatter_class='Zend_Log_Formatter_Simple'))
 if json.dumps(body.get('records'),sort_keys=True)!=json.dumps(expected,sort_keys=True):raise ValueError('Typed caller contract')
 if not isinstance(body.get('diagnostics'),list):raise ValueError('Diagnostics retained')
 return {'status':'BOUNDED_CALLER_CONTRACT_PASS','variant':variant,'cases':6,'application_acceptance':False}
