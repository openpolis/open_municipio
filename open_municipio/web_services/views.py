import json
from django.http import HttpResponse

def share(request,content_type, object_id):
    response_data = {}
    response_data['result'] = request.POST
    response_data['message'] = 'You messed up'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")