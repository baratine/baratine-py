baratine-py
============================

This is a Python client for `Baratine <http://baratine.io/>`_.

::

  import baratine

  # Python interface for your Baratine service
  class CounterService:
      def addAndGet(value):
          pass
      def incrementAndGet():
          pass
      def get():
          pass

  client = baratine.BaratineClient('http://127.0.0.1:8085/s/pod')
  
  # create a proxy for the remote service
  counter = client._lookup('/counter/123')._as(CounterService)
  
  # now call your service using your API
  # the library supports all the good python features like default args and named args
  result = counter.addAndGet(2222)
  
  print(result)
