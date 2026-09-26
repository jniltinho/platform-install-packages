import importlib.util,json,os,tempfile,unittest,io,time
from pathlib import Path
from unittest.mock import patch,Mock
import untimed_driver as d
class DriverTests(unittest.TestCase):
    def test_wrong_nonce_before_host(self):
        with patch.object(d.socket,'gethostname') as host:
            with self.assertRaises(d.Failed):d.main('bad','bad','bad')
            host.assert_not_called()
    def test_wrong_host_before_commands(self):
        with patch.object(d.socket,'gethostname',return_value='production'),patch.object(d.subprocess,'check_output') as run:
            with self.assertRaises(d.Failed):d.main('a'*32,'baseline-untimed-aaaaaaaa','bad')
            run.assert_not_called()
    def test_wrong_ip_before_auth(self):
        with patch.object(d.socket,'gethostname',return_value='kaltura-php74-baseline'),patch.object(d.subprocess,'check_output',return_value=b'[{"addr_info":[{"local":"192.168.56.20"}]}]'),patch.object(d,'sql') as sql:
            with self.assertRaises(d.Failed):d.main('a'*32,'baseline-untimed-aaaaaaaa','bad')
            sql.assert_not_called()
    def test_sql_write_blocked_before_credentials(self):
        with patch.object(d,'read_file') as read:
            for query in ['DELETE FROM entry','SELECT 1; DROP TABLE entry','UPDATE entry SET id=1']:
                with self.assertRaises(d.Failed):d.sql(query)
            read.assert_not_called()
    def test_api_error_never_exports_message(self):
        with self.assertRaisesRegex(d.Failed,'^API_START_SESSION_ERROR$'):
            d.api_value({'objectType':'KalturaAPIException','code':'START_SESSION_ERROR','message':'private-secret'})
    def test_api_error_arbitrary_code_sanitized(self):
        with self.assertRaisesRegex(d.Failed,'^API_REJECTED$'):d.api_value({'objectType':'KalturaAPIException','code':'secret!private'})
    def media(self):return {'objectType':'KalturaMediaEntry','id':'0_abcdefgh','partnerId':1,'status':2,'mediaType':1,'dataUrl':'not-exported'}
    def test_projection_preserves_wire_types_and_excludes_url(self):
        obj=self.media(); obj['status']='2'; self.assertEqual(d.media_projection(obj)['status'],'2');self.assertNotIn('dataUrl',d.media_projection(obj))
    def test_bool_not_integer_and_no_type_coercion(self):
        obj=self.media();obj['status']=True
        with self.assertRaises(d.Failed):d.media_projection(obj)
        self.assertFalse(d.typed_equal({'x':2},{'x':'2'}));self.assertFalse(d.typed_equal({'x':True},{'x':1}))
    def test_invalid_entry_identity(self):
        obj=self.media();obj['id']="0_a' OR 1"
        with self.assertRaises(d.Failed):d.media_projection(obj)
    def test_multipart_exact_bytes_and_queryless_credentials(self):
        data=b'\x00binary\xff';body,ctype=d.multipart({'ks':'privatevalue'},data,'a'*32)
        self.assertIn(b'name="ks"\r\n\r\nprivatevalue',body);self.assertIn(data,body);self.assertIn('multipart/form-data',ctype)
    def test_multipart_boundary_collision(self):
        with self.assertRaises(d.Failed):d.multipart({},b'baseline-'+b'a'*32,'a'*32)
    def test_multipart_header_injection(self):
        with self.assertRaises(d.Failed):d.multipart({'bad\r\nheader':'x'},b'video','a'*32)
    def test_source_binding_wrong_partner(self):
        with self.assertRaises(d.Failed):d.owned_storage(['1','2','0_abcdefgh','0','/opt/kaltura/web/content','x','2'],1,'0_abcdefgh','0')
    def test_source_binding_escape(self):
        with self.assertRaises(d.Failed):d.owned_storage(['1','1','0_abcdefgh','0','/opt/kaltura/web/content','../../../../etc/passwd','2'],1,'0_abcdefgh','0')
    def test_privacy_rejects_short_pattern(self):
        with self.assertRaises(d.Failed):d.privacy([b'x'],{})
    def test_missing_logger_stops_before_auth(self):
        with patch.object(d.Path,'exists',return_value=False),patch.object(d.Path,'is_file',return_value=False):
            with self.assertRaisesRegex(d.Failed,'APP_LOG_CONFIG_MISSING'):d.logging_preflight()
    def test_log_forwarder_detection(self):
        fake=Mock();fake.__str__=Mock(return_value='/etc/rsyslog.conf');fake.name='rsyslog.conf';fake.read_bytes.return_value=b'*.* @@remote:514'
        logger=Mock();logger.__str__=Mock(return_value='/opt/kaltura/app/configurations/logger.ini');logger.name='logger.ini';logger.read_bytes.return_value=b'writers.stream.name = Zend_Log_Writer_Stream'
        with patch.object(d.Path,'exists',return_value=True),patch.object(d.Path,'is_file',return_value=False),patch.object(d.Path,'rglob',return_value=[fake,logger]):
            with self.assertRaisesRegex(d.Failed,'REMOTE_LOG_FORWARDER'):d.logging_preflight()
    def test_filesync_native_concat_keeps_root_with_leading_slash(self):
        with patch.object(d.Path,'is_file',return_value=True):
            path,sync=d.owned_storage(['1','1','0_abcdefgh','0','/opt/kaltura/web','/content/source.mp4','2'],1,'0_abcdefgh','0')
        self.assertEqual(str(path),'/opt/kaltura/web/content/source.mp4');self.assertEqual(sync,1)
    def test_filesync_native_concat_keeps_trailing_root_slash(self):
        with patch.object(d.Path,'is_file',return_value=True):
            path,_=d.owned_storage(['1','1','0_abcdefgh','0','/opt/kaltura/web/','content/source.mp4','2'],1,'0_abcdefgh','0')
        self.assertEqual(str(path),'/opt/kaltura/web/content/source.mp4')
    def test_stream_detects_pattern_spanning_chunk_boundary(self):
        marker=b'invalid-secret-marker'
        data=b'x'*(1024*1024-5)+marker+b'y'*30
        budget={'bytes':0,'until':time.monotonic()+5}
        hits=d.scan_stream(io.BytesIO(data),[marker],budget)
        self.assertGreater(hits[0],0);self.assertEqual(budget['bytes'],len(data))
    def test_stream_absence_is_not_invented_hit(self):
        self.assertEqual(d.scan_stream(io.BytesIO(b'public'),[b'private-marker-xxxx'],{'bytes':0,'until':time.monotonic()+5}),[0])
    def test_stream_per_file_limit_stops(self):
        with self.assertRaisesRegex(d.Failed,'LOG_SCAN_BYTE_LIMIT'):d.scan_stream(io.BytesIO(b'12345'),[b'private-marker-xxxx'],{'bytes':0,'until':time.monotonic()+5},file_limit=4)
    def test_stream_total_limit_stops(self):
        with patch.object(d,'LOG_TOTAL_LIMIT',4):
            with self.assertRaisesRegex(d.Failed,'LOG_SCAN_BYTE_LIMIT'):d.scan_stream(io.BytesIO(b'12345'),[b'private-marker-xxxx'],{'bytes':0,'until':time.monotonic()+5})
    def test_stream_deadline_stops_before_read(self):
        stream=Mock()
        with self.assertRaisesRegex(d.Failed,'LOG_SCAN_DEADLINE'):d.scan_stream(stream,[b'private-marker-xxxx'],{'bytes':0,'until':0})
        stream.read.assert_not_called()
    def test_rotation_inode_rejected(self):
        with self.assertRaisesRegex(d.Failed,'LOG_ROTATED_OR_TRUNCATED'):d.log_continuity({'p':(1,2,9)},{'p':(1,3,9)})
    def test_truncation_rejected(self):
        with self.assertRaisesRegex(d.Failed,'LOG_ROTATED_OR_TRUNCATED'):d.log_continuity({'p':(1,2,9)},{'p':(1,2,8)})
    def test_removed_log_rejected(self):
        with self.assertRaisesRegex(d.Failed,'LOG_ROTATED_OR_REMOVED'):d.log_continuity({'p':(1,2,9)},{})
    def test_append_and_new_log_visible_at_cutoff_allowed(self):
        d.log_continuity({'p':(1,2,9)},{'p':(1,2,10),'new':(1,3,1)})
    def test_exact_cutoff_excludes_future_append(self):
        marker=b'private-marker-xxxx';budget={'bytes':0,'until':time.monotonic()+5}
        self.assertEqual(d.scan_stream(io.BytesIO(b'public'+marker),[marker],budget,byte_count=6),[0]);self.assertEqual(budget['bytes'],6)
    def test_early_eof_fails_cutoff(self):
        with self.assertRaisesRegex(d.Failed,'LOG_TRUNCATED_DURING_READ'):d.scan_stream(io.BytesIO(b'abc'),[b'private-marker-xxxx'],{'bytes':0,'until':time.monotonic()+5},byte_count=4)
if __name__=='__main__':unittest.main()
