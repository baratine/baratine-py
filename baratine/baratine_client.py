from . import jamp_client
from . import exception

import inspect

class BaratineClient(object):
    def __init__(self, url):
        self.jampClient = jamp_client.JampClient(url)

    def lookup(self, url):
        return self._lookup(url)
    
    def _lookup(self, url):
        return Proxy(self.jampClient, url)
    
    def close(self):
        self.jampClient.close()

class Proxy(object):
    def __init__(self, jampClient, serviceName):
        self.jampClient = jampClient
        self.serviceName = serviceName
    
    def __getattr__(self, name, clsName = None):
        return CallProxy(self.jampClient, self.serviceName, name, clsName)
    
    def _lookup(self, url):
        return Proxy(self.jampClient, self.serviceName + url)
    
    def _as(self, clsName):
        return ClassProxy(self, clsName)

class CallProxy(object):
    def __init__(self, jampClient, serviceName, methodName, clsName = None):
        self.jampClient = jampClient
        self.serviceName = serviceName
        self.methodName = methodName
        self.clsName = clsName
    
    def __call__(self, *args, **kwargs):
        argList = []
        argList.extend(args)
            
        if self.clsName != None:
            methods = dir(self.clsName)
        
            method = getattr(self.clsName, self.methodName)
            
            if (not callable(method)):
                raise AttributeError('attribute is not a method {0}.{1}'.format(self.clsName, self.methodName))
            
            formalArgs = inspect.getfullargspec(method)
            
            for i in range(len(args), len(formalArgs.args)):
                argName = formalArgs.args[i]
                
                if argName in kwargs:
                    argList.append(kwargs[argName])
                else:
                    break
            
            actualCount = len(argList)
            formalCount = len(formalArgs.args)
            defaultCount = len(formalArgs.defaults) if formalArgs.defaults != None else 0
            
            requiredCount = formalCount - defaultCount
            
            if actualCount < requiredCount:
                raise exception.BaratineException('required {0} arguments but saw only {1}'.format(requiredCount, actualCount))
            elif actualCount > formalCount:
                raise exception.BaratineException('needed only {0} arguments but saw {1}'.format(formalCount, actualCount))

            for i in range(actualCount, formalCount):
                formalArg = formalArgs[i]
                
                value = formalArgs.defaults[i - requiredCount]
                                
                argList.append(value)
            
        return self.jampClient.query(self.serviceName, self.methodName, argList)

class ClassProxy(object):
    def __init__(self, proxy, clsName):
        self.proxy = proxy
        self.clsName = clsName
        
    def _lookup(self, url):
        proxy = self.proxy._lookup(url)
        
        return ClassProxy(proxy, self.clsName)

    def _as(self, clsName):
        return ClassProxy(self.proxy, clsName)

    def __getattr__(self, name):
        return self.proxy.__getattr__(name, self.clsName)







if __name__ == '__main__':
    client = BaratineClient('http://127.0.0.1:8085/s/pod')
    
    proxy = client.lookup('/map/foo')
    value = proxy.clear()
    
    value = proxy.getAll()
    assert value == {}
    
    value = proxy.put('aaa', 'bbb')
    assert value == 1
    
    value = proxy.getAll()
    assert value == {'aaa': 'bbb'}
    
    class MapService:
        def size(self):
            pass
        def getAll(self):
            pass
        def put(self, key, value):
            pass
        
    clsProxy = proxy._as(MapService)
    
    value = clsProxy.getAll()
    assert value == {'aaa': 'bbb'}
    
    try:
        value = clsProxy.fooBar()
    except Exception:
        pass
    else:
        assert 'expected an exception' == 0
    
    print('test passed')
    