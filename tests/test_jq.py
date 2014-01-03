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

        s = jq.compile('.')
        for obj in objects:
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




class TestJqBackwardCompatibility(unittest.TestCase):
    def setUp(self):
        self.jq = jq.jq

    def test_output_of_dot_operator_is_input(self):
        self.assertEqual(
            "42",
            self.jq(".").transform("42")
        )

    def test_can_add_one_to_each_element_of_an_array(self):
        self.assertEqual(
            [2, 3, 4],
            self.jq("[.[]+1]").transform([1, 2, 3])
        )


    def test_input_string_is_parsed_to_json_if_raw_input_is_true(self):
        self.assertEqual(
            42,
            self.jq(".").transform("42", raw_input=True)
        )


    def test_output_is_serialised_to_json_string_if_raw_output_is_true(self):
        self.assertEqual(
            '"42"',
            self.jq(".").transform("42", raw_output=True)
        )


    def test_elements_in_raw_output_are_separated_by_newlines(self):
        self.assertEqual(
            "1\n2\n3",
            self.jq(".[]").transform([1, 2, 3], raw_output=True)
        )


    def test_first_output_element_is_returned_if_multiple_output_is_false_but_there_are_multiple_output_elements(self):
        self.assertEqual(
            2,
            self.jq(".[]+1").transform([1, 2, 3])
        )


    def test_multiple_output_elements_are_returned_if_multiple_output_is_true(self):
        self.assertEqual(
            [2, 3, 4],
            self.jq(".[]+1").transform([1, 2, 3], multiple_output=True)
        )


    def test_multiple_inputs_in_raw_input_are_separated_by_newlines(self):
        self.assertEqual(
            [2, 3, 4],
            self.jq(".+1").transform("1\n2\n3", raw_input=True, multiple_output=True)
        )


    def test_value_error_is_raised_if_program_is_invalid(self):
        with self.assertRaises(ValueError):
            self.jq("!")


    def test_unicode_strings_can_be_used_as_input(self):
        self.assertEqual(
            u"‽",
            self.jq(".").transform(u'"‽"', raw_input=True)
        )


    def test_unicode_strings_can_be_used_as_programs(self):
        self.assertEqual(
            u"Dragon‽",
            self.jq(u'.+"‽"').transform(u'"Dragon"', raw_input=True)
        )

