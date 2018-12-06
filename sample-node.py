# header files
import socket
import sys
import threading
from threading import Thread
import socketserver
import os
import time
import random
from random import randint

# set global variables
NID = 0
hostname = ' '
udp_port = 0
tcp_port = 0
l1_NID = 0
l2_NID = 0
l3_NID = 0
l4_NID = 0
l1_hostname = ' '
l2_hostname = ' '
l3_hostname = ' '
l4_hostname = ' '
l1_udp_port = 0
l2_udp_port = 0
l3_udp_port = 0
l4_udp_port = 0
l1_tcp_port = 0
l2_tcp_port = 0
l3_tcp_port = 0
l4_tcp_port = 0

# global variable to track time since
# last connection
l1_last_connection = time.time()
l2_last_connection = time.time()
l3_last_connection = time.time()
l4_last_connection = time.time()

# create node object variable
node = None

# function: InitializeTopology
def InitializeTopology (nid, itc):

	# global variables
	global node

	# initialize node object
	node = Node(int(nid))

	# open itc.txt file and read to list
	infile = open(itc)
	list = infile.readlines()

	# initialize lists for hostnames and port numbers
	hostnames = []
	ports = []

	# populate hostname and port lists
	for entry in list:
		temp = entry.split(' ')
		hostnames.append(temp[1])
		ports.append(int(temp[2]))

	# use list to populate LinkTable and PortTable
	for entry in list:
		temp = entry.split(' ')
		node.Set_link_table(int(temp[0]), (int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6])))
		node.Set_address_data_table(int(temp[0]), temp[1], int(temp[2]))

		# set parameters for for this node
		if node.GetNID() == int(temp[0]):
			node.SetHostName(temp[1])
			node.SetPort(int(temp[2]))

			# set starting point
			number_of_nodes = len(temp) - 3
			index = 3

			# iterate through and add all links for this node
			for i in range(number_of_nodes):
				corresponding_hostname = hostnames[int(temp[index+i])-1]
				corresponding_port = ports[int(temp[index+i])-1]
				node.AddLink((int(temp[index+i]), corresponding_hostname, corresponding_port))

	# close itc.txt file
	infile.close()

	# return object
	return node

# class: llnode
# the objects to be used in the linked list
# containing shortest path and number of hops
class llnode(object):

	def __init__ (self, nid=0, hops=0, next_node=None):
		self.nid = nid
		self.hops = hops
		self.next_node = next_node

	def get_nid (self):
		return self.nid

	def get_next (self):
		return self.next_node

	def set_next (self, new_next):
		self.next_node = new_next

	def get_hops (self):
		return self.hops

	def set_hops (self, new_hops):
		self.hops = new_hops

# class: LinkedList for llnode
class LinkedList (object):
	def __init__ (self, head=None):
		self.head = head

	def gotoEnd(self):
		current = self.head
		if current:
			while current.get_next() is not None:
				current = current.get_next()
			return current
		else:
			return self.head
	
	# New insert function (new inserts at tail)
	def insert (self, nid, hops):
		new_node = llnode(int(nid), int(hops))
		if self.head is None:
			self.head = new_node
		else:
			temp = self.gotoEnd()
			temp.set_next(new_node)

	def search (self, nid):
		current = self.head
		while current is not None:
			if current.get_nid() == int(nid):
				break
			else:
				current = current.get_next()
		# current will be None if not found
		return current

	def delete (self, nid):
		current = self.head
		previous = None
		found = False
		while current and found is False:
			if current.get_nid() == int(nid):
				found = True
			else:
				previous = current
				current = current.get_next()
		if previous is None:
			self.head = current.get_next()
		else:
			previous.set_next(current.get_next())

# class: Node
class Node(object):

	# initialize node
	def __init__ (self, nid=0, host_name=None, udp_port=0, links=[], address_data_table = [], link_table={}):
		self.nid = nid
		self.host_name = host_name
		self.udp_port = udp_port

		if links is not None:
			self.links = list(links)

		self.upL1 = False
		self.upL2 = False
		self.upL3 = False
		self.upL4 = False
		self.link_table = {}
		self.address_data_table = {}
    
	# get nid
	def GetNID (self):
		return self.nid

	# get hostname
	def GetHostName (self):
		return self.host_name

	# get port number
	def GetPort (self):
		return self.udp_port

	# get list of links
	def GetLinks (self):
		return self.links

	# get link table (all links)
	def Get_link_table (self):
		return self.link_table

	# get port table (all ports)
	def Get_address_data_table (self):
		return self.address_data_table

	# get up flag for neighbor 1
	def GetUpFlagL1 (self):
		return self.upL1

	# get up flag for neighbor 2
	def GetUpFlagL2 (self):
		return self.upL2

	# get up flag for neighbor 1
	def GetUpFlagL3 (self):
		return self.upL3

	# get up flag for neighbor 2
	def GetUpFlagL4 (self):
		return self.upL4    

	# set up flag for neighbor 1
	def SetUpFlagL1 (self, flag):
		self.upL1 = flag

	# set up flag for neighbor 2
	def SetUpFlagL2 (self, flag):
		self.upL2 = flag

	# set up flag for neighbor 1
	def SetUpFlagL3 (self, flag):
		self.upL3 = flag

	# set up flag for neighbor 2
	def SetUpFlagL4 (self, flag):
		self.upL4 = flag

	# set nid
	def SetNID (self, nid):
		self.nid = nid

	# set hostname
	def SetHostName (self, host_name):
		self.host_name = host_name

	# set port number
	def SetPort (self, udp_port):
		self.udp_port = udp_port

	# add link to links list
	def AddLink (self, individual_link):
		self.links.append(individual_link)

	# set link table
	def Set_link_table (self, source_nid, neighbor_nid):
		self.link_table[source_nid] = neighbor_nid
		#pass

	# set port table
	def Set_address_data_table (self, nid, hostname, port):
		self.address_data_table[nid] = nid, hostname, port

# function NodeTimeUpdate (update variable tracking last activity for a node)
def NodeTimeUpdate(node_id, new_time):

	# global variables
	global l1_NID, l2_NID, l3_NID, l4_NID
	global l1_last_connection, l2_last_connection, l3_last_connection, l4_last_connection

	if(node_id == l1_NID):
		# Connection from 1st NID
		l1_last_connection = new_time
	elif(node_id == l2_NID):
		# Connection from 2nd NID
		l2_last_connection = new_time
	elif(node_id == l3_NID):
		# Connection from 3rd NID
		l3_last_connection = new_time
	elif(node_id == l4_NID):
		# Connection from 4th NID
		l4_last_connection = new_time

# function TimeOutObserver (mark nodes as disconnected or reconnected)
def TimeOutObserver():
	
	# global variables
	global l1_last_connection, l2_last_connection, l3_last_connection, l4_last_connection
	global linked1, linked2, linked3, linked4
	
	# Give time for links to propagate
	time.sleep(10)

	while 1:
		currentTime = time.time()

		# Check link 1
		if(currentTime - l1_last_connection > 10):
			# Set node hop to 0 (disconnected)
			linked1.head.set_hops(0)
		else:
			# Set node hop to 1 (re-connected)
			linked1.head.set_hops(1)
		
		# Check link 2
		if(currentTime - l2_last_connection > 10):
			# Set node hop to 0 (disconnected)
			linked2.head.set_hops(0)
		else:
			# Set node hop to 1 (re-connected)
			linked2.head.set_hops(1)
		
		# Check link 3
		if(currentTime - l3_last_connection > 10):
			# Set node hop to 0 (disconnected)
			linked3.head.set_hops(0)
		else:
			# Set node hop to 1 (re-connected)
			linked3.head.set_hops(1)
		
		# Check link 4
		if(currentTime - l4_last_connection > 10):
			# Set node hop to 0 (disconnected)
			linked4.head.set_hops(0)
		else:
			# Set node hop to 1 (re-connected)
			linked4.head.set_hops(1)

		# Only poll every second
		time.sleep(1)

# class TCP Handler (this receives all TCP messages)
class MyTCPHandler(socketserver.BaseRequestHandler):	

	def handle(self):

		# global variables
		global NID, hostname, tcp_port
		global l1_hostname, l2_hostname, l3_hostname, l4_hostname
		global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
		global l1_NID, l2_NID, l3_NID, l4_NID
		global add_counter, update_counter, remove_counter

		self.data = self.request.recv(1024)
		message = self.data
		message = ''.join(message.decode().split())
		
		# Split actual message from headers
		SplitMsg = message.split('%20')
		DestFlag = int(SplitMsg[0])
		SourceNode = int(SplitMsg[1])
		message = SplitMsg[2]

		if(DestFlag == 0):
			# Propagation
			NodeTimeUpdate(SourceNode, time.time())
			LinkDataRecv(SourceNode, message)

		elif(DestFlag == NID):
			print(message)
			#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")	

		else:
			send_tcp(DestFlag, message)

# Class: MyUDPHandler (this receives all UDP messages)
class MyUDPHandler(socketserver.BaseRequestHandler):

	# interrupt handler for incoming messages
	def handle(self):

		# parse received data
		data = self.request[0].strip()

		# set message and split
		message = data
		message = ''.join(message.decode().split())
		
		# Split actual message from headers
		SplitMsg = message.split('%20')
		DestFlag = int(SplitMsg[0])
		SourceNode = int(SplitMsg[1])
		message = SplitMsg[2]

		if(DestFlag == NID):
			print(message)
			#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")			
		
		else:
			send_udp(DestFlag, message)

# Function: sendto()
def send_tcp(dest_nid, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID

	# Add destination ID and current node ID to message
	message = str(dest_nid) + '%20' + str(NID) + '%20' + message

	# look up address information for the destination node
	if linked1.search(dest_nid) is not None:
		if(linked1.head.get_hops() != 0):
			HOST = l1_hostname
			PORT = l1_tcp_port

	elif linked2.search(dest_nid) is not None:
		if(linked2.head.get_hops() != 0):
			HOST = l2_hostname
			PORT = l2_tcp_port

	elif linked3.search(dest_nid) is not None:
		if(linked3.head.get_hops() != 0):
			HOST = l3_hostname
			PORT = l3_tcp_port

	elif linked4.search(dest_nid) is not None:
		if(linked4.head.get_hops() != 0):
			HOST = l4_hostname
			PORT = l4_tcp_port

	else:
		print('no address information for destination')

	# encode message as byte stream
	message = message.encode()

	# send message
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				
		sock.connect((HOST, PORT))
		sock.sendall(message)
		sock.close()

	except:
		print('error, message not sent')
		pass

# function: hello (alive)
def send_udp(dest_nid, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID

	# Add destination ID and current node ID to message
	message = str(dest_nid) + '%20' + str(NID) + '%20' + message

	if linked1.search(dest_nid) is not None:
		if(linked1.head.get_hops() != 0):
			HOST = l1_hostname
			PORT = l1_udp_port

	elif linked2.search(dest_nid) is not None:
		if(linked2.head.get_hops() != 0):
			HOST = l2_hostname
			PORT = l2_udp_port

	elif linked3.search(dest_nid) is not None:
		if(linked3.head.get_hops() != 0):
			HOST = l3_hostname
			PORT = l3_udp_port

	elif linked4.search(dest_nid) is not None:
		if(linked4.head.get_hops() != 0):
			HOST = l4_hostname
			PORT = l4_udp_port

	else:
		print('no address information for destination')

	# encode message as byte stream
	message = message.encode()

	try:
		# open socket and send to neighbor 4
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
		sock.sendto(message, (HOST, PORT))
	except:
		print('error, message not sent')			
		pass

# function: start listener
def start_listener():

	# global variables
	global node, NID, hostname, udp_port, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_udp_port, l2_udp_port, l3_udp_port, l4_udp_port
	global l1_tcp_port, l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID

	# linked list of connected networks
	global linked1, linked2, linked3, linked4

	# check links for node attributes
	links = node.GetLinks()
	link1 = links[0]
	link2 = links[1]
	link3 = links[2]
	link4 = links[3]

	# set link attributes
	l1_NID = link1[0]
	l1_hostname = link1[1]
	l1_udp_port = link1[2]
	l1_tcp_port = l1_udp_port + 500

	l2_NID = link2[0]
	l2_hostname = link2[1]
	l2_udp_port = link2[2]
	l2_tcp_port = l2_udp_port + 500

	l3_NID = link3[0]
	l3_hostname = link3[1]
	l3_udp_port = link3[2]
	l3_tcp_port = l3_udp_port + 500

	l4_NID = link4[0]
	l4_hostname = link4[1]
	l4_udp_port = link4[2]
	l4_tcp_port = l4_udp_port + 500

	hostname = node.GetHostName()
	NID = node.GetNID()
	udp_port = node.GetPort()
	tcp_port = udp_port + 500

	# Create the linked lists and insert first node
	linked1 = LinkedList()
	linked1.insert(l1_NID, 1)
	linked2 = LinkedList()
	linked2.insert(l2_NID, 1)
	linked3 = LinkedList()
	linked3.insert(l3_NID, 1)
	linked4 = LinkedList()
	linked4.insert(l4_NID, 1)

	# slight pause to let things catch up
	time.sleep(2)

	# start thread for listener
	t1 = threading.Thread(target=TCP_listener)
	t1.daemon = True
	t1.start()

	# start thread for listener
	t2 = threading.Thread(target=UDP_listener)
	t2.daemon = True
	t2.start()

	# start thread for linked information propagation
	t3 = threading.Thread(target=LinkDataSend)
	t3.daemon = True
	t3.start()


	# start thread for node time activity observation
	t4 = threading.Thread(target=TimeOutObserver)
	t4.daemon = True
	t4.start()

# function: TCP listener
def TCP_listener():

	# global variables
	global hostname, tcp_port

	# set socket for listener
	server = socketserver.TCPServer((hostname, tcp_port), MyTCPHandler)
	server.serve_forever()

# function: receiver (listener)
def UDP_listener():

 	# global variables
	global hostname, udp_port

	# set socket for listener
	server = socketserver.UDPServer((hostname, udp_port), MyUDPHandler)
	server.serve_forever()

# function: Link propagation
def LinkDataSend():

	# global variables
	global NID
	global linked1, linked2, linked3, linked4

	while 1:
		time.sleep(5)
		if(l1_NID != 0):
			if(linked1.head.get_hops() != 0):
				message = str(0) + '%20' + str(NID) + '%20' + convert_linked_to_str(linked2) + convert_linked_to_str(linked3) + convert_linked_to_str(linked4)
				print("to node" + str(l1_NID))
				print(message)
				DebugLinkTCP(l1_NID, message)
		if(l1_NID != 0):
			if(linked2.head.get_hops() != 0):
				message = str(0) + '%20' + str(NID) + '%20' + convert_linked_to_str(linked1) + convert_linked_to_str(linked3) + convert_linked_to_str(linked4)
				print("to node" + str(l2_NID))
				print(message)
				DebugLinkTCP(l2_NID, message)
		if(l1_NID != 0):
			if(linked3.head.get_hops() != 0):
				message = str(0) + '%20' + str(NID) + '%20' + convert_linked_to_str(linked1) + convert_linked_to_str(linked2) + convert_linked_to_str(linked4)
				print("to node" + str(l3_NID))
				print(message)
				DebugLinkTCP(l3_NID, message)
		if(l1_NID != 0):
			if(linked4.head.get_hops() != 0):
				message = str(0) + '%20' + str(NID) + '%20' + convert_linked_to_str(linked1) + convert_linked_to_str(linked2) + convert_linked_to_str(linked3)
				print("to node" + str(l4_NID))
				print(message)
				DebugLinkTCP(l4_NID, message)

# Function to handle recieving data
def LinkDataRecv(sourceNode, message):

	# print("Link data recieved from node:", end = ' ')
	# print(sourceNode)
	global linked1, linked2, linked3, linked4

	if(sourceNode == l1_NID and l1_NID != 0):
		index_counter = 0
		while index_counter < len(message):
			if message[index_counter] == NID:
				index_counter += 2
			if linked1.search(message[index_counter]) is not None:
				# Replace
				temp_node = linked1.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					temp_node.set_hops(temp_val)
			elif linked2.search(message[index_counter]) is not None:
				temp_node = linked2.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked2.delete(int(message[index_counter]))
					linked1.insert(message[index_counter], temp_val)
			elif linked3.search(message[index_counter]) is not None:
				temp_node = linked3.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked3.delete(int(message[index_counter]))
					linked1.insert(message[index_counter], temp_val)
			elif linked4.search(message[index_counter]) is not None:
				temp_node = linked4.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked4.delete(int(message[index_counter]))
					linked1.insert(message[index_counter], temp_val)
			else:
				temp_val = int(message[index_counter + 1]) + 1
				linked1.insert(message[index_counter], temp_val)
			index_counter += 2
	elif(sourceNode == l2_NID and l2_NID != 0):
		index_counter = 0
		while index_counter < len(message):
			if linked2.search(message[index_counter]) is not None:
				# Replace
				temp_node = linked2.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					temp_node.set_hops(temp_val)
			elif linked1.search(message[index_counter]) is not None:
				temp_node = linked1.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked1.delete(int(message[index_counter]))
					linked2.insert(message[index_counter], temp_val)
			elif linked3.search(message[index_counter]) is not None:
				temp_node = linked3.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked3.delete(int(message[index_counter]))
					linked2.insert(message[index_counter], temp_val)
			elif linked4.search(message[index_counter]) is not None:
				temp_node = linked4.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked4.delete(int(message[index_counter]))
					linked2.insert(message[index_counter], temp_val)
			else:
				temp_val = int(message[index_counter + 1]) + 1
				linked2.insert(message[index_counter], temp_val)
			index_counter += 2
	elif(sourceNode == l3_NID and l3_NID != 0):
		index_counter = 0
		while index_counter < len(message):
			if linked3.search(message[index_counter]) is not None:
				# Replace
				temp_node = linked3.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					temp_node.set_hops(temp_val)
			elif linked2.search(message[index_counter]) is not None:
				temp_node = linked2.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked2.delete(int(message[index_counter]))
					linked3.insert(message[index_counter], temp_val)
			elif linked1.search(message[index_counter]) is not None:
				temp_node = linked1.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked1.delete(int(message[index_counter]))
					linked3.insert(message[index_counter], temp_val)
			elif linked4.search(message[index_counter]) is not None:
				temp_node = linked4.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked4.delete(int(message[index_counter]))
					linked3.insert(message[index_counter], temp_val)
			else:
				temp_val = int(message[index_counter + 1]) + 1
				linked3.insert(message[index_counter], temp_val)
			index_counter += 2
	elif(sourceNode == l4_NID and l4_NID != 0):
		index_counter = 0
		while index_counter < len(message):
			if linked4.search(message[index_counter]) is not None:
				# Replace
				temp_node = linked4.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					temp_node.set_hops(temp_val)
			elif linked2.search(message[index_counter]) is not None:
				temp_node = linked2.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked2.delete(int(message[index_counter]))
					linked4.insert(message[index_counter], temp_val)
			elif linked3.search(message[index_counter]) is not None:
				temp_node = linked3.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked3.delete(int(message[index_counter]))
					linked4.insert(message[index_counter], temp_val)
			elif linked1.search(message[index_counter]) is not None:
				temp_node = linked1.search(message[index_counter])
				temp_val = int(message[index_counter + 1]) + 1
				if temp_node.get_hops() >= temp_val:
					linked1.delete(int(message[index_counter]))
					linked4.insert(message[index_counter], temp_val)
			else:
				temp_val = int(message[index_counter + 1]) + 1
				linked4.insert(message[index_counter], temp_val)
			index_counter += 2

# print status
def PrintInfo():

	# global variables
	global node, NID, hostname, udp_port, tcp_port

	# output data
	#os.system('clear')
	print("NID: " + str(NID))
	print("Link Table: " + str(node.Get_link_table()))
	print("Address Data: " + str(node.Get_address_data_table()))
	#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

def convert_linked_to_str(ll_nodes):
	converted_str = ""
	curr_ptr = ll_nodes.head
	while curr_ptr is not None:
		converted_str = converted_str + str(curr_ptr.get_nid()) #+ "%20"
		converted_str = converted_str + str(curr_ptr.get_hops()) #+ "%20"
		curr_ptr = curr_ptr.get_next()
	return converted_str

# Essentially send_tcp but can be used for propagation
def DebugLinkTCP(dest_nid, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID
	global linked1, linked2, linked3, linked4

	# look up address information for the destination node
	if linked1.search(dest_nid) is not None:
		HOST = l1_hostname
		PORT = l1_tcp_port

	elif linked2.search(dest_nid) is not None:
		HOST = l2_hostname
		PORT = l2_tcp_port

	elif linked3.search(dest_nid) is not None:
		HOST = l3_hostname
		PORT = l3_tcp_port

	elif linked4.search(dest_nid) is not None:
		HOST = l4_hostname
		PORT = l4_tcp_port

	else:
		print('no address information for destination')

	# encode message as byte stream
	message = message.encode()

	# send message
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				
		sock.connect((HOST, PORT))
		sock.sendall(message)
		sock.close()

	except:
		pass

# main function
def main(argv):

	# global variables
	global node, linked1

	# set initial value for loop
	run = 1

	# check for command line arguments
	if len(sys.argv) != 3:
		print("Usage: <program_file> <nid #> <itc#.txt>")
		exit(1)

	# initialize node object
	node = InitializeTopology(sys.argv[1], sys.argv[2])

	# start UDP listener
	start_listener()

	# loop
	while(run):

		#print menu options
		#os.system('clear')
		print("1. Info")
		print("2. Send message to another node via TCP")
		print("3. Send message to another node via UDP")		
		print("4. Quit")
		print("5. Search for a connection to a node and the number of hops required")
		print("6. Show all the nodes than can be reached and the number of hops required")

		# set selection value from user
		selection = input("Enter Selection: ")

		# selection: status
		if selection == '1':
			PrintInfo()

		# selection: send_tcp
		elif(selection == '2'):
			#os.system('clear')
			dest_nid = input("Node #: ")
			message = input("Message: ")
			if "%20" in message:
				print("Error, can't use %20 (We use it for header separation!)")
			else:
				send_tcp(dest_nid, message)
			#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

		# selection: send_udp
		elif(selection == '3'):
			#os.system('clear')
			dest_nid = input("Node #: ")
			message = input("Message: ")
			if "%20" in message:
				print("Error, can't use %20 (We use it for header separation!)")
			else:
				send_udp(dest_nid, message)
			#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")			

		# selection: quit
		elif(selection == '4'):
			run = 0
			#os.system('clear')
		elif(selection == '5'):
			#os.system('clear')
			dest_nid = input("Node #: ")
			if linked1.search(dest_nid):
				print("Node" + str(dest_nid) + " can be reached through neighbor 1, Node " + str(l1_NID))
				print ("It would take " + str(linked1.search(dest_nid).get_hops()) + " hops")
			elif linked2.search(dest_nid):
				print("Node" + str(dest_nid) + " can be reached through neighbor 2, Node " + str(l2_NID))
				print ("It would take " + str(linked1.search(dest_nid).get_hops()) + " hops")
			elif linked3.search(dest_nid):
				print("Node" + str(dest_nid) + " can be reached through neighbor 3, Node " + str(l3_NID))
				print ("It would take " + str(linked1.search(dest_nid).get_hops()) + " hops")
			elif linked4.search(dest_nid):
				print("Node" + str(dest_nid) + " can be reached through neighbor 4, Node " + str(l4_NID))
				print ("It would take " + str(linked1.search(dest_nid).get_hops()) + " hops")
			else:
				print("No route found to Node" + str(dest_nid))
			#os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")
		elif(selection == '6'):
			if linked1.head:
				if linked1.head.get_hops():
					print("By sending to Node " + str(linked1.head.get_nid()) + " the following nodes can be reached:")
					curr_ptr = linked1.head
					while curr_ptr is not None:
						print( "    Node " + str(curr_ptr.get_nid()) + " in " + str(curr_ptr.get_hops()) + " hops")
						curr_ptr = curr_ptr.get_next()
			if linked2.head:
				if linked2.head.get_hops():
					print("By sending to Node " + str(linked2.head.get_nid()) + " the following nodes can be reached:")
					curr_ptr = linked2.head
					while curr_ptr is not None:
						print( "    Node " + str(curr_ptr.get_nid()) + " in " + str(curr_ptr.get_hops()) + " hops")
						curr_ptr = curr_ptr.get_next()
			if linked3.head:
				if linked3.head.get_hops():
					print("By sending to Node " + str(linked3.head.get_nid()) + " the following nodes can be reached:")
					curr_ptr = linked3.head
					while curr_ptr is not None:
						print( "    Node " + str(curr_ptr.get_nid()) + " in " + str(curr_ptr.get_hops()) + " hops")
						curr_ptr = curr_ptr.get_next()
			if linked4.head:
				if linked4.head.get_hops():
					print("By sending to Node " + str(linked4.head.get_nid()) + " the following nodes can be reached:")
					curr_ptr = linked4.head
					while curr_ptr is not None:
						print( "    Node " + str(curr_ptr.get_nid()) + " in " + str(curr_ptr.get_hops()) + " hops")
						curr_ptr = curr_ptr.get_next()
					

		else:

			# default for bad input
			#os.system('clear')
			time.sleep(.5)
			continue

# initiate program
if __name__ == "__main__":
	main(sys.argv)
