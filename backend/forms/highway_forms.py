from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import ValidationError

from backend.forms.common import CONSTRAINTS

HW_POSITIONS = [(None, '----'), ('behind', 'Behind'), ('infrontof', 'In front of'),
                ('above', 'Above'), ('below', 'Below')]
HW_COLLISION = [('collision', 'Collision')]
HW_LANES = [(None, '----'), ('lane1', 'Lane 1'), ('lane2', 'Lane 2'),
            ('lane3', 'Lane 3'), ('lane4', 'Lane 4')]

HW_PREDICATES = HW_POSITIONS + HW_LANES[1:] + HW_COLLISION


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
                    raise ValidationError(f'Element 1 must be selected')

                elif field.data == "changesinto":
                    if form.data['constraint_s_e_p2'] == "None":
                        raise ValidationError(f'Element 2 must be selected to change into')

            else:  # constraint_s_e_p2
                if form.data["constraint_s_e"] != "changesinto":
                    raise ValidationError(
                        f'Only appropriate for the "Changes into" constraint')
                elif form.data["constraint_s_e_p1"] == "None":
                    raise ValidationError(f'Element 1 must be selected')
                else:
                    pred1 = form.data['constraint_s_e_p1']
                    for group in [HW_POSITIONS[1:] + HW_COLLISION, HW_LANES[1:]]:
                        vals = [x[0] for x in group]
                        if field.data in vals:
                            if pred1 not in vals:
                                raise ValidationError(f'Cannot change element 1 into element 2, '
                                                      f'must be of same type.')
                            elif pred1 == field.data:
                                raise ValidationError(
                                    f'Element 1 and element 2 cannot be identical.')


class HighwayQueryForm(FlaskForm):
    start_pos = SelectField(u'Position', choices=HW_POSITIONS)
    start_lane = SelectField(u'Lane', choices=HW_LANES)

    end_pos = SelectField(u'Position', choices=HW_POSITIONS + HW_COLLISION)
    end_lane = SelectField(u'Lane', choices=HW_LANES)

    constraint_s_e_p1 = SelectField(u'Element A', [Constraint()], choices=HW_PREDICATES[:-1])
    constraint_s_e = SelectField(u'Constraint', [Constraint()], choices=CONSTRAINTS)
    constraint_s_e_p2 = SelectField(u'Element B', [Constraint()],
                                    choices=HW_PREDICATES[:-1] + HW_COLLISION)

    submit = SubmitField('Submit')
