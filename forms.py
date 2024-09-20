from flask_wtf import FlaskForm
from wtforms import SelectField,IntegerField,BooleanField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange,DataRequired


class AddEvaluatorForm(FlaskForm):
    """
    Drop down form field for choosing the ethereum address.
    SelectField specifies that this will be a drop down field.
    'Ethereum Address' is the label we'll give to this drop down field
    # A text input field for the form.
    """
    evaluatorAddress = SelectField("Evaluator's Address", 
                                   choices=[])
    attributeIndex= SelectField ('Attribute Id',
                                validators=[DataRequired()],
                                coerce=int,
                                choices=[0,1,2])

        

class EvaluateForm(FlaskForm):
    """
    Drop down form field for choosing the ethereum address.
    SelectField specifies that this will be a drop down field.
    'Ethereum Address' is the label we'll give to this drop down field
    # A text input field for the form.
    """
    dataset_id=IntegerField ('Dataset Id',[InputRequired(),NumberRange(min=0, message='Must enter a number greater than 0')])
    attribute_id= SelectField ('Attribute Id',validators=[DataRequired()],
                                coerce=int,
                                choices=[0,1,2])
    score=IntegerField ('Score', validators=[InputRequired(),NumberRange(min=0, max=100,message='Must enter a number greater than 0 and smaller than 100')])


class FileForm(FlaskForm):
    """User File Form."""
    file =  FileField('File',validators=[FileRequired()])





