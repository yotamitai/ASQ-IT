from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError

CONSTRAINTS = [(None, '----'), ('staysconstant', 'Stays constant'), ('changes', 'Changes'),
               ('changesinto', 'Changes into')]

# class User_ID(object):
#     def __init__(self):
#         pass
#
#     def __call__(self, form, field):
#         if not field.data:
#             raise ValidationError(f'Must insert user ID')


class LoadMoreForm(FlaskForm):
    submit = SubmitField('Load More Videos')


class BackButtonForm(FlaskForm):
    submit = SubmitField('Load Previous Video')

# class LoadMoreForm_WithID(FlaskForm):
#     user_id = StringField('User ID:', [User_ID()])
#     submit = SubmitField('Load More Videos')
#
class check_ID(FlaskForm):
    submit = SubmitField('Done')
