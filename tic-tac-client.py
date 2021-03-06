#!/usr/bin/env python
#coding: utf-8

"""
It's a client for Tic Tac Toe game.

Usecase: run it after server's started.
"""

from __future__ import print_function
import tic_tac_common as ttc

import socket
import sys
import os
import readline
import json, re, copy
import argparse

# ---------------------------------------------------------------------------- #


def main():

	s = ttc.get_client_socket()

	try:
		# get hello
		hello_msg = ttc.get_msg_from_socket(s)
		print("\n{0}\n".format(hello_msg))

		print('''
You are a cross (X).
Enter coordinats, where to put next cross.
Suppose, left top corner is (0, 0).
Input in format: <int> <int> <hit Return>
''')
		gf = copy.deepcopy(ttc.GAME_FIELD)
		ttc.print_game_field(gf)

		### loop for a game, untill winner or ^C
		while True:


			#B get a step from user
			turn_json = ttc.get_turn_from_user(gf)


			#B send step to the server
			s.sendall(turn_json.encode('utf-8'))


			#B get server answer about user step
			res = ttc.get_msg_from_socket(s, exception=False, ex=True)


			# if error - ask step again
			if is_error_in_answer(res):
				print("Ou, server not pleasent about your answer, try again.\n")
				continue;
			else:
				ttc.apply_turn(turn_json, gf, ttc.USER_RAW_STEP)
				ttc.print_game_field(gf)


			# check for winners in the answer, if exist any - game ends.
			handle_winner_variable(res)


			#B get server step
			print("Wait for server response...")
			server_step = ttc.get_msg_from_socket(s)
			ttc.d("server step: {0}\n".format(server_step))
			ttc.apply_turn(server_step, gf, ttc.SERVER_RAW_STEP)
			handle_winner_variable(server_step)

			ttc.print_game_field(gf)


	except KeyboardInterrupt as k:
		print ("\nShutting down... {0}".format(k))
	except Exception as exp:
		print(": {0}".format(exp))
		ttc.print_game_field(gf)
	except:
		print("Unexpected error:", sys.exc_info()[0])


	s.close()
	sys.exit(0)


# --------------------------------------------------------------------------- #
# ------------------------------- H E L P E R S ----------------------------- #
# --------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #

def is_error_in_answer (msg):
	"""
	Check for error field in @msg.

	@param
		msg --- string in json format

	@return
		True, if field exist and it's 1
		False otherwise
	"""

	try:
		ttc.d("your step validation: {0}".format(msg))
		tmp = json.loads(msg)

		if tmp["error"] == 1:
			return True

	except Exception as exp:
		print("error, {0}".format(exp))
		return False

# --------------------------------------------------------------------------- #

def handle_winner_variable (res):
	""" Function doc """

	try:
		tmp = json.loads(res)
		winner = tmp["Wow - You are the Winner"]

		if 0 == winner :
			pass
		elif 1 == winner:
			raise Exception("Sorry, but you lost... =\\")
		elif 2 == winner:
			raise Exception("You win!")
		elif 3 == winner:
			raise Exception("Tie! (tie)")
		else:
			print("unexpected value")

	except (KeyError, TypeError) as e:
		ttc.d(e)

# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
	"""
	debug : to enable/disable debug
	host  : where server is located (ip/host)
	port  : the port, on which server listen for incomming connections
	"""

	parser = argparse.ArgumentParser(description='Run a client for Tic-Tac-toe client-server game.')

	parser.add_argument('--host',       help='specify host/ip, where server is running')
	parser.add_argument('-p', '--port', help='specify a port to connect to',
					type=int)
	parser.add_argument('--debug', help='show debug output', action='store_true')

	args = parser.parse_args()

	if args.debug:
		ttc.DEBUG = 1
		print("Debug output: On")

	if args.host is not None:
		ttc.SERVER_IP = args.host
	if args.port is not None:
		ttc.SERVER_PORT = args.port


	main()
