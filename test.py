import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from colorops import RGBColor, YUVColor


def load_tests(loader, tests, ignore):
    # Used on Python 2.7+
    import colorops
    import doctest
    tests.addTests(doctest.DocTestSuite(colorops))
    return tests


class TestRGBColor(unittest.TestCase):
    def testCreation(self):
        self.assertEqual(str(RGBColor('#123')), '112233')
        self.assertEqual(str(RGBColor('#123456')), '123456')
        self.assertEqual(str(RGBColor(0x123456)), '123456')
        self.assertEqual(str(RGBColor((0x12, 0x34, 0x56))), '123456')   
        self.assertEqual(str(RGBColor('rgb(0, 127, 255)')), '007FFF')     
        self.assertEqual(str(RGBColor('rgb(0%, 50%, 100%)')), '007FFF')     
        
        self.assertRaises(ValueError, lambda: RGBColor({}))


if __name__ == '__main__':
    unittest.main()
