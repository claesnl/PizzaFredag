#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

import os
import urllib
import jinja2
import cgi
import datetime

class PizzaEaters(ndb.Model):
	name = ndb.StringProperty()
	points = ndb.IntegerProperty()
	wants = ndb.BooleanProperty()
	last_fetch = ndb.DateProperty()
	able_to_get = ndb.BooleanProperty()
	extra = ndb.IntegerProperty()
	remark = ndb.StringProperty()
	mail = ndb.StringProperty()
			
class CronClearFriday(webapp2.RequestHandler):
	def get(self):
		fetcher = PizzaEaters.query(PizzaEaters.wants == True and PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()			
		eaters = PizzaEaters.query(PizzaEaters.wants == True)
		for e in eaters:
			points_change = 5
			if not e.able_to_get:
				points_change += 1
			e.points = e.points + points_change
			e.wants = False
			e.remark = ''
			e.extra = None
			e.put()
		fetcher.points = 0
		fetcher.last_fetch = datetime.date.today()
		fetcher.put()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/create_friday', CreateFriday),
	('/admin/add_eater', CreateEater),
	('/admin/remove_eater/(\d+)', RemoveEater),
	('/admin/find_fetcher', FindFetcher),
	('/admin/clear_friday', ClearFriday),
	('/cron/sunday', CronClearFriday),
	('/de_register/(\d+)', DeRegister),
	('/register', Register),
	('/admin', AdminHandler)
], debug=True)