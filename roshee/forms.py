from django import forms
from roshee.models import Deal, Attachment
from django.forms import ModelForm
from crispy_forms.helper import FormHelper, Layout
from crispy_forms import layout
from django.forms.formsets import formset_factory
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

BUYER_SELLER = ((True, 'Buyer'), (False, 'Seller'))

class DealForm(ModelForm):
    # vendor_email = forms.EmailField(label='Vendor email')
    name = forms.CharField(label='Deal Name',
                           max_length=30)
    user_is_buyer = forms.ChoiceField(label='I am a:', widget=forms.RadioSelect,
                                      choices=BUYER_SELLER, initial=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':40}),
                                  max_length=200, required=False)
    class Meta:
        model = Deal
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            layout.Div(
                'name',
                'user_is_buyer',
                layout.HTML('<h5>Invite Others</br>'
                            '<span class="small">Enter their email addresses below</span></h5>'),
                layout.Div(css_id='forms'),
                layout.Div(
                layout.HTML(html='<br/>'
                            '<button class="btn btn-primary" type="button" '
                            'id="generate_forms" >Add Buyer/Vendor</button>'
                            '<br/><br/>'),
                css_class='row'),
                'description',
                css_id='main_form'
            ))

class EditDealForm(ModelForm):
    name = forms.CharField(label='Deal Name', max_length=30)
    class Meta:
        model = Deal
        fields = ['name', 'description']
        
class CounterpartyForm(forms.Form):
    party_email = forms.EmailField(label='Vendor email',
                                   required=False)
    is_buyer = forms.ChoiceField(label='', widget=forms.RadioSelect,
                                 choices=BUYER_SELLER,
                                 initial=True)

    def __init__(self, *args, **kwargs):
        super(CounterpartyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(layout.Div(
               layout.Div('party_email',
                          css_class='col-md-8'),
               layout.Div(layout.Field('is_buyer',
                                       css_class='radio-inline'),
                          css_class='col-md-4'),
               css_class='row'))

class CounterpartyFormSetHelper(FormHelper):
      def __init__(self, *args, **kwargs):
        super(CounterpartyFormSetHelper, self).__init__(*args, **kwargs)
        
CounterpartyFormSet = formset_factory(CounterpartyForm)

class AttachmentForm(forms.Form):
    data = forms.FileField(label='')

class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=200)

class InviteForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea,
                              required=False,
                              max_length=1000)
    


from userena.forms import SignupFormOnlyEmail

class SignupFormExtra(SignupFormOnlyEmail):
    """
    A form to demonstrate how to add extra fields to the signup form, in this
    case adding the first and last name.


    """
    first_name = forms.CharField(label='First name',
                                 max_length=30,
                                 required=False)

    last_name = forms.CharField(label='Last name',
                                max_length=30,
                                required=False)

    company = forms.CharField(label='Company name',
                              max_length=200)

    def __init__(self, *args, **kw):
        """

        A bit of hackery to get the first name and last name at the top of the
        form instead at the end.

        """
        super(SignupFormExtra, self).__init__(*args, **kw)
        # Put the first and last name at the top
        self.helper = FormHelper()
        self.helper.form_tag = False
        new_order = self.fields.keyOrder[:-2]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
        new_order.insert(2, 'company')
        self.fields.keyOrder = new_order

    def save(self):
        """
        Override the save method to save the first and last name to the user
        field.

        """
        # First save the parent form and get the user.
        new_user = super(SignupFormExtra, self).save()

        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.company = self.cleaned_data['company']
        new_user.save()
        
        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user

from userena.forms import EditProfileForm
from accounts.models import UserProfile

class EditProfileFormExtra(EditProfileForm):
    class Meta:
        model = UserProfile
        exclude = ['mugshot', 'privacy', 'user']

