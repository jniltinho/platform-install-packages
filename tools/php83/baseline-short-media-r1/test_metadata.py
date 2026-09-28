import copy
import unittest
import metadata as m

class Tests(unittest.TestCase):
    def fixture(self):
        return dict(objectType='KalturaFlavorAssetListResponse',totalCount=1,objects=[dict(
            objectType='KalturaFlavorAsset',id=m.ORIGINAL,entryId=m.ENTRY,partnerId=102,
            status=2,isOriginal=True,version='2',flavorParamsId=0,size=1475,fileExt='mp4',
            tags='PRIVATE',description='PRIVATE',url='https://PRIVATE')])
    def run_case(self, f):
        return m.collect(lambda **kw:f)
    def test_fixed_request_projection(self):
        calls=[]
        def call(**kw): calls.append(kw); return self.fixture()
        out=m.collect(call)
        self.assertEqual(calls,[dict(service='flavorasset',action='list',**{'filter:objectType':'KalturaFlavorAssetFilter','filter:entryIdEqual':m.ENTRY,'pager:pageSize':'51','pager:pageIndex':'1'})])
        self.assertNotIn('PRIVATE',str(out)); self.assertFalse(out['playback_tested'])
    def test_wrong_ownership(self):
        for field,value in [('entryId','0_aaaaaaaa'),('partnerId',99)]:
            f=self.fixture();f['objects'][0][field]=value
            with self.assertRaises(m.Rejected):self.run_case(f)
    def test_partial_or_excess_list(self):
        for count in [0,2,51,True,None]:
            f=self.fixture();f['totalCount']=count
            with self.assertRaises(m.Rejected):self.run_case(f)
    def test_source_binding(self):
        for field,value in [('id','0_aaaaaaaa'),('version',3),('isOriginal',False)]:
            f=self.fixture();f['objects'][0][field]=value
            with self.assertRaises(m.Rejected):self.run_case(f)
    def test_types(self):
        for field,value in [('status',True),('size',1.0),('version','02'),('isOriginal',1),('fileExt','secret/path'),('id','SECRET')]:
            f=self.fixture();f['objects'][0][field]=value
            with self.assertRaises(m.Rejected):self.run_case(f)
    def test_native_error_status(self):
        f=self.fixture();f['objects'][0]['status']=-1
        self.assertEqual(self.run_case(f)['assets'][0]['status'],-1)
    def test_duplicates(self):
        f=self.fixture();f['totalCount']=2;f['objects']*=2
        with self.assertRaisesRegex(m.Rejected,'DUPLICATE'):self.run_case(f)
    def test_error_sanitized(self):
        def call(**kw):raise ValueError('PRIVATE')
        with self.assertRaisesRegex(m.Rejected,'^API_CALL_FAILED$'):m.collect(call)
    def test_api_exception(self):
        with self.assertRaises(m.Rejected):self.run_case(dict(objectType='KalturaAPIException',message='PRIVATE'))

if __name__=='__main__':unittest.main()
