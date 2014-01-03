# coding=utf8
import unittest
from jq import jq


class TestJqBackwardCompatibility(unittest.TestCase):
    def test_output_of_dot_operator_is_input(self):
        self.assertEqual(
            "42",
            jq(".").transform("42")
        )

    def test_can_add_one_to_each_element_of_an_array(self):
        self.assertEqual(
            [2, 3, 4],
            jq("[.[]+1]").transform([1, 2, 3])
        )


    def test_input_string_is_parsed_to_json_if_raw_input_is_true(self):
        self.assertEqual(
            42,
            jq(".").transform("42", raw_input=True)
        )


    def test_output_is_serialised_to_json_string_if_raw_output_is_true(self):
        self.assertEqual(
            '"42"',
            jq(".").transform("42", raw_output=True)
        )


    def test_elements_in_raw_output_are_separated_by_newlines(self):
        self.assertEqual(
            "1\n2\n3",
            jq(".[]").transform([1, 2, 3], raw_output=True)
        )


    def test_first_output_element_is_returned_if_multiple_output_is_false_but_there_are_multiple_output_elements(self):
        self.assertEqual(
            2,
            jq(".[]+1").transform([1, 2, 3])
        )


    def test_multiple_output_elements_are_returned_if_multiple_output_is_true(self):
        self.assertEqual(
            [2, 3, 4],
            jq(".[]+1").transform([1, 2, 3], multiple_output=True)
        )


    def test_multiple_inputs_in_raw_input_are_separated_by_newlines(self):
        self.assertEqual(
            [2, 3, 4],
            jq(".+1").transform("1\n2\n3", raw_input=True, multiple_output=True)
        )


    def test_value_error_is_raised_if_program_is_invalid(self):
        with self.assertRaises(ValueError):
            jq("!")


    def test_unicode_strings_can_be_used_as_input(self):
        self.assertEqual(
            u"‽",
            jq(".").transform(u'"‽"', raw_input=True)
        )


    def test_unicode_strings_can_be_used_as_programs(self):
        self.assertEqual(
            u"Dragon‽",
            jq(u'.+"‽"').transform(u'"Dragon"', raw_input=True)
        )

if __name__ == '__main__':
    unittest.main()

