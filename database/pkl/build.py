#!/usr/bin/env python3

import sys
import pklmaster
import pivot_hard
import hw_sum

def build_main():
    pklmaster.master2pkl()
    pivot_hard.pivot_hard_weekly()
#    hw_sum.hw_sum_main()

if __name__ == "__main__":
    build_main()
    sys.exit(0)
