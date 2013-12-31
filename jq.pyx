from contextlib import contextmanager
import io
import sys


cdef extern from "jv.h":
    ctypedef struct jv:
        pass
    const char* jv_string_value(jv)

    ctypedef enum jv_kind:
      JV_KIND_INVALID,
      JV_KIND_NULL,
      JV_KIND_FALSE,
      JV_KIND_TRUE,
      JV_KIND_NUMBER,
      JV_KIND_STRING,
      JV_KIND_ARRAY,
      JV_KIND_OBJECT


    jv jv_dump_string(jv, int flags)
    jv_kind jv_get_kind(jv)
    cdef int jv_is_valid(jv x):
        return jv_get_kind(x) != JV_KIND_INVALID
    void jv_free(jv)

    jv jv_null()
    jv jv_bool(int)

    jv jv_number(double)
    double jv_number_value(jv)
    bint jv_is_integer(jv)

    jv jv_array_sized(int)
    int jv_array_length(jv)
    jv jv_array_get(jv, int)
    jv jv_array_set(jv, int, jv)

    jv jv_string_sized(const char*, int)

    jv jv_object()
    jv jv_object_get(jv object, jv key)
    jv jv_object_set(jv object, jv key, jv value)

    int jv_object_iter(jv)
    int jv_object_iter_next(jv, int)
    int jv_object_iter_valid(jv, int)
    jv jv_object_iter_key(jv, int)
    jv jv_object_iter_value(jv, int)


cdef extern from "jq.h":
    ctypedef struct jq_state:
        pass

    ctypedef void (*jq_err_cb)(void *, jv)

    jq_state *jq_init()
        #        raise JqCompileError(msg)
    void jq_teardown(jq_state **)
    bint jq_compile(jq_state *, const char* str)
    void jq_start(jq_state *, jv value, int flags)
    jv jq_next(jq_state *)
    void jq_set_error_cb(jq_state *, jq_err_cb, void *)


class JqError(Exception): pass
class JqInitError(JqError): pass
class JqCompileError(ValueError, JqError): pass
class JqUnsupportedTypeError(TypeError, JqError): pass


@contextmanager
def capture_stderr(ioobj):
    orig_stderr, sys.stderr = sys.stderr, ioobj
    try:
        yield
    finally:
        sys.stderr = orig_stderr

def compile(script):
    script = script.encode('utf-8')
    state = _State()
    state.compile(script)
    return state


cdef void _State_error_cb(void* x, jv err):
    _State._error_cb(<object>x, err)


cdef class _State:
    cdef object _errors
    cdef jq_state* _jq

    def __init__(self, const char* script):
        self._errors = []
        self._jq = jq_init()
        if not self._jq:
            raise JqInitError('Failed to initialize jq')
        jq_set_error_cb(self._jq, _State_error_cb, <void*>self)

        if not jq_compile(self._jq, script):
            raise JqCompileError("\n".join(self._errors))

    def p(self, obj):
        return self._process(self.pyobj_to_jv(obj))

    cdef _process(self, jv value):
        cdef int jq_flags = 0
        jq_start(self._jq, value, jq_flags);
        cdef jv result
        cdef int dumpopts = 0
        cdef jv dumped

        cdef list output = []

        while True:
            result = jq_next(self._jq)
            if not jv_is_valid(result):
                jv_free(result)
                break
            else:
                output.append(self.jv_to_pyobj(result))
        return output

    cdef object jv_to_pyobj(self, jv jval):
        cdef jv_kind kind = jv_get_kind(jval)
        cdef int it

        if kind == JV_KIND_NULL:
            return None
        elif kind == JV_KIND_FALSE:
            return False
        elif kind == JV_KIND_TRUE:
            return True
        elif kind == JV_KIND_NUMBER:
            v = jv_number_value(jval)
            if jv_is_integer(jval):
                return int(v)
            return v
        elif kind == JV_KIND_STRING:
            return jv_string_value(jval).decode('utf-8')
        elif kind == JV_KIND_ARRAY:
            [jv_array_get(jval, i) for i in range(jv_array_length(jval))]
        elif kind == JV_KIND_OBJECT:
            adict = {}
            it = jv_object_iter(jval)
            while jv_object_iter_valid(jval, it):
                k = self.jv_to_pyobj(jv_object_iter_key(jval, it))
                v = self.jv_to_pyobj(jv_object_iter_value(jval, it))
                adict[k] = v
                it = jv_object_iter_next(jval, it)
            return adict

    cdef jv pyobj_to_jv(self, object pyobj):
        cdef jv jval
        if isinstance(pyobj, str):
            pyobj = pyobj.encode('utf-8')
            return jv_string_sized(pyobj, len(pyobj))
        elif isinstance(pyobj, bool):
            return jv_bool(pyobj)
        elif isinstance(pyobj, (int, long, float)):
            return jv_number(pyobj)
        elif isinstance(pyobj, (list, tuple)):
            jval = jv_array_sized(len(pyobj))
            for i in range(len(pyobj)):
                jv_array_set(jval, i, self.pyobj_to_jv(pyobj))
            return jval
        elif isinstance(pyobj, dict):
            jval = jv_object()
            for key, value in pyobj.items():
                jv_object_set(jval, self.pyobj_to_jv(key), self.pyobj_to_jv(value))
            return jval
        elif pyobj is None:
            return jv_null()
        else:
            raise JqUnsupportedTypeError("{!r} object could not be converted to json".format(type(pyobj)))


    cdef _error_cb(self, jv err):
        self._errors.append(jv_string_value(err).decode('utf-8'))


#def jq(object program):
#    cdef object program_bytes_obj = program.encode("utf8")
#    cdef char* program_bytes = program_bytes_obj
#    cdef jq_state *jq = jq_init()
#    if not jq:
#        raise Exception("jq_init failed")
#
#    # TODO: jq_compile prints error to stderr
#    cdef int compiled = jq_compile(jq, program_bytes)
#
#    if not compiled:
#        raise ValueError("program was not valid")
#
#    cdef _Program wrapped_program = _Program.__new__(_Program)
#    wrapped_program._jq = jq
#    return wrapped_program
#
#
#cdef class _Program(object):
#    cdef jq_state* _jqfairydangsing
#
#    def __dealloc__(self):
#        jq_teardown(&self._jq)

    #def transform(self, input, raw_input=False, raw_output=False, multiple_output=False):
    #    string_input = input if raw_input else json.dumps(input)
    #    bytes_input = string_input.encode("utf8")
    #    result_bytes = self._string_to_strings(bytes_input)
    #    result_strings = map(lambda s: s.decode("utf8"), result_bytes)
    #    if raw_output:
    #        return "\n".join(result_strings)
    #    elif multiple_output:
    #        return [json.loads(s) for s in result_strings]
    #    else:
    #        return json.loads(next(iter(result_strings)))


    #cdef object _string_to_strings(self, char* input):
    #    cdef jv_parser* parser = jv_parser_new()
    #    jv_parser_set_buf(parser, input, len(input), 0)
    #    cdef jv value
    #    results = []
    #    while True:
    #        value = jv_parser_next(parser)
    #        if jv_is_valid(value):
    #            self._process(value, results)
    #        else:
    #            break

    #    jv_parser_free(parser)

    #    return results


    #cdef void _process(self, jv value, object output):
    #    cdef int jq_flags = 0

    #    jq_start(self._jq, value, jq_flags);
    #    cdef jv result
    #    cdef int dumpopts = 0
    #    cdef jv dumped

    #    while True:
    #        result = jq_next(self._jq)
    #        if not jv_is_valid(result):
    #            jv_free(result)
    #            return
    #        else:
    #            dumped = jv_dump_string(result, dumpopts)
    #            output.append(jv_string_value(dumped))
    #            jv_free(dumped)
