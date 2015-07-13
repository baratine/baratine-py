from . import jamp
from . import transport
from . import exception

class JampClient:
    def __init__(self, url):
        self.queryCount = 0
        
        url = url.strip()
        
        if url.find('ws:') == 0:
            url = 'http:' + url[3:]
        elif url.find('wss:') == 0:
            url = 'https:' + url[4:]
        
        if url.find('http:') == 0 or url.find('https:') == 0:
            self.transport = transport.HttpRpcTransport(url)
        else:
            raise exception.BaratineException('invalid url: {0}'.format(url))
        
    def send(self, service, method, args = None, headerMap = None):
        queryId = self.queryCount
        self.queryCount += 1
        
        msg = jamp.SendMessage(headerMap, service, method, args)
        
        return self.transport.send(msg)
    
    def query(self, service, method, args = None, headerMap = None):
        queryId = self.queryCount
        self.queryCount += 1
        
        msg = jamp.QueryMessage(headerMap, '/client', queryId, service, method, args)
                
        responseArray = self.transport.querySync(msg)
        
        if len(responseArray) == 0:
            raise exception.BaratineException('no response received')
        
        response = responseArray[0]
        
        if type(response) == jamp.ReplyMessage:
            return response.value
        elif type(response) == jamp.ErrorMessage:
            error = response.error
            
            if isinstance(error, dict) and error['message'] != None:
                error = error['message']
            else:
                error = str(error)
            
            raise exception.BaratineException(error)
        else:
            raise exception.BaratineException('unexpected response: ' + response)






if __name__ == '__main__':
    client = JampClient('http://127.0.0.1:8085/s/pod')
    
    value = client.send('/map/foo', 'clear')
    assert value == None
    
    value = client.send('/map/foo', 'size')
    assert value == None
    
    value = client.query('/map/foo', 'getAll')
    assert value == {}
    
    value = client.query('/map/foo', 'put', ['aaa', 'bbb'])
    assert value == 1
    
    value = client.query('/map/foo', 'getAll')
    assert value == {'aaa': 'bbb'}
    
    print('test passed')