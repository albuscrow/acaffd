import sys
if len(sys.argv) == 1:
    IS_FAST_MODE = True
elif sys.argv[1] == 'fast':
    IS_FAST_MODE = True
elif sys.argv[1] == 'normal':
    IS_FAST_MODE = False
IS_TESS_MODE = False
IF = '//?!if'
TIME = 'time'
TESS = 'tess'
ELSE = '//?!else'
ENDIF = '//?!end'
ELSE_TIME = '//?!else_time'
ELSE_TESS = '//?!else_tess'
NORMAL = ''

IS_UNIFORM_ADAPTIVE_TESSELLATION_FACTOR = True
