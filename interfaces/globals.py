from backend.forms.common import CONSTRAINTS
from backend.forms.highway_forms import HighwayQueryForm
from backend.forms.highway_forms_speed import HighwayQueryFormSpeed
from interfaces.Highway.highway_interface import highway_data2query, AP_Highway, \
    highway_ltlf_params

DATA2QERY = {
    "highway": highway_data2query,
}
AP = {
    "highway": AP_Highway,
}
CONSTRAINTS = {
    "highway": CONSTRAINTS[1:],
}
FORMS = {
    # "highway": HighwayQueryForm,
    "highway": HighwayQueryFormSpeed, #TODO added for speed
}
LTLF = {
    "highway": highway_ltlf_params,
}
