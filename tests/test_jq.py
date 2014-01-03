# coding=utf8
import unittest
import re
import jq


class TestJq(unittest.TestCase):
    def test_compile_dot(self):
        s = jq.compile('.')
        self.assertIsInstance(s, jq._Jq)

    def test_syntax_error(self):
        expected_message = re.escape('''\
error: syntax error, unexpected '*', expecting $end
**
1 compile error''')

        with self.assertRaisesRegex(ValueError, expected_message):
            s = jq.compile('**')

    def test_conversion_between_python_object_and_jv(self):
        objects = [
            None,
            False,
            True,
            1,
            1.5,
            "string",
            [None, False, True, 1, 1.5, [None, False, True], {'foo': 'bar'}],
            {
                'key1': None,
                'key2': False,
                'key3': True,
                'key4': 1,
                'key5': 1.5,
                'key6': [None, False, True, 1, 1.5, [None, False, True], {'foo': 'bar'}],
            },
        ]

        for obj in objects:
            s = jq.compile('.')
            self.assertEqual([obj], s.apply(obj))


    def test_assigning_values(self):
        self.assertEqual(jq.one('$foo', {}, foo='bar'), 'bar')
        self.assertEqual(jq.one('$foo', {}, foo=['bar']), ['bar'])


    def test_apply(self):
        self.assertEqual(jq.apply('. + $foo', 'val', foo='bar'), ['valbar'])

    def test_first(self):
        self.assertEqual(jq.first('. + $foo + "1", . + $foo + "2"', 'val', foo='bar'), 'valbar1')

    def test_one(self):
        self.assertEqual(jq.one('. + $foo', 'val', foo='bar'), 'valbar')

        # raise IndexError if there are multiple elements
        with self.assertRaises(IndexError):
            jq.one('. + $foo, . + $foo', 'val', foo='bar')
