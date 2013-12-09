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
from google.appengine.api import mail

import os
import urllib
import jinja2
import cgi
import datetime
import time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class PizzaEaters(ndb.Model):
	name = ndb.StringProperty()
	points = ndb.IntegerProperty()
	wants = ndb.BooleanProperty()
	last_fetch = ndb.DateProperty()
	able_to_get = ndb.BooleanProperty()
	extra = ndb.IntegerProperty()
	remark = ndb.StringProperty()
	mail = ndb.StringProperty()
	nr_of_fetches = ndb.IntegerProperty(default=0)
	nr_of_participatiens = ndb.IntegerProperty(default=0)

class MainHandler(webapp2.RequestHandler):
    def get(self):
		number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
		template_values2 = {
			'number_of_eaters': number_of_eaters,
		}
		header = JINJA_ENVIRONMENT.get_template('header.html')
		self.response.write(header.render())
		header2 = JINJA_ENVIRONMENT.get_template('header_index.html')
		self.response.write(header2.render(template_values2))
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render())
		
class ShowParticipants(webapp2.RequestHandler):
    def get(self):		
		eaters_points = PizzaEaters.query(PizzaEaters.wants == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
		fetcher = PizzaEaters.query(PizzaEaters.wants == True, PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()			
		last_fetcher = PizzaEaters.query().order(-PizzaEaters.last_fetch).get()
		last_fetcher_id = None
		if last_fetcher != None:
			last_fetcher_id = last_fetcher.key.id
		template_values = {
			'eaters_points': eaters_points,
			'last_fetcher': last_fetcher_id,
			'fetcher': fetcher,
	    }
		number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
		template_values2 = {
			'number_of_eaters': number_of_eaters,
		}
		header = JINJA_ENVIRONMENT.get_template('header.html')
		self.response.write(header.render())
		header2 = JINJA_ENVIRONMENT.get_template('header_participants.html')
		self.response.write(header2.render(template_values2))
		template = JINJA_ENVIRONMENT.get_template('who_signed_up.html')
		self.response.write(template.render(template_values))
		footer = JINJA_ENVIRONMENT.get_template('footer.html')
		self.response.write(footer.render())
		
class SignUpForPizza(webapp2.RequestHandler):
    def get(self):		
		eaters = PizzaEaters.query().order(PizzaEaters.name)
		template_values = {
			'eaters': eaters,
	    }
		number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
		template_values2 = {
			'number_of_eaters': number_of_eaters,
		}
		header = JINJA_ENVIRONMENT.get_template('header.html')
		self.response.write(header.render())
		header2 = JINJA_ENVIRONMENT.get_template('header_signup.html')
		self.response.write(header2.render(template_values2))
		# Check if its friday (wd: 4) and if the time is past 11 (h: >= 10)
		if(datetime.datetime.today().weekday() == 4 and datetime.datetime.now().hour >= 10 or datetime.datetime.today().weekday() > 4): #+1 for GB time. 
			template = JINJA_ENVIRONMENT.get_template('sign_up_too_late.html')
			self.response.write(template.render())
		else:
			template = JINJA_ENVIRONMENT.get_template('sign_up.html')
			self.response.write(template.render(template_values))
		footer = JINJA_ENVIRONMENT.get_template('footer.html')
		self.response.write(footer.render())	
		
class ShowEaters(webapp2.RequestHandler):
    def get(self):		
		eaters_all_points = PizzaEaters.query().order(-PizzaEaters.points).order(PizzaEaters.last_fetch)
		template_values = {
			'eaters_all_points': eaters_all_points
	    }
		number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
		template_values2 = {
			'number_of_eaters': number_of_eaters,
		}
		header = JINJA_ENVIRONMENT.get_template('header.html')
		self.response.write(header.render())
		header2 = JINJA_ENVIRONMENT.get_template('header_eaters.html')
		self.response.write(header2.render(template_values2))
		template = JINJA_ENVIRONMENT.get_template('eaters.html')
		self.response.write(template.render(template_values))
		footer = JINJA_ENVIRONMENT.get_template('footer.html')
		self.response.write(footer.render())
		
class RegisterForUser(webapp2.RequestHandler):
	def get(self):
		number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
		template_values2 = {
			'number_of_eaters': number_of_eaters,
		}
		header = JINJA_ENVIRONMENT.get_template('header.html')
		self.response.write(header.render())
		header2 = JINJA_ENVIRONMENT.get_template('header_register.html')
		self.response.write(header2.render(template_values2))
		template = JINJA_ENVIRONMENT.get_template('register.html')
		self.response.write(template.render())
		footer = JINJA_ENVIRONMENT.get_template('footer.html')
		self.response.write(footer.render())
	def post(self):
		firstname = cgi.escape(self.request.get('firstname'))
		lastname = cgi.escape(self.request.get('lastname'))
		email = cgi.escape(self.request.get('email'))
		mail.send_mail(sender="PizzaFriday <claesnl@gmail.com>",
		              to="Claes Ladefoged <claesnl@gmail.com>",
		              subject="PizzaFridag User Registration",
		              body="Firstname: "+firstname+"\nLastname: "+lastname+"\nEmail: "+email)
		self.redirect('/')
		
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
		
class ClearFriday(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			if PizzaEaters.query(PizzaEaters.wants == True).count() > 0:
				fetcher = PizzaEaters.get_by_id(int(cgi.escape(self.request.get('whoFetched'))))		
				eaters = PizzaEaters.query(PizzaEaters.wants == True)
				for e in eaters:
					points_change = 5
					if not e.able_to_get:
						points_change += 1
					e.points += points_change
					e.wants = False
					e.remark = ''
					e.extra = None
					e.nr_of_participatiens += 1
					e.put()
				fetcher.points = 0
				fetcher.last_fetch = datetime.date.today()
				fetcher.nr_of_fetches += 1
				fetcher.put()
				self.redirect('/admin')
			
class CronClearFriday(webapp2.RequestHandler):
	def get(self):
		if PizzaEaters.query(PizzaEaters.wants == True).count() == 0:
			return
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
			e.nr_of_participatiens += 1
			e.put()
		fetcher.points = 0
		fetcher.last_fetch = datetime.date.today()
		fetcher.nr_of_fetches += 1
		fetcher.put()
			
class CronFindFetcher(webapp2.RequestHandler):
	def get(self):
		if PizzaEaters.query(PizzaEaters.wants == True).count() == 0:
			return			
		fetcher = PizzaEaters.query(PizzaEaters.wants == True, PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()
		if fetcher == None:
			fetcher = PizzaEaters.query(PizzaEaters.wants == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()
			mail.send_mail(sender="PizzaFriday <claesnl@gmail.com>",
			              to="Claes Ladefoged <claesnl@gmail.com>",
			              subject="PizzaFridag: No one volunteered.",
			              body="Who fetched then (according to system): "+fetcher.name+"\nEmail: "+fetcher.mail)
		eaters = PizzaEaters.query(PizzaEaters.wants == True)
		pizzas = 0
		msg = ""
		for e in eaters:
			pizzas += 1
			msg += e.name
			if e.extra != None:
				pizzas += e.extra
				msg += " (+"+str(e.extra)+" extra guests)"
			if e.remark != '':
				msg += " Comment: "+e.remark
			msg += "\n"
			
		mail.send_mail(sender="PizzaFriday <claesnl@gmail.com>",
		              to=fetcher.name+" <"+fetcher.mail+">",
					  cc="Claes Ladefoged <claesnl@gmail.com>",
		              subject="PizzaFridag has selected you!",
		              body="Hello "+fetcher.name+"\nPizzaFriday has selected you to fetch the pizzas today. The list of people who is signed up is shown here:\n\n"+msg+"\n\nThe total number of people who have signed up is: "+str(pizzas)+" including you.\n\nThank you!")

class CronReminder(webapp2.RequestHandler):
	def get(self):
		eaters = PizzaEaters.query(PizzaEaters.wants == False)
		pizzas = 0
		msg = "You did not sign up for pizza this week. Sign up closes in 1 hour (at 11.00).\n\nKind regards, PizzaFredag"
		for e in eaters:
			mail.send_mail(sender="PizzaFriday <claesnl@gmail.com>",
					       to=e.name+" <"+e.mail+">",
					       subject="Forgot to sign up for PizzaFridag?",
					       body="Hello "+e.name+",\n\n"+msg)

class FindFetcher(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			if users.is_current_user_admin():				
				fetcher = PizzaEaters.query(PizzaEaters.wants == True, PizzaEaters.able_to_get == True).order(-PizzaEaters.points).order(PizzaEaters.last_fetch).get()
				if fetcher != None:
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
					self.response.write('Sorry, no users have signed up.')
				
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
			mail.send_mail(sender="PizzaFriday <claesnl@gmail.com>",
			              to=eater.name+" <"+eater.mail+">",
			              subject="User created at PizzaFridag!",
			              body="Hello "+eater.name+", \nYou are now a user at PizzaFriday. \nWhen you sign up for pizza you must use the password: pizza")
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
			self.redirect('/participants')
		else:
			self.response.write('Sorry, you need the password. <a href="/">Back</a>')
			
class DeRegister(webapp2.RequestHandler):
	def get(self,e_id):
		# Check if its friday (wd: 4) and if the time is past 11 (h: >= 10)
		if(datetime.datetime.today().weekday() == 4 and datetime.datetime.now().hour >= 10 or datetime.datetime.today().weekday() > 4): #+1 for GB time.
			number_of_eaters = PizzaEaters.query(PizzaEaters.wants == True).count()
			template_values2 = {
				'number_of_eaters': number_of_eaters,
			}
			header = JINJA_ENVIRONMENT.get_template('header.html')
			self.response.write(header.render())
			header2 = JINJA_ENVIRONMENT.get_template('header_signup.html')
			self.response.write(header2.render(template_values2))
			self.response.write('<div class="alert alert-danger">You can not de-register after the deadline. Suck it up and eat your pizza!</div>')
			footer = JINJA_ENVIRONMENT.get_template('footer.html')
			self.response.write(footer.render())
			return
			
		eater = PizzaEaters.get_by_id(int(e_id))
		if not eater:
			self.response.write('Could not find user with id: '+str(e_id))
		else:
			eater.remark = ''
			eater.wants = False
			eater.remark = ''
			eater.extra = None
			eater.put()
			self.redirect('/participants')

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
	('/participants', ShowParticipants),
	('/sign_up_for_pizza', SignUpForPizza),
	('/pizza_eaters', ShowEaters),
	('/register_for_membership', RegisterForUser),
	('/admin/add_eater', CreateEater),
	('/admin/remove_eater/(\d+)', RemoveEater),
	('/admin/find_fetcher', FindFetcher),
	('/admin/clear_friday', ClearFriday),
	('/cron/give_points', CronClearFriday),
	('/cron/find_fetcher', CronFindFetcher),
	('/cron/remind_eaters', CronReminder),
	('/de_register/(\d+)', DeRegister),
	('/register', Register),
	('/android/all_users', AndroidAllUsers),
	('/android/participants', AndroidParticipants),
	('/admin', AdminHandler)
], debug=True)