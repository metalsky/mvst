#!/usr/bin/env python
import sys, os
import cPickle

sys.path.append("../update")
import mvlapt as apt

product_id = 2
merged_id = 471


u = apt.update(product_id)
u.pushToTesting(merged_id)
