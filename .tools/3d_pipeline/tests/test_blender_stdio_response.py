"""Local subprocess transport regressions; no Blender or provider execution."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.tools/3d_pipeline'))
from lib import mcp_stdio as route

SERVER=r'''
import json,sys,time,threading,subprocess
mode=sys.argv[1]
def send(value):
    print(json.dumps(value),flush=True)
init=json.loads(sys.stdin.readline())
if mode=='init_error':
    send({'jsonrpc':'2.0','id':1,'error':{'code':-32600,'message':'initialize rejected'}})
    sys.exit(0)
send({'jsonrpc':'2.0','id':1,'result':{'protocolVersion':'2024-11-05','serverInfo':{'name':'fixture','version':'1'}}})
notification=json.loads(sys.stdin.readline())
request=json.loads(sys.stdin.readline())
assert notification['method']=='notifications/initialized'
if mode=='eof': sys.exit(0)
if mode=='timeout':
    child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
    send({'jsonrpc':'2.0','method':'notifications/message','params':{'child_pid':child.pid}})
    time.sleep(60)
if mode=='delay':
    # Emulate a server that cancels outstanding work at client EOF.
    def answer():
        time.sleep(.2)
        send({'jsonrpc':'2.0','id':2,'result':{'tools':[{'name':'fixture'}]}})
    threading.Thread(target=answer,daemon=True).start()
    sys.stdin.read()
elif mode=='error':
    send({'jsonrpc':'2.0','id':2,'error':{'code':-32602,'message':'explicit tool error'}})
    sys.stdin.read()
elif mode=='wrong_id':
    send({'jsonrpc':'2.0','id':99,'result':{'tools':[]}})
    time.sleep(60)
elif mode=='stderr':
    sys.stderr.write('diagnostic '*10000);sys.stderr.flush()
    send({'jsonrpc':'2.0','id':2,'result':{'tools':[]}})
    sys.stdin.read()
elif mode=='request_once':
    send({'jsonrpc':'2.0','id':2,'result':{'observed_method':request['method']}})
    remaining=sys.stdin.read()
    assert remaining=='', 'Unexpected request replay'
'''


class AdapterStdioTests(unittest.TestCase):
    def run_fixture(self,mode,timeout=5,tool=None):
        receipt={}
        with patch.object(route,'_is_repository_blender_adapter',return_value=True):
            try:
                return route.call_stdio([sys.executable,'-u','-c',SERVER,mode],list_tools=tool is None,tool=tool,timeout_seconds=timeout,cwd=ROOT,lifecycle_receipt=receipt)
            finally:
                self.assertEqual(receipt['surviving_process_ids'],[])
                if receipt['root_pid'] and os.name=='nt': self.assertFalse(route._windows_pid_is_alive(receipt['root_pid']))
                self.last_receipt=receipt

    def test_only_exact_repository_wrapper_is_selected(self):
        command=['cmd.exe','/d','/c','call',str(ROOT/'.tools/3d_pipeline/wrappers/run_blender_hoi4_adapter.cmd')]
        self.assertTrue(route._is_repository_blender_adapter(command))
        for bad in (command+['extra'],command[:-1]+[str(ROOT/'elsewhere/run_blender_hoi4_adapter.cmd')],command[:-1]+[str(ROOT/'.tools/3d_pipeline/wrappers/run_meshy_mcp.cmd')],['python','server.py']):
            self.assertFalse(route._is_repository_blender_adapter(bad))

    def test_delayed_response_arrives_before_stdin_eof(self):
        self.assertEqual(self.run_fixture('delay')['tools'],[{'name':'fixture'}])
        self.assertTrue(self.last_receipt['initialized_before_request'])
        self.assertEqual(self.last_receipt['response_id_before_stdin_eof'],2)

    def test_fixture_reproduces_legacy_eof_cancellation(self):
        with patch.object(route,'_is_repository_blender_adapter',return_value=False):
            with self.assertRaisesRegex(route.MCPRouteError,'no JSON-RPC response'):
                route.call_stdio([sys.executable,'-u','-c',SERVER,'delay'],list_tools=True,timeout_seconds=5,cwd=ROOT)

    def test_early_eof_rejects_and_cleans_process(self):
        with self.assertRaisesRegex(route.MCPRouteError,'EOF before JSON-RPC id 2'): self.run_fixture('eof')

    def test_explicit_rpc_error_preserved(self):
        with self.assertRaisesRegex(route.MCPRouteError,'explicit tool error'): self.run_fixture('error')

    def test_initialize_error_sends_no_followup(self):
        with self.assertRaisesRegex(route.MCPRouteError,'initialize rejected'): self.run_fixture('init_error')

    def test_timeout_cleans_owned_process_tree(self):
        with self.assertRaisesRegex(route.MCPRouteError,'timed out'): self.run_fixture('timeout',timeout=1)
        if os.name=='nt': self.assertGreaterEqual(len(self.last_receipt['owned_process_ids_at_cleanup']),2)

    def test_wrong_response_id_cannot_complete_call(self):
        with self.assertRaisesRegex(route.MCPRouteError,'timed out'): self.run_fixture('wrong_id',timeout=1)

    def test_stderr_is_drained_without_blocking_response(self):
        self.assertEqual(self.run_fixture('stderr')['tools'],[])

    def test_mutation_request_is_sent_only_once(self):
        self.assertEqual(self.run_fixture('request_once',tool='fixture_mutation')['observed_method'],'tools/call')
        self.assertEqual(self.last_receipt['request_replays'],0)

    def test_other_routes_keep_existing_exchange(self):
        server="import sys,json; rows=[json.loads(line) for line in sys.stdin]; print(json.dumps({'jsonrpc':'2.0','id':2,'result':{'messages':len(rows)}}))"
        receipt={}
        result=route.call_stdio([sys.executable,'-u','-c',server],list_tools=True,timeout_seconds=5,lifecycle_receipt=receipt)
        self.assertEqual(result['messages'],3)
        self.assertNotIn('exchange',receipt)


if __name__=='__main__': unittest.main()
