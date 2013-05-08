import python_lexer
import parser
import utils
import unittest
import logging
import re
import random


def setup_test(test, filename):
    f = open(filename)
    data = f.read()
    f.close()
    gl={}
    lc={}
    lexer = python_lexer.PythonLexer()
    lexer.input(data)
    res=parser.parse_data(data, lexer)
    code=utils.node_to_str(res)
    test.gl=gl
    test.lc=lc
    test.code=code
    

class SampleTest(unittest.TestCase):

    def test_sample1(self):
        setup_test(self, 'sample1.py')
        lc=self.lc
        exec(self.code,self.gl,self.lc)
        pokus=lc['Pokus']()
        a=lc['a']
        b=lc['b']
        mul=lc['mul']

        self.assertEqual(pokus.get_all(), (10,10,10))
        self.assertEqual(a, 'jozo')
        self.assertEqual(b, 23)
        self.assertEqual(mul(4)(5), 20)
        self.assertTrue(re.search('riadkov', pokus.__init__.__doc__))


    def test_sample2(self):
        setup_test(self, 'sample2.py')
        exec(self.code,globals(),self.lc)
        lc=self.lc
        dct=lc['get_dct']()
        self.assertEqual(dct[3],4)
        tpl=lc['get_tpl']()
        lst=lc['lst']
        slc=lc['slc']
        self.assertEqual(len(tpl),5)
        self.assertEqual(len(lst),5)
        self.assertEqual(len(slc),2)

    def test_sample3(self):
        setup_test(self, 'sample3.py')
        exec(self.code,globals(),self.lc)
        lc=self.lc
        inc=lc['inc']
        self.assertEqual(inc(3),4)
        self.assertIn('pokus', lc)
        self.assertEqual(lc['loop'](),10)
        self.assertLess(lc['cond'](),0.001)


if __name__ == '__main__':
    logger=logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    unittest.main()


#print(utils.node_to_tree(res))
#for tok in lexer:
#    print(tok.__str__())

#if __name__ == '__main__':
#    run_all=True
#    #run_all=False
#
#    if run_all:
#        logger=logging.getLogger('')
#        logger.setLevel(logging.DEBUG)
#        unittest.main()
#    else:
#        suite = unittest.TestSuite()
#        suite.addTest(TestWarnings('test_nonexistent_attribute'))
#        suite.addTest(TestScope('test_basic'))
#        suite.addTest(TestScope('test_parent'))
#        suite.addTest(TestScope('test_copy'))
#        unittest.TextTestRunner().run(suite)