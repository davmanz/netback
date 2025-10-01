from django.http import JsonResponse

def health_check(request):
    """
    Vista simple que devuelve un estado 'ok' para los health checks.
    """
    return JsonResponse({"status": "ok"})
