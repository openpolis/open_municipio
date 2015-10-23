from rest_framework import serializers

from open_municipio.acts.models import Act, Deliberation
from open_municipio.people.models import Person

# acts
class ActSerializer(serializers.ModelSerializer):
    
    class Meta:
    
        model = Act
        fields = ( "idnum", "title", "adj_title", "presentation_date", 
                    "description","text", "status_is_final", "is_key",
                    "slug" )

class DeliberationSerializer(serializers.ModelSerializer):

    class Meta:

        model = Deliberation
        fields = ActSerializer.Meta.fields + ( "status", "approval_date", 
                    "publication_date", "final_idnum", "execution_date", 
                    "initiative", "approved_text" )


class CGDeliberationSerializer(serializers.ModelSerializer):

    class Meta:

        model = Deliberation
        fields = ActSerializer.Meta.fields + ( "status", "approval_date", 
                    "publication_date", "final_idnum", "execution_date", 
                    "initiative", "approved_text" )


# people
class PersonSerializer(serializers.ModelSerializer):
    
    class Meta:

        model = Person
        fields = ( 'first_name', 'last_name', 'birth_date', 'slug', 'sex', 
                    'op_politician_id', 'img', )
