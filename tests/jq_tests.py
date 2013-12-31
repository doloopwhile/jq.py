# coding=utf8
import jq

def test_compile_dot():
    s = jq.compile('.')
    assert isinstance(s, jq._State)


def test_syntax_error():
    try:
        s = jq.compile('**')
    except jq.JqCompileError as err:
        expected_message = '''\
error: syntax error, unexpected '*', expecting $end
**
1 compile error'''

        assert str(err) == expected_message
    else:
        assert False, "exception not raised"
