#!/usr/bin/python
# -*- coding: utf-8 -*-
# François-Xavier Bourlet <fx@dotcloud.com>, May 2011.

import pstats
import sys

print '++++++++++++++++++++++++++++++', "calls count"
pstats.Stats(sys.argv[1]).strip_dirs().sort_stats('calls').print_stats(10)
print '------------------------------', "internal time"
pstats.Stats(sys.argv[1]).strip_dirs().sort_stats('time').print_stats(10)
print '------------------------------', "cumulative"
pstats.Stats(sys.argv[1]).strip_dirs().sort_stats('cumulative').print_stats(10)
