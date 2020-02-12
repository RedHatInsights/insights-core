from insights import rule, make_pass
from insights.core.filters import add_filter
from insights.parsers.ps import PsAux, PsAuxww, PsAlxwww
from insights.specs import Specs


@rule(PsAux)
def psaux_no_filter(ps_aux):
    return make_pass("FAKE RESULT")


add_filter(Specs.ps_auxww, "fake-filter")


@rule(PsAuxww)
def psauxww_ds_filter(ps_auxww):
    return make_pass("FAKE RESULT")


add_filter(PsAlxwww, "fake-filter")


@rule(PsAlxwww)
def psalxwww_parser_filter(ps_alxwww):
    return make_pass("FAKE RESULT")
