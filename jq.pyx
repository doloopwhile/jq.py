

cdef extern from "jq.h":
    bytecode* jq_compile(const char* str)
    struct bytecode:
        pass

#cdef class _Program(object):
cdef class _Program:
    cdef bytecode* _bytecode

def compile(const char* str):
    #return _CompiledProgram.__new__(_CompiledProgram, (jq_compile(str)))

    cdef _Program program = _Program.__new__(_Program)
    program._bytecode = jq_compile(str)
    return program
