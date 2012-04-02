from django.template.context import RequestContext
from os import sys

from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, render_to_response

from open_municipio.votations.models import Votation


class VotationDetailView(DetailView):
    """
    Renders a Votation page
    """
    model = Votation
    template_name = 'votations/votation_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VotationDetailView, self).get_context_data(**kwargs)

        votation = self.object
        extra_context = {
            'votation': votation,
            }

        # Update context with extra values we need
        context.update(extra_context)
        return context

