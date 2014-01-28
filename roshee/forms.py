from django import forms
from roshee.models import Deal, Attachment
from django.forms import ModelForm

class DealForm(ModelForm):
    vendor_email = forms.EmailField(label='Vendor email')
    BUYER_SELLER = ((True, 'Buyer'), (False, 'Seller'))
    buyer = forms.ChoiceField(label='',widget=forms.RadioSelect, choices=BUYER_SELLER, initial=True)
    description = forms.CharField(widget=forms.Textarea,max_length=200)
    
    class Meta:
        model = Deal
        fields=['name']

class EditDealForm(ModelForm):
    class Meta:
        model = Deal
        fields=['name','description']

class AttachmentForm(forms.Form):
    data = forms.FileField(label='')

class MessageForm(forms.Form):
    message = forms.CharField(max_length=200)

class InviteForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea,required=False, max_length=1000)
    


from userena.forms import SignupForm

class SignupFormExtra(SignupForm):
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

    def __init__(self, *args, **kw):
        """

        A bit of hackery to get the first name and last name at the top of the
        form instead at the end.

        """
        super(SignupFormExtra, self).__init__(*args, **kw)
        # Put the first and last name at the top
        new_order = self.fields.keyOrder[:-2]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
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
        new_user.save()
        
        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user