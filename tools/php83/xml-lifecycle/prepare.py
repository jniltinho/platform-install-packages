"""Read-only pinned original/exp11 subsets plus synthetic local SOAP documents."""
import argparse,hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
PINS=json.loads((HERE/'source-pins.json').read_text())
SCHEMA=b'''<?xml version="1.0"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:xml-lifecycle-types" xmlns:t="urn:xml-lifecycle-types" elementFormDefault="qualified">
<xsd:element name="Ping"><xsd:complexType><xsd:sequence><xsd:element name="value" type="xsd:string"/></xsd:sequence></xsd:complexType></xsd:element>
<xsd:element name="PingResponse"><xsd:complexType><xsd:sequence><xsd:element name="value" type="xsd:string"/></xsd:sequence></xsd:complexType></xsd:element>
</xsd:schema>
'''
WSDL=b'''<?xml version="1.0"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:tns="urn:xml-lifecycle" xmlns:t="urn:xml-lifecycle-types" targetNamespace="urn:xml-lifecycle">
<types><xsd:schema targetNamespace="urn:xml-lifecycle"><xsd:import namespace="urn:xml-lifecycle-types" schemaLocation="file:///audit/probe/fixtures/types.xsd"/></xsd:schema></types>
<message name="PingInput"><part name="parameters" element="t:Ping"/></message>
<message name="PingOutput"><part name="parameters" element="t:PingResponse"/></message>
<portType name="FixturePort"><operation name="ping"><input message="tns:PingInput"/><output message="tns:PingOutput"/></operation></portType>
<binding name="FixtureBinding" type="tns:FixturePort"><soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/><operation name="ping"><soap:operation soapAction="urn:xml-lifecycle:ping"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation></binding>
<service name="FixtureService"><port name="Fixture" binding="tns:FixtureBinding"><soap:address location="urn:xml-lifecycle:transport"/></port></service>
</definitions>
'''
RESPONSE=b'''<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="urn:xml-lifecycle-types"><soap:Body><t:PingResponse><t:value>SYNTHETIC_RESPONSE</t:value></t:PingResponse></soap:Body></soap:Envelope>
'''
def prepare(out):
 if out.exists():raise ValueError('Refuse existing stage')
 payload={}
 for variant,meta in PINS.items():
  archive=Path(meta['archive'])
  if H(archive.read_bytes())!=meta['archive_sha256']:raise ValueError('Archive drift')
  with zipfile.ZipFile(archive) as z:
   for p,h in meta['files'].items():
    b=z.read(meta['root']+p)
    if H(b)!=h:raise ValueError('Source drift')
    payload[variant+'/'+p]=b
 for n in ['probe.php','run.sh']:payload[n]=(HERE/n).read_bytes()
 payload.update({'fixtures/good.wsdl':WSDL,'fixtures/inner.wsdl':WSDL,
   'fixtures/types.xsd':SCHEMA,'fixtures/malformed.wsdl':b'<definitions><broken></definitions>',
   'fixtures/response.xml':RESPONSE,'fixtures/marker.txt':b'SYNTHETIC_LIFECYCLE_MARKER'})
 out.mkdir(parents=True)
 for n,b in payload.items():
  p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 for v in PINS:
  for d in ['configurations','vendor/ZendFramework/library']:(out/v/d).mkdir(parents=True)
 manifest={'files':{n:H(b) for n,b in sorted(payload.items())},'archives':{v:m['archive_sha256'] for v,m in PINS.items()},'source_mode':'unchanged five-class subsets; not full app/bootstrap or real transport','empty_synthetic_directories':['configurations','vendor/ZendFramework/library']}
 (out/'identities.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return {'manifest_sha256':H((out/'identities.json').read_bytes()),'files':len(payload),'application_patch_selected':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();print(json.dumps(prepare(a.out)))
