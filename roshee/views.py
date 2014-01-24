from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from roshee.forms import DealForm, MessageForm
from roshee.models import Deal, DealMessage


def new_deal(request):
    if request.method == 'POST':  # If the form has been submitted...
        # ContactForm was defined in the the previous section
        form = DealForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            print form.cleaned_data
            new_deal = Deal(name=form.cleaned_data['name'],
                            description=form.cleaned_data['description'],
                            owner=request.user)
            new_deal.save()
            return HttpResponseRedirect('/')  # Redirect after POST
    else:
        form = DealForm()  # An unbound form

    return render(request, 'form.html', {
        'form': form,
    })


def new_message(request, id):
    if request.method == 'POST':  # If the form has been submitted...
        # ContactForm was defined in the the previous section
        form = MessageForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            print form.cleaned_data
            msg = DealMessage(message=form.cleaned_data['message'],
                            deal_id=id,
                            user=request.user)
            msg.save()
        return HttpResponseRedirect('/deal/' + id)
    return HttpResponseNotFound('<h1>Page not found</h1>')



def edit_deal(request, id=0):
    deal = Deal.objects.get(id=id)
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            form.save()

    deal = Deal.objects.get(id=id)
    messages = DealMessage.objects.filter(deal_id=id)
    form = DealForm(instance=deal)  # An unbound form
    message_form = MessageForm()
    return render(request, 'main/edit.html', {
        'deal': deal,
        'messages': messages,
        'deal_form': form,
        'deal_form_target': '/deal/' + id,
        'message_form': message_form,
        'message_form_target': '/deal/' + id + '/message/'
    })


def delete_deal(request, id=0):
    deal = Deal.objects.get(id=id)
    deal.delete()
    return HttpResponseRedirect('/')

@login_required
def deal_list(request):
    deals = Deal.objects.filter(owner_id=request.user.id)\
        .values('id',
                'name',
                'description',
                'start_date').order_by('-start_date')
    return render(request, 'main/list.html', {
        'deal_list': deals,
    })
