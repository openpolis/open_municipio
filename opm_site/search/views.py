from django.shortcuts import render_to_response
from django.contrib.flatpages.models import FlatPage

def search(request): 
  query = request.GET.get('q', '')
  results = []
  if query:
    results = FlatPage.objects.filter(content__icontains=query)

  return render_to_response('search/search.html', 
                            { 'query': query,
                              'results': results })
  