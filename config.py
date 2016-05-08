import sys
if len(sys.argv) == 1:
    IS_FAST_MODE = True
elif sys.argv[1] == 'fast':
    IS_FAST_MODE = True
elif sys.argv[1] == 'normal':
    IS_FAST_MODE = False
IF = '//?!iftime'
ELSE = '//?!else'
ENDIF = '//?!end'
NORMAL = ''