# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# ====== PREREQUISITE ======
# install antlr4-tools locally with:
# > pip install antlr4-tools

#!/bin/bash

FILE="endanswer"
antlr4 $FILE.g4 -visitor -no-listener

# for debugging locally
# antlr4-parse $FILE.g4 $FILE -gui test.txt -tokens

# Not used anymore
# antlr4 -Dlanguage=Python3 -visitor $FILE.g4