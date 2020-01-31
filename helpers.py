import config as c

def vectorizetext(file):
    lines = []
    with open(file) as f:
        for i in f:
            line = i.strip('\n')
            if line.strip() != '':
                lines.append(line)
    return lines

def strip(string):
    rm = [',', '.', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']']
    for c in rm:
        string = string.replace(c, '')
    return string

def find(line, quotes): # assumes line.strip(irc garbage) --(string, [set1,setn])
    line = [line]
    for word in line:
        rm = []
        for quote in quotes:

            if(quote.find(word) == -1):
                rm.append(quote)
        for r in rm:
            quotes.remove(r)
    if(len(quotes) == 1):
        return quotes[0]
    elif(len(quotes) > 1):
        return quotes
    else:
        return -1
