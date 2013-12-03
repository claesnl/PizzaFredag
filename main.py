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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Fridays(ndb.Model):
    date = ndb.DateProperty(auto_now_add=True)

class PizzaEaters(ndb.Model):
	name = ndb.StringProperty()
	points = ndb.IntegerProperty()
	wants = ndb.BooleanProperty()
	last_fetch = ndb.DateProperty()
	able_to_get = ndb.BooleanProperty()
	extra = ndb.IntegerProperty()
	remark = ndb.StringProperty()
	mail = ndb.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):		
		eaters_points = PizzaEaters.query(PizzaEaters.wants == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
		eaters_all_points = PizzaEaters.query().order(-PizzaEaters.points)
		eaters = PizzaEaters.query().order(PizzaEaters.name)
		template_values = {
			'eaters': eaters,
			'eaters_points': eaters_points,
			'eaters_all_points': eaters_all_points
	    }
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))
		
class AdminHandler(webapp2.RequestHandler):
    def get(self):	
		if users.is_current_user_admin():
			user = users.get_current_user()
			eaters_points = PizzaEaters.query(PizzaEaters.wants == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
			eaters_all_points = PizzaEaters.query().order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
			eaters = PizzaEaters.query().order(PizzaEaters.name)
			template_values = {
				'eaters': eaters,
				'eaters_points': eaters_points,
				'eaters_all_points': eaters_all_points,
				'logout_url': users.create_logout_url('/'),
				'nick': user.nickname()
		    }
			template = JINJA_ENVIRONMENT.get_template('admin.html')
			self.response.write(template.render(template_values))
		else:
			self.response.write('<a href="%s">Sign in</a>.' % users.create_login_url('/admin'))

class CreateFriday(webapp2.RequestHandler):
	def get(self):
		friday = Fridays()
		friday.put()
		self.redirect('/')
		
class ClearFriday(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():

			fetcher = PizzaEaters.get_by_id(int(cgi.escape(self.request.get('whoFetched'))))
							
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
			self.redirect('/admin')
			
class CronClearFriday(webapp2.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			fetcher = PizzaEaters.query(PizzaEaters.wants == True, PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()			
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

class FindFetcher(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			if users.is_current_user_admin():				
				fetcher = PizzaEaters.query(PizzaEaters.wants == True, PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()
				eaters = PizzaEaters.query(PizzaEaters.wants == True)
				pizzas = 0
				for e in eaters:
					pizzas += 1
					if e.extra != None:
						pizzas += e.extra
				eaters = PizzaEaters.query(PizzaEaters.wants == True)
				template_values = {
					'fetcher': fetcher.name,
					'nrOfPizzas': pizzas,
					'eaters': eaters
				}
				template = JINJA_ENVIRONMENT.get_template('who_fetches.html')
				self.response.write(template.render(template_values))
				
			else:
				self.response.write('Sorry, ' + user.nickname() + '. You need to be admin.')
		else:
			self.response.write('<a href="%s">Sign in</a>.' % users.create_login_url('/'))
			

class CreateEater(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			eater = PizzaEaters()
			eater.name = cgi.escape(self.request.get('firstname')) + " " + cgi.escape(self.request.get('lastname'))
			eater.mail = cgi.escape(self.request.get('email'))
			eater.points = 0
			eater.wants = False
			eater.put()
			self.redirect('/admin')
		else:
			self.response.write('Sorry, you need to be admin.')
			
class RemoveEater(webapp2.RequestHandler):
	def get(self,e_id):
		if users.is_current_user_admin():
			eater = PizzaEaters.get_by_id(int(e_id))
			eater.key.delete()
			self.redirect('/admin')
		else:
			self.response.write('Sorry, you need to be admin.')

class Register(webapp2.RequestHandler):
	def post(self):
		if(cgi.escape(self.request.get('password')) == "pizza"):			
			eater = PizzaEaters.get_by_id(int(self.request.get('attendee')))
			eater.remark = cgi.escape(self.request.get('comment'))
			eater.wants = True
			if(self.request.get('persons') == "x"):
				eater.able_to_get = False
			elif(self.request.get('persons') == "2"):
				eater.able_to_get = True
				eater.extra = int(cgi.escape(self.request.get('numguests')))
			else:
				eater.able_to_get = True
			eater.put()
			self.redirect('/')
		else:
			self.response.write('Sorry, you need the password. <a href="/">Back</a>')
			
class DeRegister(webapp2.RequestHandler):
	def get(self,e_id):
		user = users.get_current_user()
		if user:
			eater = PizzaEaters.get_by_id(int(e_id))
			if not eater:
				self.response.write('Could not find user with id: '+str(e_id))
			else:
				eater.remark = ''
				eater.wants = False
				eater.remark = ''
				eater.extra = None
				eater.put()
				self.redirect('/')
		else:
			self.response.write('<a href="%s">Sign in</a>.' % users.create_login_url('/'))

class AndroidAllUsers(webapp2.RequestHandler):
	def get(self):
		eaters_all_points = PizzaEaters.query().order(-PizzaEaters.points)
		template_values = {
			'eaters_all_points': eaters_all_points
	    }
		template = JINJA_ENVIRONMENT.get_template('android_points_table.html')
		self.response.write(template.render(template_values))
		
class AndroidParticipants(webapp2.RequestHandler):
	def get(self):
		eaters_points = PizzaEaters.query(PizzaEaters.wants == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
		template_values = {
			'eaters_points': eaters_points
	    }
		template = JINJA_ENVIRONMENT.get_template('android_participants.html')
		self.response.write(template.render(template_values))
			

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
	('/android/all_users', AndroidAllUsers),
	('/android/participants', AndroidParticipants),
	('/admin', AdminHandler)
], debug=True)