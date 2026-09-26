"""Fail-closed four-process same-engine cumulative comparison."""
import importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('marker_compare',Path(__file__).resolve().parent.parent/'criteria-marker/attribute/compare.py')
marker=importlib.util.module_from_spec(spec);spec.loader.exec_module(marker)
MODES=['prior-filter','candidate-filter','prior-returns','candidate-returns']
CONTRACTS={'Criteria::getIterator':'Traversable','CriterionIterator::rewind':'void','CriterionIterator::valid':'bool','CriterionIterator::key':'mixed','CriterionIterator::current':'mixed','CriterionIterator::next':'void'}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def target(e):
    return e['severity']==8192 and e['message'].startswith('Creation of dynamic property ') and any(x in e['message'] for x in ('Criteria::$creteria_filter_attached','myCriteria::$hint'))
def native(events):
    labels={8192:'Deprecated',2:'Warning',8:'Notice'}
    return ''.join(f"{labels[e['severity']]}: {e['message']} in /audit/probe/{e['file']} on line {e['line']}\n" for e in events)
def normalized(events,variant):
    out=[]
    for e in events:
        x=dict(e)
        if x['file']==variant+'.php':
            x['file']='Criteria.php'
            if variant=='candidate' and x['line']>=39:x['line']-=1
        out.append(x)
    return out
def validate(records,ids):
    require([r['mode'] for r in records]==MODES,'Mode inventory')
    by={};targets={}
    for r in records:
        variant,corpus=r['mode'].split('-');b=r['body']
        require(type(r['exit']) is int and r['exit']==0,'Exit')
        require(json.loads(r['stdout'])==b and b['php'].startswith('8.3.'),'Output binding')
        require(b['source_sha256']['criteria']==ids['files'][variant+'.php'],'Criteria identity')
        if corpus=='filter':
            require(b['schema']==2 and b['variant']==variant,'Filter mode')
            require(b['source_sha256']['filter']==ids['files']['criteriaFilter.php'],'Filter identity')
            require(list(b['rows'])==marker.CASES and b['imports'] in ({},[]),'Filter inventory')
            marker.legacy(b['rows'])
            events=b['events'];chosen=[e for e in events if target(e)];targets[variant]=chosen
            require(bool(chosen) if variant=='prior' else not chosen,'Hierarchy diagnostic delta')
            if variant=='prior':
                for text in ['Criteria::$creteria_filter_attached','myCriteria::$hint','KalturaCriteria::$creteria_filter_attached']:
                    require(any(text in e['message'] for e in chosen),'Hierarchy control')
            unrelated=[e for e in events if 'UnrelatedMarkerControl::$fixtureMarker' in e['message']]
            require(len(unrelated)==1 and unrelated[0]['severity']==8192,'Unrelated negative control')
            require(not any('Return type of ' in e['message'] for e in events),'Prior return regression')
        else:
            require(b['variant']==variant and len(b['rows'])==16,'Return inventory/mode')
            require(b['contracts']==CONTRACTS and b['load_diagnostics']==[],'Return contract')
            require([x[0] for x in b['invalid_controls']]==['empty','exhausted'],'Invalid inventory')
            events=[]
            for name,value,diagnostics in b['invalid_controls']:
                require(value==[None,None] and len(diagnostics)==2,'Invalid values')
                for severity,message,file,line in diagnostics:
                    require(severity==2,'Invalid severity')
                    events.append(dict(severity=severity,message=message,file=file,line=line))
        require(r['stderr']==native(events),'Exact native stderr')
        by[r['mode']]=(b,normalized([e for e in events if not target(e)],variant))
    for corpus in ['filter','returns']:
        a,ae=by['prior-'+corpus];b,be=by['candidate-'+corpus]
        require(a['rows']==b['rows'],'Exact behavior/representation parity')
        require(ae==be,'Unrelated diagnostic parity')
    return {'status':'BOUNDED_NATIVE83_COMPOSITION_PARITY','filter_cases':19,'return_rows':16,'invalid_iterator_controls':2,'hierarchy_events_before':len(targets['prior']),'hierarchy_events_after':len(targets['candidate']),'strict_cross_engine_layout':'FAIL_RETAINED','cache_acceptance':False,'patch_selected':False,'application_acceptance':False}
