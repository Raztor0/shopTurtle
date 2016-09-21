#!/bin/python

import socket
import sys
import time
import select

from threading import Thread, Lock

connections = []
lock = Lock()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

def listen_for_shells():
  while True:
    connection, client_address = sock.accept()
    connection.setblocking(0)
    print "Got a connection from: " + str(client_address)
    with lock:
      connections.append(connection)

def listen_for_responses():
  while True:
    with lock:
      readable, _, _ = select.select(connections, [], [], 1)

    for connection in readable:
      print "Reading from: " + str(connection.getpeername())
      while True:
        try:
          data = connection.recv(1024)

          if data:
            sys.stdout.write(data)
            sys.stdout.flush()
          else:
            break
        except:
          break

    time.sleep(1)

def print_options():
  print "Here are the available options:"
  print "b <command> - Broadcast a command"
  print "l - List connections"
  print "s <number> - Select a connection"

if __name__ == '__main__':
  t = Thread(target=listen_for_shells)
  t.daemon = True
  t.start()

  t = Thread(target=listen_for_responses)
  t.daemon = True
  t.start()

  print "Welcome to shopTurtle."
  print_options()

  while True:
    try:
      command = raw_input("Enter an option\n")
    except:
      sock.close()
      with lock:
        for connection in connections:
          connection.close()

      break

    if command[0:1] == "b":
      broadcast_command = command[2:]
      with lock:
        for connection in connections:
          try:
            print "Sending command: '" + broadcast_command + "' to: " + str(connection.getpeername())
            connection.sendall(broadcast_command + '\n')
          except:
            pass
    elif command == "l":
      for i, connection in enumerate(connections):
        print "[" + str(i) + "] " + str(connection.getpeername())

    elif command[0:1] == "s":
      connection_index = command[2:]
      with lock:
        if not connection_index.isdigit() or int(connection_index) >= len(connections):
          print "Invalid connection index: " + str(connection_index)
          continue
      with lock:    
        for i, connection in enumerate(connections):
          if i == int(connection_index):
            try:
              command = raw_input("Enter a command to send to " + str(connection.getpeername()))
            except:
              sock.close()
              with lock:
                for connection in connections:
                  connection.close()

              break

            connection.sendall(command + '\n')
    else:
      print "Invalid option. Please try again."
      print_options()

  print "Done"
  sys.exit()