import subprocess
import tempfile
import os
import re
import time
import threading

def assemble_binary(code):
    code = '\n'.join(code.split('/'))
    code = '\n'.join(code.split('\\'))
    process = subprocess.Popen(["dtasm", "-o", "-", "--binary", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = process.communicate(code)
    res = results[0]
    err = results[1]
    return (res, err)

def assemble(code):
    res, err = assemble_binary(code)
    words = []
    i = 0
    while i < len(res) /  2:
        byte_one = ord(res[2*i])
        byte_two = ord(res[2*i+1])
	print "Bytes:", byte_one, byte_two
        word = "0x%04x" % ((byte_one << 8) + byte_two)
        words.append(word)
	i += 1
    print "Assembly attempted"
    return (words, err)

def timeout(p):
    if p.poll() == None:
        p.kill()

register_re = re.compile(r"([A-Z]{1,2}):\s*0x([\dA-F]+)")

def execute(code):
    binary, err = assemble_binary(code)
    if err != "" and not ("warning" in err):
        return err

    num_words = len(binary) / 2

    fd, filename = tempfile.mkstemp()
    file = os.fdopen(fd, 'wb')
    file.write(binary)
    file.close()

    start = time.time()
    proc = subprocess.Popen(['dtemu', '-t', filename], stderr=subprocess.PIPE)
    t = threading.Timer(5, timeout, [proc])
    while proc.poll() == None:
        if time.time() - start > 5:
	    proc.kill()
    final = time.time() - start

    err = proc.stderr.read()

    os.remove(filename)

    register_matches = register_re.findall(err)

    changed_registers = []

    for match in register_matches:
        if match[1] != "0000":
            changed_registers.append(match[0] + ":0x" + match[1])
    registers = ', '.join(changed_registers)
    ms = final * 1000
    response = "[" + str(num_words) + " words][" + registers + "][%dms]" % round(ms)
    return response
