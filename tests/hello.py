import unittest

class TestHello(unittest.TestCase):
    def setUp(self):
        self.hello = 'hello'
        
    def test_hello(self):
        self.assertEqual(self.hello, 'hello')

if __name__ == '__main__':
    unittest.main()