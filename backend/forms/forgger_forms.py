from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError

from backend.forms.common import CONSTRAINTS

ELEMENTS = [(None, '----'), ('clear', 'Clear'), ('water', 'Water'),
            ('car', 'Car'), ('log', 'Log')]  # ('boundary', 'Boundary')
# ON = [(None, '----'), ('grass', 'Grass'), ('road', 'Road'), ('log', 'Log')]
AREAS = [(None, '----'),
         ('beforeroad', 'Before road'),
         ('onroad', 'On road'),
         # ('afterroad', 'After road'),
         # ('beforeriver', 'Before river'),
         ('onriver', 'On river')
         ]
LILYPAD = [('lilypad', 'Lilypad')]
TERMINAL = [(None, '----'), ('win', 'Win'), ('drown', 'Drown'), ('runover', 'Run over'),
            ('timeout', 'Timeout')]
DIRECTIONS = [(None, '----'), ('on', 'On'), ('above', 'Above'), ('below', 'Below'),
              ('left', 'Left'), ('right', 'Right')]
OCCURS = [(None, '----'), ('occurs', 'Occurs'), ('notoccurs', "Doesn't Occur")]
AREA_CONSTRAINTS = [(None, '----'), ('changes', 'Changes'), ('staysconstant', "Stays constant")]
# SIDE = [(None, '----'), ('left', 'Left'), ('right', 'Right'), ('middle', 'Middle')]
# AREAS = [(None, '----'),
#          ('atstartlocation', 'At start location'),
#          ('atroadstart', 'At road start'),
#          ('afterroadstart', 'After road start'),
#          ('atroadend_riverstart', 'At road end-river start'),
#          ('afterroadend', 'After road end'),
#          ('beforeriverstart', 'Before river start'),
#          ('afterriverstart', 'After river start')
#          ]


# Constraints = CONSTRAINTS[0] + CONSTRAINTS[-1]

area_dict = {
    'beforeroad': {"up": ["clear", "car"], "down": [], "left": ["clear"],
                   "right": ["clear"]},
    'onroad': {"up": ["clear", "car", "water", "log"], "down": ["clear", "car"],
               "left": ["clear", "car"],
               "right": ["clear", "car"]},
    # 'afterroad': {"up": ["clear", "car"], "down": [],
    #                    "left": ["clear"], "right": ["clear"]},
    # 'beforeriver': {"up": ["clear", "car"], "down": [], "left": ["clear"],
    #                      "right": ["clear"]},
    'onriver': {"up": ["log", "water", "lilypad"], "down": ["clear", "water", "log"],
                "left": ["log", "water"],
                "right": ["log", "water"]},
}
position_dict = {
    'up': {"car": {"down": ["water", "log"], "left": ["water", "log"], "right": ["water", "log"]},
           "water": {"down": [], "left": ["car"], "right": ["car"]},
           "log": {"down": [], "left": ["car"], "right": ["car"]},
           "lilypad": {"down": [], "left": ["car", "clear"], "right": ["car", "clear"]}
           },
    'down': {"car": {"up": ["lilypad"], "left": ["water", "log"], "right": ["water", "log"]},
             "water": {"up": ["car", "clear"], "left": ["car", "clear"],
                       "right": ["car", "clear"]},
             "log": {"up": ["car", "clear"], "left": ["car", "clear"], "right": ["car", "clear"]}
             },
    'left': {"car": {"up": ["lilypad", "log", "water"], "down": ["log", "water"],
                     "right": ["log", "water"]},
             "water": {"up": ["car", "clear"], "down": ["car"], "right": ["car", "clear"]},
             "log": {"up": ["car", "clear"], "down": ["car"], "right": ["car", "clear"]}
             },
    'right': {"car": {"up": ["lilypad", "log", "water"], "left": ["log", "water"],
                      "down": ["log", "water"]},
              "water": {"up": ["car", "clear"], "left": ["car", "clear"], "down": ["car"]},
              "log": {"up": ["car", "clear"], "left": ["car", "clear"], "down": ["car"]}
              },
}
terminal_dict = {
    'win': {"up": ["water", "log", "lilypad"], "down": ["water", "log", "car", "clear"],
            "left": ["water", "log", "car"],
            "right": ["water", "log", "car"]},
    'drown': {"up": ["clear", "car"], "down": ["car"], "left": ["car", "clear"],
              "right": ["car", "clear"]},
    'runover': {"up": ["water", "log", "lilypad"], "down": ["water", "log"],
                "left": ["water", "log"],
                "right": ["water", "log"]},
}

class ConstraintValidator(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        if field.data != "None":

            if form.data['start_area'] == "None":
                raise ValidationError(f'Start area must be selected')
            elif field.data == "constant" and (form.data['end_area'] not in [form.data['start_area'], 'None']):
                raise ValidationError(f'End area selection not compatible with constraint chosen.')

class PositionValidator(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        if field.data != "None":

            state, position = field.name.split('_')
            area = '_'.join([state, 'area'])
            # if positions are not relevant terminal
            if field.name == "end_terminal":
                if field.data != "timeout":
                    for direction, element in terminal_dict[field.data].items():
                        if form.data['_'.join([state, direction])] in element:
                            raise ValidationError(
                                f'Terminal state {field.data.upper()} is not possible with {direction.upper()} specification.')

            # if positions are not in area specified
            elif form.data[area] != "None":
                if field.data not in area_dict[form.data[area]][position]:
                    raise ValidationError(f'Selection not possible in chosen Area')

            # if positions are not relevant to each other
            elif field.data in position_dict[position].keys():
                for direction, element in position_dict[position][field.data].items():
                    if form.data['_'.join([state, direction])] in element:
                        raise ValidationError(
                            f'{position.upper()} & {direction.upper()} positions not possible.')


class FroggerQueryForm(FlaskForm):

    # Start
    start_area = SelectField(u'Area:', choices=AREAS)
    start_left = SelectField(u'L:', [PositionValidator()], choices=ELEMENTS)
    start_right = SelectField(u'R:', [PositionValidator()], choices=ELEMENTS)
    start_up = SelectField(u'U:', [PositionValidator()], choices=ELEMENTS + LILYPAD)
    start_down = SelectField(u'D:', [PositionValidator()], choices=ELEMENTS)
    # End
    end_area = SelectField(u'Area:', choices=AREAS)
    end_left = SelectField(u'L:', [PositionValidator()], choices=ELEMENTS)
    end_right = SelectField(u'R:', [PositionValidator()], choices=ELEMENTS)
    end_up = SelectField(u'U:', [PositionValidator()], choices=ELEMENTS + LILYPAD)
    end_down = SelectField(u'D:', [PositionValidator()], choices=ELEMENTS)
    end_terminal = SelectField(u'Terminal state:', [PositionValidator()], choices=TERMINAL)
    # Action Constraints
    act_left = SelectField(u'L:', choices=OCCURS)
    act_right = SelectField(u'R:', choices=OCCURS)
    act_up = SelectField(u'U:', choices=OCCURS)
    act_down = SelectField(u'D:', choices=OCCURS)
    # Area Constraints
    area_constraint = SelectField(u'', [ConstraintValidator()], choices=AREA_CONSTRAINTS)
    # padding
    pre_padding = BooleanField('Add Padding Before')

    submit = SubmitField('Submit')
