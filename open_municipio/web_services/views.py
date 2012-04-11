import json
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from django.http import HttpResponse
from open_municipio.web_services.models import Sharing

def share(request,app, model, object_id):

    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({
            'result': 'error',
            'message': 'Esegui l\' accesso per condividere il contenuto'
        }), mimetype="application/json")


    response_data = {
        'result': 'success',
        'message': ''
    }

    content_type = ContentType.objects.get_by_natural_key(app, model)

    if request.POST['action'] == 'add':
        try:
            share = Sharing(
                object_id= object_id,
                content_type= content_type,
                user= request.user.get_profile(),
                service= request.POST['service']
            )
            share.save()
        except IntegrityError:
            return HttpResponse(json.dumps({
                'result': 'error',
                'message': 'Esegui l\' accesso per condividere il contenuto'
            }), mimetype="application/json")


    if request.POST['action'] == 'remove':
        share = Sharing.objects.filter(
            object_id= object_id,
            content_type= content_type,
            user= request.user.get_profile(),
            service= request.POST['service']
        )
        share.delete()
        response_data['message'] = 'Condivisione rimossa correttamente'

    return HttpResponse(json.dumps(response_data), mimetype="application/json")