from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from pi_io_site.models import *
import urllib2
import urllib
import json

@csrf_exempt
def register(request):
    """
    When a rpi connects to the WS server this is called
    """
    if request.method == 'POST':
        try:
            jreq = json.loads(request.POST['json'])
        except:
            return HttpResponseBadRequest('Unable to parse post json key', mimetype='application/json')

        # verify fields exist
        if 'mac' not in jreq or 'ip' not in jreq or 'iface' not in jreq:
            return HttpResponseBadRequest('Does not have required fields', mimetype='application/json')

        # update rpi model
        rpi_db, created = RaspberryPi.objects.get_or_create(mac_address=jreq['mac'], defaults={'current_ip':jreq['ip']})

        if created:
            # create a default name
            rpi_db.name = '%s - %s' % (jreq['mac'], jreq['ip'])

        rpi_db.current_ip = jreq['ip']
        rpi_db.online = True
        rpi_db.save()

        def update_iface(model_cls, index_name):
            if index_name in jreq['iface']:
                for iface in jreq['iface'][index_name]:
                    iface_db, created = model_cls.objects.get_or_create(rpi=rpi_db, name=iface['name'],
                        defaults={'io_type':iface['io_type']})

                    iface_db.description = iface['desc']
                    iface_db.possible_choices = json.dumps(iface['choices'])
                    iface_db.save()

        # update referring interface models
        update_iface(RPIReadInterface, 'read')
        update_iface(RPIWriteInterface, 'write')

        print jreq

    return HttpResponse('ok', mimetype='application/json')

@csrf_exempt
def disconnect(request):
    if request.method == 'POST':
        try:
            jreq = json.loads(request.POST['json'])
        except:
            return HttpResponseBadRequest('Unable to parse post json key', mimetype='application/json')

        # verify fields exist
        if 'mac' not in jreq:
            return HttpResponseBadRequest('Does not have required fields - mac', mimetype='application/json')

        rpi = RaspberryPi.objects.get(mac_address=jreq['mac'])
        rpi.online = False
        rpi.save()

    return HttpResponse('ok', mimetype='application/json')

def test(request):
    post_data = {'a':43, 'b':11}
    post_data = urllib.urlencode(post_data)
    url = urllib2.Request('https://localhost:8090', post_data)
    url_response = urllib2.urlopen(url)

    return HttpResponse(url_response.read(), mimetype='application/json')