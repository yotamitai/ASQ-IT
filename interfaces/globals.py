from backend.forms.common import CONSTRAINTS
from backend.forms.forgger_forms import FroggerQueryForm
from backend.forms.highway_forms import HighwayQueryForm
from backend.forms.highway_forms_speed import HighwayQueryFormSpeed
from interfaces.Frogger.frogger_interface import frogger_data2query, AP_Frogger, \
    frogger_ltlf_params
from interfaces.Highway.highway_interface import highway_data2query, AP_Highway, \
    highway_ltlf_params

DATA2QERY = {
    "highway": highway_data2query,
    "frogger": frogger_data2query
}
AP = {
    "highway": AP_Highway,
    "frogger": AP_Frogger
}
CONSTRAINTS = {
    "highway": CONSTRAINTS[1:],
    "frogger": CONSTRAINTS[-1]
}
FORMS = {
    # "highway": HighwayQueryForm,
    "highway": HighwayQueryFormSpeed, #TODO added for speed
    "frogger": FroggerQueryForm
}
LTLF = {
    "highway": highway_ltlf_params,
    "frogger": frogger_ltlf_params
}
