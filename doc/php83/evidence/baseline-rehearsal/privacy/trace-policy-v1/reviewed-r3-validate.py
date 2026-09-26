"""Bounded synthetic contract. Negative controls must keep leaking; never whole privacy PASS."""
NAMES=['mixed-arguments','writer-roundtrip','exception','previous','error-err','error-alert','error-crit','intrinsic-control','prerendered-control','extras-control','plain-control']
def validate(report,policy,expected_loaded):
 if report['policy'] is not policy or report['privacy_acceptance'] is not False:raise ValueError('Policy identity')
 if not expected_loaded or report['loaded']!=expected_loaded:raise ValueError('Loaded source identity')
 if [r['case'] for r in report['records']]!=NAMES:raise ValueError('Exact cases')
 if report['negative_controls_expected_to_leak']!=['intrinsic-control','prerendered-control','extras-control']:raise ValueError('Negative inventory')
 if set(report['reject_filter'])!={'empty_sink','observer_not_called','formatter_not_called'} or any(v is not True for v in report['reject_filter'].values()):raise ValueError('Rejected event changed')
 for row in report['records']:
  name=row['case'];
  for flag in ['full_marker','prefix_marker','redaction_marker','writer_same_message','mixed_types_exact']:
   if type(row[flag]) is not bool:raise ValueError('Typed flag')
  negative=name in report['negative_controls_expected_to_leak']
  for flag in ['exception_state_unchanged','observed_same_bytes','structural_preserved','context_preserved']:
   if row[flag] is not True:raise ValueError(flag)
  if type(row['priority']) is not int or row['priority']!=({'error-alert':1,'error-crit':2}.get(name,3)):raise ValueError('Priority')
  if name=='plain-control':
   if row['full_marker'] or row['prefix_marker']:raise ValueError('Plain changed')
  elif negative:
   if not row['prefix_marker']:raise ValueError('Negative leak hidden')
   if name!='prerendered-control' and not row['full_marker']:raise ValueError('Negative full leak hidden')
  elif policy:
   if row['full_marker'] or row['prefix_marker'] or not row['redaction_marker']:raise ValueError('Trace argument leak')
   if not row['writer_same_message'] or row['formatter_type']!='string':raise ValueError('Throwable copy boundary')
  elif not row['prefix_marker']:raise ValueError('Original leak control missing')
  if policy and name=='mixed-arguments' and not row['mixed_types_exact']:raise ValueError('Argument count/type display')
 return {'status':'BOUNDED_TRACE_DISPLAY_CONTRACT','negative_controls':'KNOWN_LEAKS_PRESERVED','privacy_acceptance':False}
