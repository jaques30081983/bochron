import kivy
#kivy.require('1.4.2')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.slider import Slider
import time
import random
import urllib
from datetime import timedelta
from datetime import datetime
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from functools import partial
from kivy.factory import Factory
from kivy.storage.jsonstore import JsonStore

store = JsonStore('bochron_config.json')

#Layout
class Bochron(BoxLayout):
#Globals	
	global session_id
	session_id = ''

	global count_value
	global elapsed_time

	elapsed_time = ''
	count_value = 1
	
	if store.exists('settings'):
		global store_session_id
		global store_user
		store_session_id = store.get('settings')['session_id']
		store_user = store.get('settings')['user']

	def __init__(self, **kwargs):
		super(Bochron, self).__init__(**kwargs)
		
		if store.exists('settings'):
			if store_session_id == '':
				pass
			else:
				global working_server_adress
				working_server_adress = store.get('settings')['server_adress']
				self.bochron_login_status(self)

		
#Programm	
	def get_by_id(self, search_id, text_for_id):
		print 'fired'
		children = self.children[:]
		while children:
			child = children.pop()
			#print("{} -> {}".format(child, child.id))
			children.extend(child.children)
			if child.id == search_id:
				child.text = text_for_id
			
				
	def extend_children_ids(self, *args):
		children = self.children[:]
		while children:
			child = children.pop()
			print("{} -> {}".format(child, child.id))
			children.extend(child.children)
			
	
	def start_count(self,recorder_id, rec_start_time, ss):
		global elapsed_time
		global start_time
		global recorder_id1
		recorder_id1 = recorder_id
		
		if rec_start_time == '':
			start_time = time.strftime("%Y-%m-%d %H:%M:%S")
		else:	
			start_time = rec_start_time
		
		if ss == 1:
			Clock.schedule_interval(self.update_counter,  1.)
		else:
			Clock.unschedule(self.update_counter)
			itm['rec_counter_'+str(recorder_id1)].text = ''
			
		print recorder_id
		#self.rec_time(recorder_id)
		#self.get_by_id('recorder_counter_'+str(recorder_id),recorder_id)
		
	
	def comp_dates(self,d1):
		# Date format: %Y-%m-%d %H:%M:%S
		t = datetime.now()
		#d1 = '2015-03-01 03:25:09'
		#time.mktime(t.timetuple()) -
		return (time.mktime(t.timetuple()) - time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S")))
		
	def update_counter(self,dt):
		global count_value
		global start_time
		global recorder_id1
		
		
		elapsed_time = self.comp_dates(start_time) -3600
		
		#elapsed_time = round(elapsed_time, 2)
		
		elapsed_time = (datetime.fromtimestamp(int(elapsed_time)).strftime('%H:%M:%S'))
		
    
		#elapsed_time = datetime.strftime("%H:%M:%S", datetime.fromtimestamp(int(elapsed_time)))

		
		#elapsed_time = datetime.datetime() - start_time
		#elapsed_time1 = datetime.strftime("%H:%M:%S", datetime.gmtime(elapsed_time))
		#count_value = 1 + count_value
		
		itm['rec_counter_'+str(recorder_id1)].text = str(elapsed_time)
		print str(elapsed_time)
		
	
	

		
	
	
	
		
#User Autentication		
	def bochron_connect(self,server_adress):
		
		def bochron_connected(req, results):
			self.ids.kv_user_list.clear_widgets(children=None)
			self.ids.sm.current = 'login_user'
			
			for row in results:
				print row['bname']
				
				self.ids.kv_user_list.add_widget(UserSelectButton(text=row['bname']))
		
			global working_server_adress
			working_server_adress = server_adress	
#			store.put('settings', server_adress=server_adress, ssl='0')
#			self.ids.sm.current = 'work1'
		
		
		req = UrlRequest('http://'+server_adress+'/bochron_backend/?b=get_user',bochron_connected)
		
		
	def bochron_login(self, user, password):
		global selected_user 
		selected_user = user
		self.ids.sm.current = 'login_auth'
		self.ids.kv_password_input.focus = True
		
		self.ids.kv_user_label.text = user
		
		#self.ids.kv_login_list.add_widget(Label(size_hint_y= 1, text=user, font_size=25), len(self.ids.kv_login_list.children))
		
		
		
	def bochron_login_auth(self, password):	
		
		
		def bochron_login_auth_check(req, results):
				
						
			for row in results:
							
				if row['login_status'] == '1':
					print row['session_id']
					global session_id
					session_id = row['session_id']
					self.ids.sm.current = 'view_projekts'
					self.ids.kv_user_button.text = selected_user
					self.ids.kv_password_input.focus = False
					
					#Store
					store.put('settings', server_adress=working_server_adress, ssl='0', session_id=session_id, user=selected_user)
					
					#Retrive data
					self.ids.recorder_box.clear_widgets(children=None)
					self.get_recorder()
					
				
				if row['login_status'] == '0':
					self.ids.kv_password_input.text = ''
					self.ids.kv_password_input.focus = True
					self.ids.kv_login_button.text = 'retry login'
				
				#self.ids.kv_user_list.add_widget(UserSelectButton(text=row['user']))
				
			#store.put('settings', server_adress=server_adress, ssl='0')
#			self.ids.sm.current = 'work1'
		
		if session_id == '':
			req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?b=auth_user&user='+selected_user+'&password='+password, bochron_login_auth_check)
		else:
			req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=auth_user&user='+selected_user+'&password='+password, bochron_login_auth_check)
	


	def bochron_logout(self):	
		
		
		def bochron_logout_check(req, results):
				
						
			for row in results:
				
				if row['login_status'] == '1':
					self.ids.logout_button.text = 'Retry to Logout'
							
				if row['login_status'] == '0':
					self.ids.logout_button.text = 'You logged out'
					exit()
					
		
		req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=logout', bochron_logout_check)
	



	def bochron_login_status(self,*args):	
		global store_user
		global store_session_id
		
		def bochron_login_status_check(req, results):
			
						
			for row in results:
				
				if row['login_status'] == '1':
					global session_id
					session_id = store_session_id
					self.ids.sm.current = 'view_projekts'
					self.ids.kv_user_button.text = store_user
					#Retrive data
					self.ids.recorder_box.clear_widgets(children=None)
					self.get_recorder()
					
					
							
				if row['login_status'] == '0':
					self.ids.sm.current = 'server_connect'
					
					
					
		
		req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+store_session_id+'&b=login_status', bochron_login_status_check)
	



	
	def bochron_logout_change(self):
		req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=logout')

#Get Recorder
	def get_recorder(self):	
		global session_id
	
	
		def result_recorder(req, results):
			global itm
			global recorder_count
			recorder_count = 0
			
			itm = {}
			for row in results:
				print row['id']
				print row['color']
				print row['title']
				print row['open_rec']
				print row['start_time']

				recorder_count = recorder_count+1
				
				float_layout1 = FloatLayout(size_hint=[0.3, None])
				itm['rec_btn_'+str(row['id'])] = RecorderButton(id=str(row['id']), pos_hint= {'x': .0, 'y': .0}, size_hint=[1, 1], background_normal='', background_color=row['color'].split(","), text=row['title'])
				
				if row['open_rec'] == 0:
					itm['rec_counter_'+str(row['id'])] = Label(id='rec_counter_'+str(row['id']), pos_hint= {'x': .2, 'y': -.25}, size_hint=[1, 1], text='')
				elif row['open_rec'] == 1:
					self.start_count(row['id'], row['start_time'],1)
					itm['rec_counter_'+str(row['id'])] = Label(id='rec_counter_'+str(row['id']), pos_hint= {'x': .2, 'y': -.25}, size_hint=[1, 1], text='')
				
				
				float_layout1.add_widget(itm['rec_btn_'+str(row['id'])])
				float_layout1.add_widget(itm['rec_counter_'+str(row['id'])])

				self.ids.recorder_box.add_widget(float_layout1)
				
			#itm['rec_btn_3'].text = 'test'
			#itm['rec_counter_2'].text = 'test count'

				
		
		req = UrlRequest(
			'http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=get_recorder',
			result_recorder)
			
			
			
			
#Record start/stop
	def rec_start_stop(self, recorder_id):
		global session_id
		global recorder_count
		
		def rec_start_stop_result(req, results):
			itm['rec_btn_'+recorder_id].disabled = False
			
			for row in results:
				if row['login_status'] == 1:

					if itm['rec_counter_'+recorder_id].text == '':
						self.start_count(recorder_id, '',1)
						for x in range(0, 99):
							self.get_by_id('rec_counter_'+str(x),'')
					else:
						self.start_count(recorder_id, '',0)
						for x in range(0, recorder_count):
							self.get_by_id('rec_counter_'+str(x),'')
							
				if row['login_status'] == 0:	
					self.ids.sm.current = 'login_user'		
		
		def rec_start_stop_error(request,error):
			itm['rec_counter_'+recorder_id].text = 'no con, retry'
			itm['rec_btn_'+recorder_id].disabled = True
			
			def clear_reg_counter(dt):
				itm['rec_counter_'+recorder_id].text = ''
				itm['rec_btn_'+recorder_id].disabled = False
				
			Clock.schedule_once(clear_reg_counter, 2)
			
		itm['rec_btn_'+recorder_id].disabled = True
		req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=rec_start_stop&recorder_id='+recorder_id, rec_start_stop_result,on_error=rec_start_stop_error)
		
		
		
		
#Add Recorder
	def add_recorder(self):
		global session_id
		global recorder_count
		global rec_color
		r = round(random.uniform(0.3, 1.0),2)
		g = round(random.uniform(0.3, 1.0),2)
		b = round(random.uniform(0.3, 1.0),2)
		rec_color = ''+str(r)+','+str(g)+','+str(b)+',1'
		
		def add_recorder_result(req, results):
			global itm
			global rec_color
						
			itm = {}
			for row in results:
				
				
				if row['login_status'] == 1:
					print row['id']
					row['color'] = rec_color
					row['title'] = self.ids.add_rec_title.text
					
					
					float_layout1 = FloatLayout(size_hint=[0.3, None])
					itm['rec_btn_'+str(row['id'])] = RecorderButton(id=str(row['id']), pos_hint= {'x': .0, 'y': .0}, size_hint=[1, 1], background_normal='', background_color=row['color'].split(","), text=row['title'])
					itm['rec_counter_'+str(row['id'])] = Label(id='rec_counter_'+str(row['id']), pos_hint= {'x': .25, 'y': -.25}, size_hint=[1, 1], text='')
					
					float_layout1.add_widget(itm['rec_btn_'+str(row['id'])])
					float_layout1.add_widget(itm['rec_counter_'+str(row['id'])])

					self.ids.recorder_box.add_widget(float_layout1)
					
					self.ids.sm.current = 'view_projekts'
				
				if row['login_status'] == 0:
					self.ids.sm.current = 'login_user'
		
		req = UrlRequest('http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=add_recorder&color='+rec_color+'&title='+self.ids.add_rec_title.text+'&description='+self.ids.add_rec_description.text, add_recorder_result)
				

#Get History
	def get_history(self):	
		global session_id
	
	
		def result_history(req, results):
			self.ids.history_box.clear_widgets(children=None)	
			itm = {}
			for row in results:
				print row['id']
				
				if row['show_day_minutes'] == 1:
					self.ids.history_box.add_widget(Button(text=row['last_time'], background_normal='', pos_hint= {'x': .0, 'y': .0}, size_hint=[1, 1], background_color=[0.3,0.3,0.3,1]))
				
				float_layout1 = FloatLayout(size_hint=[0.3, None])
				itm['history_btn_'+str(row['id'])] = HistoryButton(id=str(row['id']), pos_hint= {'x': .0, 'y': .0}, size_hint=[1, 1],  background_normal='', background_color=row['color'].split(","), text=row['recorder'] +'  '+ row['time'])
				self.ids.history_box.add_widget(itm['history_btn_'+str(row['id'])])
				
				
				#float_layout1.add_widget(itm['history_btn_'+str(row['id'])])
				#self.ids.history_box.size_hint_y = self.ids.history_box.size_hint_y + 0.06
				#self.ids.history_box.add_widget(float_layout1)
				
			#itm['rec_btn_3'].text = 'test'
			#itm['rec_counter_2'].text = 'test count'

				
		
		req = UrlRequest(
			'http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=get_history',
			result_history)
			
#Adjust DateTime with Sliders			
	def add_rem_datetime0(self, slider_value):
		global h_rec_start_time
		global h_rec_start_time_init
		dt1 = datetime.strptime(h_rec_start_time_init, "%Y-%m-%d %H:%M:%S")
		
		dt2 = time.mktime(dt1.timetuple()) + int(slider_value)
		
		dt3 = datetime.fromtimestamp(dt2).strftime('%Y-%m-%d %H:%M:%S')
		
		h_rec_start_time.text = dt3

	def add_dhm_datetime0(self, op, dhm, *args):
		global h_rec_start_time
		global h_rec_start_time_init
		dt1 = datetime.strptime(h_rec_start_time.text, "%Y-%m-%d %H:%M:%S")

		if op == 0:
			dt2 = time.mktime(dt1.timetuple()) - dhm
		if op == 1:
			dt2 = time.mktime(dt1.timetuple()) + dhm

		dt3 = datetime.fromtimestamp(dt2).strftime('%Y-%m-%d %H:%M:%S')

		h_rec_start_time.text = dt3
		
	def add_rem_datetime1(self, slider_value):
		global h_rec_stop_time
		global h_rec_stop_time_init
		dt1 = datetime.strptime(h_rec_stop_time_init, "%Y-%m-%d %H:%M:%S")
		
		dt2 = time.mktime(dt1.timetuple()) + int(slider_value)
		
		dt3 = datetime.fromtimestamp(dt2).strftime('%Y-%m-%d %H:%M:%S')
		
		h_rec_stop_time.text = dt3	

	def add_dhm_datetime1(self, op, dhm, *args):
		global h_rec_stop_time
		global h_rec_stop_time_init
		dt1 = datetime.strptime(h_rec_stop_time.text, "%Y-%m-%d %H:%M:%S")

		if op == 0:
			dt2 = time.mktime(dt1.timetuple()) - dhm
		if op == 1:
			dt2 = time.mktime(dt1.timetuple()) + dhm

		dt3 = datetime.fromtimestamp(dt2).strftime('%Y-%m-%d %H:%M:%S')

		h_rec_stop_time.text = dt3
		
#Get History Record for editing
	def get_history_record(self, record_id):	
		global session_id
		
	
	
		def result_history_record(req, results):
			self.ids.edit_history_box.clear_widgets(children=None)	
			

			
			
			itm = {}
			for row in results:
				
				print row['id']
				global h_rec_id
				global h_rec_title
				global h_rec_start_time
				global h_rec_start_time_init
				global h_rec_stop_time
				global h_rec_stop_time_init
				global h_rec_note
				
				
				h_rec_start_time_init = row['start_time']
				
				h_rec_stop_time_init = row['stop_time']

				h_rec_id = row['id']
				
				h_rec_title = Button(id=str(row['id']), size_hint=[1, None], background_normal='', background_color=row['color'].split(","), text=row['recorder'])
				
				h_rec_start_time = TextInput(id=str(row['id']), size_hint=[1, None], text=row['start_time'], font_size=self.width * 0.09)

				h_rec_start_time_buttons = BoxLayout(size_hint=[1, None],orientation='horizontal')
				h_rec_start_time_buttons.add_widget(Label(text='Day'))
				h_rec_start_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime0,1,86400)))
				h_rec_start_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime0,0,86400)))
				h_rec_start_time_buttons.add_widget(Label(text='Hour'))
				h_rec_start_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime0,1,3600)))
				h_rec_start_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime0,0,3600)))
				h_rec_start_time_buttons.add_widget(Label(text='Min'))
				h_rec_start_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime0,1,60)))
				h_rec_start_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime0,0,60)))

				datetime_slider_0 = DateTimeSlider0()
				
				h_rec_stop_time = TextInput(id=str(row['id']), size_hint=[1, None], text=row['stop_time'], font_size=self.width * 0.09)
				
				datetime_slider_1 = DateTimeSlider1()

				h_rec_stop_time_buttons = BoxLayout(size_hint=[1, None], orientation='horizontal')
				h_rec_stop_time_buttons.add_widget(Label(text='Day'))
				h_rec_stop_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime1,1,86400)))
				h_rec_stop_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime1,0,86400)))
				h_rec_stop_time_buttons.add_widget(Label(text='Hour'))
				h_rec_stop_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime1,1,3600)))
				h_rec_stop_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime1,0,3600)))
				h_rec_stop_time_buttons.add_widget(Label(text='Min'))
				h_rec_stop_time_buttons.add_widget(Button(text='+', on_release=partial(self.add_dhm_datetime1,1,60)))
				h_rec_stop_time_buttons.add_widget(Button(text='-', on_release=partial(self.add_dhm_datetime1,0,60)))
				
				
				h_rec_note = TextInput(id=str(row['id']), size_hint=[1, None], hint_text='Note', text=row['note'])
				


				self.ids.edit_history_box.add_widget(h_rec_title)
				self.ids.edit_history_box.add_widget(h_rec_start_time)
				self.ids.edit_history_box.add_widget(datetime_slider_0)
				self.ids.edit_history_box.add_widget(h_rec_start_time_buttons)


				self.ids.edit_history_box.add_widget(h_rec_stop_time)
				self.ids.edit_history_box.add_widget(datetime_slider_1)
				self.ids.edit_history_box.add_widget(h_rec_stop_time_buttons)

				self.ids.edit_history_box.add_widget(h_rec_note)


				
			#itm['rec_btn_3'].text = 'test'
			#itm['rec_counter_2'].text = 'test count'

				
		
		req = UrlRequest(
			'http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=get_history_record&record_id='+record_id,
			result_history_record)

#Update History Record
	def update_history_record(self):	
		global session_id
		global h_rec_id
		global h_rec_title
		global h_rec_start_time
		global h_rec_stop_time
		global h_rec_note
		
		upd_start_time = urllib.quote(h_rec_start_time.text.encode('utf8'))
		upd_stop_time = urllib.quote(h_rec_stop_time.text.encode('utf8'))
		upd_note = urllib.quote(h_rec_note.text.encode('utf8'))
		
		
		def result_history_record_update(req, results):
			print 'id:'+str(h_rec_id)
			print h_rec_title.text
			print h_rec_start_time.text
			print h_rec_stop_time.text
			print h_rec_note.text
			
			for row in results:
				#print str(row['login_status'])
				pass
			self.get_history()
			self.ids.sm.current = 'view_history'
						
		
		req = UrlRequest(
			'http://'+working_server_adress+'/bochron_backend/?s='+session_id+'&b=update_history_record&record_id='+str(h_rec_id)+'&start_time='+upd_start_time+'&stop_time='+upd_stop_time+'&note='+upd_note,
			result_history_record_update)		

#Recorder

class RecorderFloatLayout(FloatLayout):
	pass



#Buttons
class RecorderButton(Button):
	pass
	
class HistoryButton(Button):
	pass	

class ItemAmountButton(Button):
	pass

class UserSelectButton(Button):
	pass
	
class DateTimeSlider0(Slider):
	pass	

class DateTimeSlider1(Slider):
	pass

class LoginButton(Button):
	pass

#Inputs
class PasswordInput(TextInput):
	pass

#App
class ControllerApp(App):
	
	def build(self):
		self.title = 'bochron 15.02b'
		
#Screens		

#		s = Screen(name='Login')
#		s.add_widget(Label(text='Server'))
#		s.add_widget(Label(text='Server'))
#		s.add_widget(Label(text='Server'))
#		self.root.ids.sm.add_widget(s)

#Init		
		#self.root.ids.buttons.add_widget(ItemAmountButton(text='login_user'))
		
		if store.exists('settings'):
			self.root.ids.kv_server_adress.text = store.get('settings')['server_adress']
			

		return self.root
	

	
	def on_pause(self):
		return True

	def on_resume(self):
		pass		
		
		
if __name__ == '__main__':
    ControllerApp().run()
