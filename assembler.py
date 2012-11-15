import subprocess
import os

def assemble(code):
    code = '\n'.join(code.split('/'))
    code = '\n'.join(code.split('\\'))
    process = subprocess.Popen(["dtasm", "-o", "-", "--binary", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = process.communicate(code)
    res = results[0]
    err = results[1]
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
