from django.template.context import RequestContext
from os import sys

from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, render_to_response

from open_municipio.votations.models import Votation
from open_municipio.acts.models import Agenda, Deliberation, Interrogation, Interpellation, Motion


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

        # So we have an act. What kind of act, specifically? (FIXME: I
        # don't like the way act types are hardcoded here with their
        # Italian names.)
        if votation.act.downcast().__class__() == Agenda().__class__():
            act_type = "Ordine del Giorno"
        elif votation.act.downcast().__class__() == Deliberation().__class__():
            act_type = "Delibera"
        elif votation.act.downcast().__class__() == Interpellation().__class__():
            act_type = "Interpellanza"
        elif votation.act.downcast().__class__() == Interrogation().__class__():
            act_type = "Interrogazione"
        elif votation.act.downcast().__class__() == Motion().__class__():
            act_type = "Mozione"

        votation.act_type = act_type

        extra_context = {
            'votation': votation,
            }

        # Update context with extra values we need
        context.update(extra_context)
        return context

