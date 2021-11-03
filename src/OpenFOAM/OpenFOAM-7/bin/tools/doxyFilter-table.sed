#------------------------------------------------------------------------------
# Script
#     doxyFilter-table.sed
#
# Description
#     Splice lines in tables separated by the \\\n continuation tag
#------------------------------------------------------------------------------

/\\\\/{
N
s/\\\\\n */ /
}


#------------------------------------------------------------------------------
