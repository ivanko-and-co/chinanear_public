from Main import socketio, app
#0
#app.run("localhost", 5001, debug=True)
if __name__ == '__main__':
    socketio.run(app, "localhost", 5001, debug=True)