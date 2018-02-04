import mcpi.minecraft as minecraft
from mcpi.block import *
from mcturtle import *
import code
import time
import sys
import SpeechToText as Spt
from MineCraftInterpreter import process_instruction
import argparse
from ImportantCoordinates import load_location_dict, add_location_to_database
import os
sys.path.append('.')

# Get the specified input method
parser = argparse.ArgumentParser(description='Specifies options (Voice Input or Text Input) for command input.')
parser.add_argument('--input', dest='input_method', default='text', help='Specify the input method that will be used \
 (default: text)', choices=['voice', 'text'])
args = vars(parser.parse_args())
input_method = args['input_method']


commands = {'build', 'move', 'turn', 'save', 'go'}

sd = Spt.SpeechDetector()
sd.setup_mic()

# Load my saved locations
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
important_locations = load_location_dict(os.path.join(__location__, 'important_locations.txt'), {})


def execute_instruction(instruction):
	# get dictionary for command and arguments
	instruction_dict = process_instruction(instruction)
	mc.postToChat(instruction_dict)

	if instruction_dict['command'] is None:
		return 'No command was recognized'
	elif instruction_dict['command'] not in commands:
		return "The recognized command " + instruction_dict['command'] + " is not supported by the system"

	# orient player to match turtle
	t.goto(mc.player.getPos().x, mc.player.getPos().y, mc.player.getPos().z)
	t.angle(mc.player.getRotation())

	if instruction_dict['command'] == 'move':
		t.penup()
		if instruction_dict['direction'] == 'backward' or instruction_dict['direction'] == 'back':
			t.right(180)
		elif instruction_dict['direction'] is 'left':
			t.left(90)
		elif instruction_dict['direction'] is 'right':
			t.right(90)
		if len(instruction_dict['dimensions']) == 0:
			return 'Please specify the number of steps the player should move'
		t.go(instruction_dict['dimensions'][0])
		return 'executed'
	elif instruction_dict['command'] == 'go':
		coordinates = important_locations[instruction_dict['location_name']]
		t.goto(coordinates[0], coordinates[1], coordinates[2])
		# mc.postToChat(important_locations[instruction_dict['location_name']])
		return 'executed'
	elif instruction_dict['command'] == 'build':
		t.gridalign()
		comms = instruction_dict['dimensions']
		pos = mc.player.getPos()
		x = pos.x
		y = pos.y
		z = pos.z
		block_code = instruction_dict['blockCode']
		mc.setBlocks(x, y, z, x+comms[0], y+comms[1], z+comms[2], block_code)
		if instruction_dict['house'] is False:
			return 'executed'
		elif instruction_dict['house'] is True:
			x += 1
			y += 1
			z += 1
			comms[0] -= 2
			comms[1] -= 2
			comms[2] -= 1
			mc.setBlocks(x, y, z, x+comms[0], y+comms[1], z+comms[2], 0)
		return 'executed'
	elif instruction_dict['command'] == 'turn':
		if instruction_dict['direction'] == 'backward' or instruction_dict['direction'] == 'back':
			t.right(180)
		elif instruction_dict['direction'] is 'left':
			t.left(90)
		elif instruction_dict['direction'] is 'right':
			t.right(90)
		return 'executed'
	elif instruction_dict['command'] == 'save':
		coordinates = [int(mc.player.getPos().x), int(mc.player.getPos().y), int(mc.player.getPos().z)]
		important_locations[instruction_dict['location_name']] = coordinates
		add_location_to_database(instruction_dict['location_name'], coordinates, os.path.join\
			(__location__, 'important_locations.txt'))
		return 'executed'
	else:
		return 'Command is not supported'


def quit_mod():
	sys.exit()


def input_line(prompt):
	mc.events.clearAll()
	#mc.postToChat(important_locations)
	while True:
		response = None
		if input_method == 'voice':
			input_message = sd.run()
			mc.postToChat(input_message)
			response = execute_instruction(input_message)
		else:
			chats = mc.events.pollChatPosts()
			for c in chats:
				if c.entityId == playerId:
					if c.message == 'quit':
						return 'quit()'
					elif c.message == ' ':
						return ''
					elif "__" in c.message:
						sys.exit()
					else:
						mc.postToChat(c.message)
						response = execute_instruction(c.message)
						#mc.postToChat(important_locations)
		if response == 'executed':
			mc.postToChat('executed')
			pass
		elif response is not None:
			mc.postToChat(response)
		time.sleep(0.2)


mc = minecraft.Minecraft()
playerPos = mc.player.getPos()
playerId = mc.getPlayerId()
t = Turtle(mc)

mc.postToChat("Enter python code into chat, type 'quit' to quit.")
i = code.interact(banner="", readfunc=input_line, local=locals())
