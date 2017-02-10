#!/usr/bin/env python


import confu
parser = confu.standard_parser("FXdiv configuration script")


def main(args):
    options = parser.parse_args(args)
    build = confu.Build.from_options(options)

    build.export_cpath("include", ["fxdiv.h"])

    with build.options(source_dir="test", deps=[build.deps.googletest]):
        build.unittest("MultiplyHighTest", build.cxx("MultiplyHigh.cc"))
        build.unittest("QuotientTest", build.cxx("Quotient.cc"))

    return build


if __name__ == "__main__":
    import sys
    main(sys.argv[1:]).generate()
