import subprocess
import tempfile
import os
import re
import time
import threading

def link(files):
    out_fd, out_fname = tempfile.mkstemp()
    os.fdopen(out_fd).close()

    process_flags = ["dtld", "-o", out_fname, "-k", "none"]
    filenames = []
    for file in files:
        fd, fname = tempfile.mkstemp()
	f = os.fdopen(fd, 'wb')
	f.write(file)
	f.close()
        filenames.append(fname)
        process_flags.append(fname)

    proc = subprocess.Popen(process_flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res, err = proc.communicate()

    for file in filenames:
        os.remove(file)

    final = open(out_fname)
    res = final.read()
    final.close()

    return (res, err)

def assemble_file(code, binary=False):
    code = '\n'.join(code.split('/'))
    code = '\n'.join(code.split('\\'))

    process_flags = ["dtasm", "-o", "-", "-"]
    if binary:
        process_flags.append("--binary")
    process = subprocess.Popen(process_flags, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = process.communicate(code)
    res = results[0]
    err = results[1]
    return (res, err)

def assemble_binary(code):

    code = '///'.join(code.split('\\\\\\'))
    files = code.split('///')

    if len(files) > 1:
        file_binaries = []
	err = ""
        for file in files:
            assembled = assemble_file(file)
            if assembled[0]:
                file_binaries.append(assembled[0])
            if assembled[1]:
                err += assembled[1]
        res, link_err = link(file_binaries)
        err += link_err
	return (res, err)
    else:
        return assemble_file(code, True)

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
    if err and not ("warning" in err):
        return err

    num_words = len(binary) / 2

    fd, filename = tempfile.mkstemp()
    file = os.fdopen(fd, 'wb')
    file.write(binary)
    file.close()

    start = time.time()
    proc = subprocess.Popen(['dtemu', '-t', '-h', filename], stderr=subprocess.PIPE)
    t = threading.Timer(5, timeout, [proc])
    while proc.poll() == None:
        if time.time() - start > 5:
	    proc.kill()
    final = time.time() - start

    err = proc.stderr.read()

    err_lines = err.split("\n")

    for i in range(10):
        err_lines.pop()

    errors = "\n".join(err_lines)

    os.remove(filename)

    register_matches = register_re.findall(err)

    changed_registers = []

    for match in register_matches:
        if match[1] != "0000":
            changed_registers.append(match[0] + ":0x" + match[1])
    registers = ', '.join(changed_registers)
    ms = final * 1000
    response = "[" + str(num_words) + " words][" + registers + "][%dms]" % round(ms)
    return (response, errors)
