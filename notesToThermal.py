from escpos import *
import gkeepapi, keyring, shutil, time, yaml

class ThermalPrinter():
	def __init__(self):
		self.epson = printer.Usb(0x04B8, 0x0202) # WinUSB Port IDs of Epson M224A
		self.maxCharPerLine = 42 # The maximum characters per line that will fit on Epson TM-T88V
		self.footer = 'Generated: %NOW%\nhttps://github.com/ijjy303/googleNotesToThermal'

	def cut(self):
		self.epson.cut()

	def printBarcode(self, code=''):
		if code == '':
			raise ValueError('Barcode was not supplied!')
		typeCode = type(code)

		if typeCode is not int and typeCode is not str:
			raise ValueError('Barcode is not valid int() or str() type!')
		else:
			code = str(code)

		if len(code) < 13:
			raise ValueError('Barcode Too Short!...')
		else:
			self.epson.barcode(code, 'EAN13', 64, 2, '', '')

		self.cut()

	def printImage(self, img='img.jpg'): # Really need to crop/resize image to paper dimensions...
		self.epson.image(img)
		self.cut()

	def printText(self, content, header=True, footer=True, ordered=None):
		""" Efficiently print to-do/grocery list. ie:
		One line contains maximum characters without spreading single checkbox, bullet or string onto multiple lines
		"""
		if header == True: # Note input argument has a title
			title = content[0]
			noteLines = content[-1].strip().split('\n')
		
		else: # Do not include a title/header
			print(content)
			noteLines = content[-1].strip().split('\n')
		
		formattedNote = ''
		lineCounter = 0

		for line in noteLines:
			printerLine = formattedNote.split('\n')[lineCounter]
			lineBuffer = len(printerLine) + len(line) # Get current character length of both printer line and note line
			if lineBuffer <= self.maxCharPerLine:
				if lineBuffer == self.maxCharPerLine: # Line full, next iteration *will* start with \n
					formattedNote += line # Line has max chars, do not add space/exceed line buffer.
				else:  # Add space between checkboxes in case next iteration is on same line.
					formattedNote += f'{line} '
			else: # Line buffer exceeded, start new printer line.
				formattedNote += f'\n{line} '
				lineCounter += 1

		if header == True: # After formatting content of note, prefix with title
			formattedNote = f'{title}\n{formattedNote}'

		if footer == True:
			from datetime import datetime as dt
			formattedNote += self.footer.replace('%NOW%', f'{dt.now().strftime("%m.%d.%Y @ %H:%M:%S")}')

		print('Note reformatted to maximum efficiency.\nPrinting...')
		print(formattedNote)
		self.epson.text(formattedNote)
		self.cut()
		return True

class KeepNotes():
	def __init__(self):
		keep = gkeepapi.Keep()
		
		with open('keepConfig.yml', 'r') as y:
			keepConfig = yaml.safe_load(y)

		user = keepConfig['user']
		pswd = keepConfig['pswd']
		
		if user == '' or pswd == '':
			raise ValueError('Missing login credentials...')

		self.imageFormat = '.jpg'
		self.keep = keep
		self.catBorderL = '--------------'#'--------{---(@'
		self.catBorderR = '--------------'#'@)---}--------' 
		# Below example needs to be imported from a json file using json library. Multiple jsons, mulitple stores.
		self.storeAisles = keepConfig['grocery-store']

		try: # Try resuming previous API session using token....
			print('Attemping to use previous login token...')
			token = keyring.get_password('google-keep-token', user)
			keep.resume(user, token)
		
		except: # Token not present or old, create a new token...
			print('Logging in...')
			success = keep.login(user, pswd)
			token = keep.getMasterToken()
			keyring.set_password('google-keep-token', user, token)
	
	def noteFound(self, notes): # Determines if note search function has matched on a note or not.
		if notes in [[], None, [None]]: # If note object is variation of empty None value...
			return False # Note not found
		else:
			return True # Note found!

	def findNoteID(self, ID): # Find note by ID (url suffix), otherwise throw error if no match found.
		notes = self.keep.get(ID) # get(ID) returns as contents of note as opposed to object array, so...
		if self.noteFound(notes) == True:
			return [notes] # Return as array
		else:
			raise ValueError(f'Could not find ID "{ID}"')

	def findNoteKeyword(self, keyword): # Find notes that contain keyword, otherwise throw error if no match found.
		notes = self.keep.find(query=keyword) # find() returns objects
		notes = [x for x in notes] # put objects into array

		if self.noteFound(notes) == True:
			return notes # return array
		else:
			raise ValueError(f'Note with keyword "{keyword}" not found.')

	def findNoteLabeled(self, label): # Find Note by label identifier, otherwise throw error if no match found.
		findLabel = self.keep.findLabel(label) # Find label
		notes = self.keep.find(labels=[findLabel]) # Find notes with label
		notes = [x for x in notes]

		if self.noteFound(notes) == True:
			return notes
		else:
			raise ValueError(f'Note with label "{label}" not found.')

	def searchFor(self, *args, **kwargs): # One function to search all Google Notes by 3 identifiers. id, keyword, label.
		args = args[0]
		argument = list(args.keys())[0]
		argumentVal = list(args.values())[0]

		try:
			if argument == 'label':
				notes = self.findNoteLabeled(label=argumentVal)
		
			elif argument == 'ID':
				notes = self.findNoteID(ID=argumentVal)
		
			elif argument == 'keyword':
				notes = self.findNoteKeyword(keyword=argumentVal)

			return notes

		except: # Either argument that was passed is invalid or note matching search criteria failed.
			if argument not in ['ID', 'keyword', 'label']:
				raise ValueError(f'Invalid "{argument}" argument. Search arguments include: ID, keyword, label')
			else:
				raise ValueError('Note search unsuccessful. Try swiping down to refresh Google Notes App...')

	def saveUrlToImg(self, url=None, name=f'default.jpg'): # Use requests and shutil to download img from url and save to file.
		import requests
		response = requests.get(url, stream=True)
		with open(name, 'wb') as outFile:
		    shutil.copyfileobj(response.raw, outFile)
		del response

	def downloadImage(self, *args, **kwargs): # Find note by identifier, download and save all attached pictures
		notes = self.searchFor(kwargs)
		
		images = [] # Array of all image urls
		for note in notes: # For each note...
			for x, img in enumerate(note.images):
				image = note.images[x] # Get all images indexed in note
				url = self.keep.getMediaLink(image) # Get url for each image...
				images.append(url) # Append image url to array

		for x, url in enumerate(images): # For each image in array...
			name = f'{x}{self.imageFormat}' # Establish name for image based on enumeration. ie: 1.jpg, 2.jpg, etc...
			print(f'Saving image: {name}...')
			self.saveUrlToImg(url=url, name=name) # Use requests and shutil libraries to convert url to jpg

	def deleteNoteBy(self, *args, **kwargs): # Delete note matching specified id, keyword or label.
		notes = self.searchFor(kwargs)
		for note in notes:
			print('Deleting note...')
			note.delete()
		#self.keep.sync() # Have to sync with Google, otherwise no changes will be made.

	def createOrganizedCopy(self, *args, **kwargs):
		notes = self.getNotesWith(label=kwargs['label'], ordered='grocery') # Need to make this dynamic later (take, label, ID, etc...)

		for note in notes:
			orgNote = []
			for line in note[-1].split('\n'):
				if '[ ]' in line:
					line = line.replace('[ ]', '')
					line = tuple((line, False))
					orgNote.append(line)
				else:
					line = line.replace('-----', '')
					line = tuple((line, False))
					orgNote.append(line)

			self.keep.createList(note[0], orgNote)
			print('Organize note and created it...')

	def getNotesWith(self, ordered=None, *args, **kwargs):
		notes = self.searchFor(kwargs)
		
		noteBlobs = []
		for note in notes:
			noteTitle = note.title
			note = f'{note.text}'.replace('☐', '[ ]') # replace any checkbox unicode characters with regular brackets
			noteBlobs.append([noteTitle, note])
		
		if ordered == 'grocery': # If ordered specified as grocery, reorganize grocery list according to aisle. ie: Most efficient buying route
			for note in noteBlobs:
				groceries = note[-1].replace('[ ] ', '').split('\n') # [-1] References the content (not title) of note, reduce list strings to item names
				groceries = [x.strip().lower() for x in groceries] # Remove trailing \n chars. Leaving lowercase values without check boxes, fluff, etc...
				basket = {} # Create a dictionary, corresponding to the final 'basket'

				for lotion in groceries:
					basket[lotion] = 'None-Misc' # Fill up the dict basket with items. All items start with None-Misc location value

				for aisle in self.storeAisles: # For each aisle in json/dict
					for item, location in basket.items(): # Get each item and location in basket
						if item in self.storeAisles[aisle] and location == 'None-Misc':  # If basket item found in json aisle..
							basket[item] = aisle # assign known aisle to basket item location
				sortBasket = sorted(basket.items(), key=lambda x: (x[1], x[0])) # Sort by aisle, then alphabetically for optimal buying route and visual reference

				items = []
				aisleCounter = 0 # Counter to determine which aisle we're one
				for item, location in sortBasket:
					location = location.split('-')[1]
					if location == aisleCounter:
						items.append(f'[ ] {item.capitalize()}\n') # Add item to note blob
					else: # Location of item is different...
						aisleCounter = location # update aisle counter to current aisle.
						items.append(f'{self.catBorderL} Aisle: {location} {self.catBorderR}\n[ ] {item.capitalize()}\n') # Label each part of the note with respective aisle.
				
				note.pop(-1) # Remove old list
				note.append(''.join(items)) # Append new list smooshed into a single string
		
		#print(noteBlobs)
		return noteBlobs # Returns as 2D array because their may be multiple notes

	def removeLabel(self, rmLabel=None, *args, **kwargs): # Can only remove one label at a time for now...
		notes = self.searchFor(kwargs)

		argument = list(kwargs.keys())[0]
		argumentVal = list(kwargs.values())[0] # Arguments passed in label as string	

		try:
			label = self.keep.findLabel(rmLabel)
			for note in notes:
				note.labels.remove(label)
				print('Label removed...')

		except: # If label was not specified in any way...
			if argument == 'label' and rmLabel == None: # Try to find discern label from arguments.
				label = self.keep.findLabel(argumentVal)
				for note in notes:
					note.labels.remove(label)
					print('Label removed...')
			
			elif argument != 'label' and rmLabel != None: # Label not passed in argument. Cannot derive label value from note identifier...
				raise ValueError(f'Label "{rmLabel}" not found....')
			
			else:
				raise ValueError(f'Label not defined in argument.\nI even tried to check the note identifier for you.\nYou failed.')

		return True

	def sync(self):
		self.keep.sync()

if __name__ == '__main__':
	tp = ThermalPrinter()
	kn = KeepNotes()
	notes = kn.getNotesWith(label='print-me', ordered='grocery')
	[tp.printText(note) for note in notes]
