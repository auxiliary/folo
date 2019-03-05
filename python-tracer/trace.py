import os 
import sys
import json
import socket
import threading

_foo = None

class LineTracer:
    def __init__(self, target):
        self.sourcefiles = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("localhost", 5050))

        # read in the configuration
        self.target = target
        self.last_filename = ""

    def trace_calls(self, frame, event, arg):
        global _foo

        current_filename = os.path.abspath(frame.f_code.co_filename)
        if _foo != current_filename:
            #print(current_filename)
            pass
        _foo =  current_filename

        if current_filename.find(self.target) != -1:
            print (current_filename)
            payload = {"line": frame.f_lineno}
            if current_filename != self.last_filename:
                payload['file'] = current_filename
            self.socket.sendall(json.dumps(payload) + "\n")
            self.socket.recv(32)

        return self.trace_calls

class Tracer:
    def __init__(self, config_file):
        # Every target has a filename, a func name, 
        # a variable name, and a line number
        self.targets = []
        self.sourcefiles = {}
        self.record_flag = -1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("localhost", 5050))

        # read in the configuration
        self.targets = json.load(open(config_file))
        for i, _ in enumerate(self.targets):
            self.targets[i]['values'] = []

    def trace_calls(self, frame, event, arg):
        counter = 0
        next_func = self.trace_calls
        for i, target in enumerate(self.targets):
            try:
                current_filename = os.path.abspath(frame.f_code.co_filename)
            except:
                continue
            if current_filename != target['filename']:
                if not current_filename.startswith('/') and \
                        not current_filename.startswith('<'):
                    print 'skipping', current_filename, 'for', i
                continue

            counter += 1

            if current_filename not in self.sourcefiles:
                self.sourcefiles[current_filename] = \
                        open(current_filename).readlines()

            #if frame.f_code.co_name == target['func']:
            # get the current line being executed to see if it has a 
            # target variable
            line = self.sourcefiles[current_filename][frame.f_lineno - 1]

            if line.find(target['varname']) != -1 and frame.f_lineno == target['lineno']:
                next_func = self.observe_single_line

        return next_func


    def observe_single_line(self, frame, event, arg):
        for i, target in enumerate(self.targets):
            if target['varname'] in frame.f_locals:
                self.targets[i]['values'].append(frame.f_locals[target['varname']])
                value = frame.f_locals[target['varname']]
                value = self.simplify(value)
                message = {"varname": target['varname'], "value": value}
                self.socket.sendall(json.dumps(message))
                self.socket.recv(32)
        
        # give control back to trace_calls
        return self.trace_calls

    def simplify(self, value):
        if type(value) is np.ndarray:
            return value.tolist()
        return value


if __name__ == '__main__':
    mode = sys.argv[1]
    config_filename = sys.argv[2]
    filename_to_run = sys.argv[3]
    sys.argv.pop(0)
    sys.argv.pop(0)
    sys.argv.pop(0)

    if mode == "line":
        tracer = LineTracer(config_filename) # in this case, project_path is config_filename
    if mode == "variable":
        tracer = Tracer(config_filename)

    threading.settrace(tracer.trace_calls)
    sys.settrace(tracer.trace_calls)

    execfile(filename_to_run, globals(), locals())

