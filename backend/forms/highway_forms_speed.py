from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import ValidationError

from backend.forms.common import CONSTRAINTS

HW_POSITIONS = [(None, '----'), ('behind', 'Behind'), ('infrontof', 'In front of'),
                ('above', 'Above'), ('below', 'Below')]
HW_COLLISION = [('collision', 'Collision')]
HW_LANES = [(None, '----'), ('lane1', 'Lane 1'), ('lane2', 'Lane 2'),
            ('lane3', 'Lane 3'), ('lane4', 'Lane 4')]
HW_SPEED = [(None, '----'),('slow', 'Slow'),('fast', 'Fast')] #TODO added for speed
HW_PREDICATES = HW_POSITIONS + HW_LANES[1:] + HW_SPEED[1:] + HW_COLLISION #TODO added for speed
HW_PREDICATES_NO_SPEED = HW_POSITIONS + HW_LANES[1:] + HW_COLLISION #TODO added for speed


class Constraint(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        if field.data != "None":
            if field.name == 'constraint_s_e_p1':
                if form.data['constraint_s_e'] == "None":
                    raise ValidationError(f'Constraint must be selected')

            elif field.name == 'constraint_s_e':
                if form.data['constraint_s_e_p1'] == "None":
                    raise ValidationError(f'Element A must be selected')

                elif field.data == "changesinto":
                    if form.data['constraint_s_e_p2'] == "None":
                        raise ValidationError(f'Element B must be selected to change into')

                elif field.data == "staysconstant":
                    for group in [HW_POSITIONS[1:] + HW_COLLISION, HW_LANES[1:], HW_SPEED]:
                        pred_names = [x[0] for x in group]
                        if form.data['constraint_s_e_p1'] in pred_names:
                            for choice in [form.data['start_lane'], form.data['start_pos'],
                                               form.data['start_speed']]:
                                if choice in pred_names and choice != form.data['constraint_s_e_p1']:
                                    raise ValidationError(
                                        f'Element A conflicts with the Start Frame description.')

            else:  # constraint_s_e_p2
                if form.data["constraint_s_e"] != "changesinto":
                    raise ValidationError(
                        f'Only appropriate for the "Changes into" constraint')
                elif form.data["constraint_s_e_p1"] == "None":
                    raise ValidationError(f'Element A must be selected')
                else:
                    pred1 = form.data['constraint_s_e_p1']
                    for group in [HW_POSITIONS[1:] + HW_COLLISION, HW_LANES[1:], HW_SPEED]:
                        vals = [x[0] for x in group]
                        if field.data in vals:
                            if pred1 not in vals:
                                raise ValidationError(f'Cannot change element A into element B, '
                                                      f'must be of same type.')
                            elif pred1 == field.data:
                                raise ValidationError(
                                    f'Element A and element B cannot be identical.')


class HighwayQueryFormSpeed(FlaskForm):
    start_pos = SelectField(u'Position', choices=HW_POSITIONS)
    start_lane = SelectField(u'Lane', choices=HW_LANES)
    start_speed = SelectField(u'Speed', choices=HW_SPEED, default="None") #TODO added for speed

    end_pos = SelectField(u'Position', choices=HW_POSITIONS + HW_COLLISION)
    end_lane = SelectField(u'Lane', choices=HW_LANES)
    end_speed = SelectField(u'Speed', choices=HW_SPEED, default="None")  # TODO added for speed

    constraint_s_e = SelectField(u'Constraint', [Constraint()], choices=CONSTRAINTS)
    constraint_s_e_p1 = SelectField(u'Element A', [Constraint()],
                                    choices=HW_PREDICATES_NO_SPEED[:-1])
    constraint_s_e_p2 = SelectField(u'Element B', [Constraint()],
                                    choices=HW_PREDICATES_NO_SPEED)
    pre_padding = BooleanField('Add 1 Second Before Start Frame')

    submit = SubmitField('Submit')
