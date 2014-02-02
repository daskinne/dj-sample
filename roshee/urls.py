from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.views.generic import TemplateView
from roshee.forms import SignupFormExtra

class DirectTemplateView(TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'roshee.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^login', 'userena.views.signin'),
    (r'^logout', 'userena.views.signout'),
    (r'^accounts/signup/$',
     'userena.views.signup',
     {'signup_form': SignupFormExtra}),
    (r'^accounts/', include('userena.urls')),
    (r'^deal/new', 'roshee.views.new_deal'),
    (r'^deal/(?P<id>\d+)/message', 'roshee.views.new_message'),
    (r'^deal/(?P<id>\d+)/delete', 'roshee.views.delete_deal'),
    (r'^deal/(?P<id>\d+)/attach', 'roshee.views.add_attachment'),
    (r'^deal/(?P<id>\d+)/invite', 'roshee.views.invite'),
    (r'^deal/(?P<id>\d+)', 'roshee.views.edit_deal'),
    (r'^deals/', 'roshee.views.deal_list'),
    (r'^$', 'roshee.views.deal_list'),
    # (r'^$', DirectTemplateView.as_view(template_name="index.html")),
)
