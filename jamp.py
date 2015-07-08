import json
from . import exception

def unserializeJson(str):
    obj = json.loads(str)
    
    msg = unserializeArray(obj)
    
    return msg

def unserializeArray(array):
    type = array[0]
    
    if type == 'reply':
        if len(array) < 5:
            raise exception.BaratineException('incomplete message for JAMP type: {0}'.format(type));

        headers = array[1]
        fromAddress = array[2]
        queryId = array[3]
        result = array[4]
      
        msg = ReplyMessage(headers, fromAddress, queryId, result)
      
        return msg
    
    elif type == 'error':
        if len(array) < 5:
            raise exception.BaratineException('incomplete message for JAMP type: {0}'.format(type))
        
        (headers, serviceName, queryId, result) = array[1:5]
        
        if len(array) > 5:
            result = array[4:]
        
        msg = ErrorMessage(headers, serviceName, queryId, result)
        
        return msg
    
    elif type == 'query':
        if len(array) < 6:
            raise exception.BaratineException('incompatible message for JAMP type: {0}'.format(type))

        (headers, fromAddress, queryId, serviceName, methodName) = array[1:6]
        
        args = array[6:]
        
        msg = QueryMessage(headers, fromAddress, queryId, serviceName, methodName, args)
        
        return msg
        
    elif type == 'send':
        if len(array) < 4:
            raise exception.BaratineException('incomplete message for JAMP type: {0}'.format(type))
        
        (headers, serviceName, methodName) = array[1:4]
        
        args = array[4:]
        
        msg = SendMessage(headers, serviceName, methodName, args)
        
        return msg
    
    else:
        raise exception.BaratineException('unknown JAMP type: {0}'.format(type))

class Message:
    def __init__(self, headers):
        self.headers = headers
    
    def serialize(self):
        array = self.serializeImpl()
        
        str = json.dumps(array)
        
        return str
    
    def buildUrl(self, baseUrl, serviceName, methodName, args = None):
        url = baseUrl + serviceName + '?m=' + methodName
        
        for i, arg in enumerate(args):
            url += '&p{0}={1}'.format(i, arg)
        
        return url

class SendMessage(Message):
    def __init__(self, headers, serviceName, methodName, args):
        super().__init__(headers)
        
        self.serviceName = serviceName
        self.methodName = methodName
        
        self.args = args
    
    def serializeImpl(self):
        array = []
        
        array.append('send')
        array.append(self.headers)
        array.append(self.serviceName)
        array.append(self.methodName)
        
        if self.args != None:
            array.extend(self.args)
        
        return array
    
    def toUrl(self, baseUrl):
        return self.buildUrl(baseUrl, self.serviceName, self.methodName, self.args)
    
class QueryMessage(Message):
    def __init__(self, headers, fromAddress, queryId, serviceName, methodName, args):
        super().__init__(headers)
        
        self.fromAddress = fromAddress
        self.queryId = queryId
        
        self.serviceName = serviceName
        self.methodName = methodName
        
        self.args = args
        
        if fromAddress is None:
            self.fromAddress = 'me'
    
    def serializeImpl(self):
        array = []
        
        array.append('query')
        array.append(self.headers)
        array.append(self.fromAddress)
        array.append(self.queryId)
        array.append(self.serviceName)
        array.append(self.methodName)
        
        if self.args != None:
            array.extend(self.args)
        
        return array
        
    def toUrl(self, baseUrl):
        return self.buildUrl(baseUrl, self.serviceName, self.methodName, self.args)

    def __repr__(self):
        return '{0}[{1},{2},{3}]'.format(self.__class__.__name__, self.queryId, self.serviceName, self.methodName)

class ReplyMessage(Message):
    def __init__(self, headers, fromAddress, queryId, value):
        super().__init__(headers)
        
        self.fromAddress = fromAddress
        self.queryId = queryId
        
        self.value = value
    
    def serializeImpl(self):
        array = []
        
        array.append('reply')
        array.append(self.headers)
        array.append(self.fromAddress)
        array.append(self.queryId)
        array.append(self.value)
        
        return array
    
    def __repr__(self):
        return '{0}[{1},{2}]'.format(self.__class__.__name__, self.queryId, self.value)
    
class ErrorMessage(Message):
    def __init__(self, headers, toAddress, queryId, error):
        super().__init__(headers)
        
        self.address = toAddress
        self.queryId = queryId
        
        self.error = error
    
    def serializeImpl(self):
        array = []
        
        array.append('error')
        array.append(self.headers)
        array.append(self.address)
        array.append(self.queryId)
        array.append(self.error)
        
        return array
    
    def __repr__(self):
        return '{0}[{1},{2}.{3}]'.format(self.__class__.__name__, self.address, self.queryId, self.error)

class Response:
    def __init__(self, status = None, error = None, value = None, rawResponse = None, isError = None):
        self.status = status
        self.error = error
        self.value = value
        self.rawResponse = rawResponse
        self.isError = isError

class RawResponse(Response):
    def __init__(self, rawResponse):
        self.rawResponse = rawResponse

class ErrorResponse(Response):
    def __init__(self, rawResponse, status, error):
        self.rawResponse = rawResponse
        
        self.status = status
        self.error = error
        self.isError = true




if __name__ == '__main__':
    str = '["reply", {"key0": "value0"}, "/from0", 123, "responseValue"]'
    msg = unserializeJson(str)
    assert type(msg) == ReplyMessage
    assert msg.fromAddress == '/from0'
    assert msg.queryId == 123
    assert msg.value == 'responseValue'    
    assert msg.serialize() == str
    
    str = '["query", {"key0": "value0"}, "/from0", 123, "/service0", "method0", "arg0", "arg1"]'
    msg = unserializeJson(str)    
    assert type(msg) == QueryMessage
    assert msg.fromAddress == '/from0'
    assert msg.queryId == 123
    assert msg.serviceName == '/service0'
    assert msg.methodName == 'method0'
    assert msg.args == ['arg0', 'arg1']
    assert msg.serialize() == str
    
    str = '["error", {}, "/to0", 123, "error0"]'
    msg = unserializeJson(str)
    assert type(msg) == ErrorMessage
    assert msg.address == '/to0'
    assert msg.queryId == 123
    assert msg.error == 'error0'
    assert msg.serialize() == str
    
    str = '["send", {}, "/service0", "method0", "arg0", "arg1"]'
    msg = unserializeJson(str)
    assert type(msg) == SendMessage
    assert msg.serviceName == '/service0'
    assert msg.methodName == 'method0'
    assert msg.args == ['arg0', 'arg1']
    assert msg.serialize() == str
    
    print('test passed')
