from . import jamp
from . import exception

import json
import requests

class Transport:
    def __init__(self, url):
        self.url = url

class HttpRpcTransport(Transport):
    def __init__(self, url):
        super().__init__(url)
        
    def send(self, msg):
        str = msg.serialize()
        
        str = '[' + str + ']'
        
        headers = {'Content-Type': 'x-application/jamp-push'}
        
        try:
            r = requests.post(self.url, data = str, headers = headers)
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise BaratineException(e)
    
    def querySync(self, msg):
        str = msg.serialize()
        str = '[' + str + ']'
        
        headers = {'Content-Type': 'x-application/jamp-rpc'}
        
        try:
            r = requests.post(self.url, data = str, headers = headers)
            
            if r.status_code != 200:
                raise exception.BaratineException('query error: {0} {1}'.format(r.status_code, r.text))
            
            try:
                list = json.loads(r.text)
            except ValueError as e:
                raise exception.BaratineException('unable to decode json response: {0}'.format(r.text), e)
            
            responses = []
            
            for array in list:
                msg = jamp.unserializeArray(array)
                
                responses.append(msg)
            
            return responses
            
        except requests.exceptions.RequestException as e:
            raise exception.BaratineException(e)

if __name__ == '__main__':
    transport = HttpRpcTransport('http://127.0.0.1:8085/s/pod')
    
    msg = jamp.QueryMessage(None, '', 123, '/map/foo', 'put', ['aaa', 'bbb'])
    responses = transport.querySync(msg)
    response = responses[0]
    assert type(response) == jamp.ReplyMessage
    assert response.queryId == 123
        
    msg = jamp.QueryMessage(None, '', 124, '/map/foo', 'getAll', None)
    responses = transport.querySync(msg)
    response = responses[0]
    assert type(response) == jamp.ReplyMessage
    assert response.queryId == 124
    assert response.value == {'aaa': 'bbb'}
    
    print('test passed')