from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from roshee.forms import *
from roshee.models import *
from django.views.decorators.http import *
from django.db.models import Q
from guardian.shortcuts import *
from django.core.mail import send_mail

def new_deal(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        counterparties = CounterpartyFormSet(request.POST)
        print counterparties.is_valid()
        print counterparties.errors
        if form.is_valid() and counterparties.is_valid():
            new_deal = Deal(name=form.cleaned_data['name'],
                            description=form.cleaned_data['description'],
                            owner=request.user)
            new_deal.save()
            if form.cleaned_data['user_is_buyer'] == True:
                assign_perm('buyer', request.user, new_deal)
            else:
                assign_perm('seller', request.user, new_deal)

            # add counterparty
            for party in counterparties.forms:
                email = party.cleaned_data['party_email']
                if email == '':
                    continue
                #new_deal.add_user(party.cleaned_data['vendor_email'], '', is_buyer)
                new_deal.add_user(email, '',
                                  party.cleaned_data['is_buyer']==True)
            return HttpResponseRedirect('/')
    form = DealForm()
    counterparty_form = CounterpartyFormSet()
    counterparty_form_helper = CounterpartyFormSetHelper()

    return render(request, 'add_deal.html', {
        'form': form,
        'counterparty_form': counterparty_form,
        'counterparty_form_helper': counterparty_form_helper
    })


def new_message(request, id):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            deal = Deal.objects.get(id=id)
            msg = DealMessage(message=form.cleaned_data['message'],
                            deal_id=id,
                            user=request.user,
                            is_buyer=deal.is_buyer(request.user))
            msg.save()
        return HttpResponseRedirect('/deal/' + id)
    return HttpResponseNotFound('<h1>Page not found</h1>')

def add_party(request, id):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            msg = DealMessage(message=form.cleaned_data['message'],
                            deal_id=id,
                            user=request.user)
            msg.save()


def invite(request, id=0):
    form = InviteForm(request.POST)
    if form.is_valid():
        deal = Deal.objects.get(id=id)
        is_buyer = deal.is_buyer(request.user)
        deal.add_user(form.cleaned_data['email'], form.cleaned_data['message'], is_buyer)
    return HttpResponseRedirect('/deal/' + id)

@require_POST
def add_attachment(request, id=0):
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        deal = Deal.objects.get(id=id)
        is_buyer = deal.is_buyer(request.user)
        print is_buyer
        att = Attachment(deal_id=id,
                        is_private=True,
                        is_buyer=is_buyer,
                        file_name=request.FILES['data'].name)
        att.data = request.FILES['data']
        att.save()
    return HttpResponseRedirect('/deal/' + id)

def edit_deal(request, id=0):
    deal = Deal.objects.get(id=id)
    if request.method == 'POST':
        form = EditDealForm(request.POST, instance=deal)
        if form.is_valid():
            form.save()
    user_is_buyer = request.user.has_perm('buyer', deal)
    perm_filter = permission_filter(user=request.user,
                                    user_is_buyer=user_is_buyer)
    deal = Deal.objects.get(id=id)

    
    participants = deal.participants
    print participants
    buyers = participants['buyers']
    sellers = participants['sellers']
    messages = DealMessage.objects.filter(deal_id=id)\
        .order_by('-created_date').filter(perm_filter)

    invite_form = InviteForm()
    form = EditDealForm(instance=deal)  # An unbound form
    message_form = MessageForm()
    attachment_form = AttachmentForm()
    attachments = Attachment.objects.filter(deal_id=id).filter(perm_filter)
    for at in attachments:
        print at.data
    pending_users = deal.pending_users
    return render(request, 'main/edit.html', {
        'deal': deal,
        'messages': messages,
        'attachments': attachments,
        'buyers': buyers,
        'sellers': sellers,
        'pending_users': pending_users,
        'deal_form': form,
        'deal_form_target': '/deal/' + id,
        'add_user_form': invite_form,
        'add_user_target': '/deal/' + id + '/invite/',
        'attachment_form': attachment_form,
        'attachment_form_target': '/deal/' + id + '/attach/',
        'message_form': message_form,
        'message_form_target': '/deal/' + id + '/message/'
    })


def delete_deal(request, id=0):
    deal = Deal.objects.get(id=id)
    if not deal.owner == request.user:
        # will hide from list
        permlist = get_perms(request.user, deal)
        for perm in permlist:
            remove_perm(perm, request.user, deal)
    else:
        deal.delete()
    return HttpResponseRedirect('/')

@login_required
def deal_list(request):
    shared_deals = get_objects_for_user(request.user, ['buyer', 'seller'], klass=Deal, any_perm=True)
    deals = Deal.objects.filter(owner_id=request.user.id)
    qs = deals | shared_deals
    print deals
    deals = qs.values('id',
                'name',
                'description',
                'start_date').order_by('-start_date')
    return render(request, 'main/list.html', {
        'deal_list': deals,
    })
