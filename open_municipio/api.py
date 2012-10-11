"""
This module provides a hierarchy of Python objects designed to implement a **private DB API** for OpenMunicipio.

With the locution *private DB API* we mean an object-based API providing easier access -- compared to the Django ORM --
to the data stored within the DB. The word *private* refers to the fact that this API is intended for 
**internal use only** (in particular, the view and template layers should rely on this API when possible, 
instead of re-implementing their own.

In a nutshell, this private DB API may be considered a thin abstraction layer on the top of Django ORM. 
""" 

from open_municipio.people.models import Institution, InstitutionCharge, Group


class Mayor(object):
    """
    A municipality mayor (both as a charge and an institution).
    """
     
    @property
    def as_institution(self):
        """
        A municipality mayor, as an *institution*.
        """
        return Institution.objects.select_related().get(institution_type=Institution.MAYOR)
    
    @property
    def as_charge(self):
        """
        A municipality mayor, as a *charge*.
        """
        return InstitutionCharge.objects.select_related().get(institution__institution_type=Institution.MAYOR)
    
    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the mayor (as an institution).
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.emitted_acts
    

class CityCouncil(object):
    @property
    def as_institution(self):
        """
        A municipality council, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.COUNCIL)
    
    @property
    def charges(self):
        """
        All current members of the municipality council (aka *counselors*), as charges.
        President and vice-presidents **included**.
        """
        return self.as_institution.charges.select_related()

    @property
    def president(self):
        """
        The current president of the city council as InstitutionResponsability
        None if not found.
        """
        return  self.as_institution.president


    @property
    def vicepresidents(self):
        """
        The current vice presidents of the city council, as InstitutionResponsabilities

        There can be more than one vicepresident
        """
        return self.as_institution.vicepresidents.select_related()

    @property
    def members(self):
        """
        Members of the municipality council (aka *counselors*), as charges.
        Current president and vice presidents **excluded**.
        """
        return self.as_institution.members.select_related()

    @property
    def majority_members(self):
        """
        Majority counselors, as charges.
        """
        # FIXME: this method should return a QuerySet, non a Set
        result = set()
        for majority_group in self.majority_groups:
            result.add(majority_group.counselors)            
        return result
    
    @property
    def minority_members(self):
        """
        Minority counselors, as charges.
        """
        # FIXME: this method should return a QuerySet, non a Set
        result = set()
        for minority_group in self.minority_groups:
            result.add(minority_group.counselors)            
        return result
        
    @property
    def groups(self):
        """
        Groups of counselors within of a municipality council.
        """
        return Group.objects.select_related().all()
    
    @property
    def majority_groups(self):
        """
        Counselors' groups belonging to majority.
        """
        qs = Group.objects.select_related().filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=True)
        return qs
    
    @property
    def minority_groups(self):
        """
        Counselors' groups belonging to minority.
        """
        qs = Group.objects.select_related().filter(groupismajority__end_date__isnull=True).filter(groupismajority__is_majority=False)
        return qs

    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the City Council.
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.select_related().emitted_acts
    
    @property
    def deliberations(self):
        """
        The QuerySet of all deliberations emitted by the City Council.
        """
        from open_municipio.acts.models import Deliberation
        return Deliberation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Council.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Council.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.select_related().filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Council.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Council.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.select_related().filter(emitting_institution=self.as_institution)


class CityGovernment(object):
    @property
    def as_institution(self):
        """
        A municipality government, as an *institution*.
        """
        return Institution.objects.get(institution_type=Institution.CITY_GOVERNMENT)
    
    @property
    def charges(self):
        """
        Members of a municipality government (mayor and first deputy included), as charges.
        """
        return self.as_institution.charges.select_related()

    @property
    def firstdeputy(self):
        """
        Returns the first deputy mayor, if existing, None if not existing
        """
        return  self.as_institution.firstdeputy

    @property
    def members(self):
        """
        Members of a municipality government (mayor and first deputy excluded), as charges.
        """
        return self.as_institution.members.select_related()

    @property
    def acts(self):
        """
        The QuerySet of all acts emitted by the city government (as an institution).
        
        Note that the objects comprising the resulting QuerySet aren't generic ``Act`` instances,
        but instances of specific ``Act`` subclasses (i.e. ``Deliberation``, ``Motion``, etc.).
        """
        return self.as_institution.emitted_acts
    
    @property
    def deliberations(self):
        """
        The QuerySet of all deliberations emitted by the City Government.
        """
        from open_municipio.acts.models import Deliberation
        return Deliberation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interrogations(self):
        """
        The QuerySet of all interrogations emitted by the City Government.
        """
        from open_municipio.acts.models import Interrogation
        return Interrogation.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def interpellations(self):
        """
        The QuerySet of all interpellations emitted by the City Government.
        """
        from open_municipio.acts.models import Interpellation
        return Interpellation.objects.select_related().filter(emitting_institution=self.as_institution)
            
    @property
    def motions(self):
        """
        The QuerySet of all motions emitted by the City Government.
        """
        from open_municipio.acts.models import Motion
        return Motion.objects.select_related().filter(emitting_institution=self.as_institution)
    
    @property
    def agendas(self):
        """
        The QuerySet of all agendas emitted by the City Government.
        """
        from open_municipio.acts.models import Agenda
        return Agenda.objects.select_related().filter(emitting_institution=self.as_institution)


class Committees(object):
    def as_institution(self):
        """
        Municipality committees, as *institutions*.
        """
        # FIXME: Should we include joint committees here?
        # (Institution.JOINT_COMMITTEE)
        return Institution.objects.select_related().filter(
            institution_type__in=(Institution.COMMITTEE, Institution.JOINT_COMMITTEE)
        )



class Municipality(object):
    """
    A hierarchy of objects representing a municipality.
    
    Provides convenient access to insitutions, charges, groups and the like.
    """  
    def __init__(self):
        self.mayor = Mayor()
        self.gov = CityGovernment()
        self.council = CityCouncil()
        self.committees = Committees()
  
  
municipality = Municipality()