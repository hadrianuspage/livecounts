# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import redis
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django_grip import set_hold_stream
from .models import Counter
from .utils import sse_encode

r = redis.Redis()

def counter(request, counter_id):
	c = get_object_or_404(Counter, name=counter_id)

	if request.method == 'OPTIONS':
		return HttpResponse()
	elif request.method == 'GET':
		return HttpResponse(str(c.value) + '\n', content_type='text/plain')
	elif request.method == 'POST':
		prev = c.incr()
		pub_data = {
			'name': str(counter_id),
			'value': c.value,
			'prev-value': prev
		}
		r.publish('updates', json.dumps(pub_data))
		return HttpResponse(str(c.value) + '\n', content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['OPTIONS', 'GET', 'POST'])

def stream(request, counter_id):
	c = get_object_or_404(Counter, name=counter_id)

	if request.method == 'OPTIONS':
		return HttpResponse()
	elif request.method == 'GET':
		body = ':' + (' ' * 2048) + '\n\n'
		body += sse_encode(c.value)
		set_hold_stream(request, 'counter-%s' % counter_id)
		return HttpResponse(body, content_type='text/event-stream')
	else:
		return HttpResponseNotAllowed(['OPTIONS', 'GET'])
