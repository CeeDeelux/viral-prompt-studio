import unittest
from unittest.mock import patch, MagicMock
import socket
import app
import extractor
import local_runtime as policy

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden in offline tests'))
        self.network.start()
        app.app.testing = True
        self.client = app.app.test_client()
        app.extraction_status['running'] = False
        app.extracted_subtitles.update(content='', videos_processed=0)
    def tearDown(self):
        self.network.stop()
    def test_health(self):
        data = self.client.get('/api/health').get_json()
        self.assertEqual(data['app'], 'viral-prompt-studio')
        self.assertEqual(data['locale'], 'en')
        self.assertFalse(data['external_operations_enabled'])
    def test_all_external_routes_blocked(self):
        with patch.object(app, 'extract_viral_content') as extract, patch.object(policy, 'generate_text') as generate:
            for endpoint in ('extract', 'generate-viral-dna', 'generate-script'):
                self.assertEqual(self.client.post('/api/'+endpoint, json={}).status_code, 403)
            extract.assert_not_called(); generate.assert_not_called()
    def test_provider_boundaries_blocked(self):
        for call in (lambda: extractor.get_viral_videos('https://www.youtube.com/@test',1),
                     lambda: extractor.get_transcript_apify('test'),
                     lambda: policy.generate_text('test','test')):
            with self.assertRaises(PermissionError): call()
    def test_empty_state(self):
        self.assertEqual(self.client.get('/api/status').status_code,200)
        self.assertEqual(self.client.get('/api/subtitles').status_code,404)
    def test_url_normalization(self):
        self.assertEqual(extractor.clean_url('https://www.youtube.com/@test/videos?other=1'),
                         'https://www.youtube.com/@test/videos?view=0&sort=p')
    def test_input_validation(self):
        with patch.object(policy, 'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='mock'):
            for url,limit in [('http://127.0.0.1/',1),('https://evil.test/@x',1),('https://www.youtube.com/watch',1),('https://www.youtube.com/@x',21),('https://www.youtube.com/@x',True)]:
                self.assertEqual(self.client.post('/api/extract',json={'channel_url':url,'limit':limit}).status_code,400)
    def test_concurrent_extraction_rejected(self):
        app.extraction_lock.acquire()
        try:
            with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='mock'):
                self.assertEqual(self.client.post('/api/extract',json={'channel_url':'https://www.youtube.com/@test','limit':1}).status_code,409)
        finally: app.extraction_lock.release()
    def test_analysis_route_mock_only(self):
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='mock'), patch.object(policy,'generate_text',return_value='MOCK_ANALYSIS') as generate:
            response=self.client.post('/api/generate-viral-dna',json={'subtitles':'MOCK_INPUT'})
            self.assertEqual(response.get_json()['viral_dna'],'MOCK_ANALYSIS')
            self.assertIn('English',generate.call_args.args[0])
    def test_script_route_mock_only(self):
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='mock'), patch.object(policy,'generate_text',return_value='MOCK_RESULT') as generate:
            response=self.client.post('/api/generate-script',json={'viral_dna':'MOCK_DNA','topic':'MOCK_TOPIC'})
            self.assertEqual(response.get_json()['script'],'MOCK_RESULT')
            self.assertIn('original work',generate.call_args.args[0])
    def test_actual_sdk_mapping_mock_only(self):
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='mock'), patch.object(policy.genai,'Client') as factory:
            client=factory.return_value.__enter__.return_value
            client.models.generate_content.return_value.text='MOCK_RESULT'
            self.assertEqual(policy.generate_text('SYSTEM','INPUT'),'MOCK_RESULT')
            self.assertEqual(client.models.generate_content.call_args.kwargs['config'].system_instruction,'SYSTEM')
    def test_socket_connection(self):
        client=app.socketio.test_client(app.app)
        self.assertTrue(client.is_connected())
        client.disconnect()
    def test_completion_after_storage(self):
        with patch.object(app,'extract_viral_content',return_value={'content':'MOCK','videos_processed':1}), patch.object(app.socketio,'emit') as emit:
            app.run_extraction('unused',1)
            self.assertEqual(app.extracted_subtitles['content'],'MOCK')
            self.assertEqual(emit.call_args.args[1]['status'],'complete')
            self.assertFalse(app.extraction_status['running'])
    def test_mode_configuration_gate(self):
        headers={'X-Viral-DNA-Local':'1'}
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',False), patch.object(policy,'provider_key',return_value=''):
            self.assertEqual(self.client.post('/api/mode',json={'mode':'online'},headers=headers).status_code,400)
            self.assertFalse(policy.EXTERNAL_OPERATIONS_ENABLED)
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',False), patch.object(policy,'provider_key',return_value='MOCK'):
            self.assertEqual(self.client.post('/api/mode',json={'mode':'online'}).status_code,403)
            self.assertEqual(self.client.post('/api/mode',json={'mode':'online'},headers=headers).status_code,200)
            self.assertTrue(policy.EXTERNAL_OPERATIONS_ENABLED)
            self.assertEqual(self.client.post('/api/mode',json={'mode':'offline'},headers=headers).status_code,200)
            self.assertFalse(policy.EXTERNAL_OPERATIONS_ENABLED)
    def test_script_languages(self):
        with patch.object(policy,'EXTERNAL_OPERATIONS_ENABLED',True), patch.object(policy,'provider_key',return_value='MOCK'), patch.object(policy,'generate_text',return_value='MOCK') as generate:
            for language,expected in [('en','English'),('cs','cs-CZ')]:
                response=self.client.post('/api/generate-script',json={'viral_dna':'MOCK','topic':'MOCK','language':language})
                self.assertEqual(response.status_code,200)
                self.assertIn(expected,generate.call_args.args[0])
            generate.reset_mock()
            self.assertEqual(self.client.post('/api/generate-script',json={'viral_dna':'MOCK','topic':'MOCK','language':'invalid'}).status_code,400)
            generate.assert_not_called()
    def test_project_configuration_resolution(self):
        import os
        with patch.dict(os.environ,{},clear=True), patch.object(policy,'PROJECT_ENV',{'GEMINI_API_KEY':'MOCK_G','APIFY_API_KEY':'MOCK_A'}):
            self.assertTrue(policy.configuration_ready())
            self.assertEqual(policy.provider_key('gemini'),'MOCK_G')
            self.assertEqual(policy.provider_key('apify'),'MOCK_A')
            self.assertEqual(policy.PROJECT_ENV_PATH.name,'.env')
if __name__ == '__main__': unittest.main(verbosity=2)
