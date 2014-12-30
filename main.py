__author__ = 'teo'

from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import requests
import re
import pygraphviz


def b_print(a):
    """For testing purposes"""
    for x in range(0,len(a)):
        print str(x) + '===================================================================================================='
        a[x].string
        print str(x) + '===================================================================================================='


test6 = "https://en.wikipedia.org/wiki/Information_Processing_Language"

def re_catch(inf):
    """prevent the creation of nodes for things that aren't progamming languages"""
    if (re.search('\[[0-9]*\]', inf.text) is None) and (re.search('cite',inf.text) is None) and (re.search('Citation',inf.text) is None): #compress this you lazy bastard....
        return True
    else:
        print inf.text + "killed"
        return False


def bad_link_catch(start):
    """Prevent 404 errors"""
    if (re.search('orghttp',start)) is None:
        return False
    else:
        return True

DG = nx.DiGraph() #create blank new graph
allTitles = [] # a list of all titles added
covered = [] # links that we have run by and checked
added = [] # titles that I have added and done something to
dates = {}


#use links as the already examined meachnism... or a back up one
# add nodes for invalid links!!!!!!!!! once we get the title that is....

def one_page(start):
    print ('Link is ',start) #parents for filtering purposes
    if start in added:
        print "Already Covered!"
        return ()

    if bad_link_catch(start):
        print "Invalid link!"
        return ()
    covered.append(start)

    r = requests.get(start)

    print ('server response:',r)


    r1 = r.text
    soup = BeautifulSoup(r1)

    if soup.h1 is None:
        print "Reached End 1!"
        return ()
    if soup.title is None:
        print "Reached End 2!"
        return ()
    if soup.h1.span is None:
        print soup.h1.span
        print "Reached End 3!"
        return ()


    title = soup.h1.span.string.replace(' (programming language)', '')
    print ('The title is',title)


    if title in allTitles:
        print start
        print title
        print "Already Examined"
        return ()

    added.append(start)
    if soup.table is None:
        print start
        print title
        print "Reached End 4!"
        return ()



    trytest = soup.find_all('table', class_ = 'infobox vevent')
    if trytest == []:
        print "Reached End 5!"
        return ()

    date_find = trytest[0].find_all('tr') #Start the grabbing of suc/predcs

    for x in range(1, len(date_find)): #grabbing the date
        try:
            if re.search('Appeared', date_find[x].th.string) is None:
                pass
            if re.search('Appeared', date_find[x].th.string) is not None:
                time = (date_find[x].td.text)
                dates[title] = time
                break
            if re.search('Initial release', date_find[x].th.string) is not None:
                time = (date_find[x].td.text)
                dates[title] = time
                break
        except TypeError:
            print "There was a type error"
            # countdate += 1
        except AttributeError:
            print "There was an attribute error"
            # countdate += 1

    trytest2 = trytest[0].find_all('table')
    if trytest2 == []:
        print "Reached End 6!"
        return ()

    test = (soup.find_all('table', class_ = 'infobox vevent')[0].find_all('table')[0].find_all('tr'))


    allTitles.append(title)
    influenced = soup.a
    influenced_by = soup.a
    dialect = soup.a

    for x in range(0, len(test) -1):
        # print test[x]
        if re.search('Influenced', test[x].text) is None:
            # print 'r'
            pass
        if re.search('Influenced(?! by)', test[x].text) is not None:
            # print 'q'
            influenced = test[x+1]
    for x in range(1, len(test) - 1):
        if re.search('Influenced by', test[x].text) is None:
            pass
        if re.search('Influenced by', test[x].text) is not None:
            influenced_by = test[x+1]
    for x in range(1, len(test) - 1):
        if re.search('Dialects', test[x].text) is None:
            pass
        if re.search('Dialects', test[x].text) is not None:
            dialect= test[x+1]

    influenced_links1 = influenced.find_all('a')
    influenced_links1_by = influenced_by.find_all('a')
    dialects1 = dialect.find_all('a')
    influenced_links = filter(re_catch,influenced_links1)
    influenced_links_by = filter(re_catch,influenced_links1_by)
    dialects = filter(re_catch, dialects1)
    DG.add_edges_from([(title, s.text) for s in influenced_links ])
    DG.add_edges_from([(s.text, title) for s in influenced_links_by ])
    DG.add_edges_from([(title, s.text) for s in dialects])
    print('Completed:', title)
    map (one_page, [('https://en.wikipedia.org' + s.get('href')) for s in influenced_links]) #recusion
    map (one_page, [('https://en.wikipedia.org' + s.get('href')) for s in influenced_links_by])
    map (one_page, [('https://en.wikipedia.org' + s.get('href')) for s in dialects])
    return ()



def widithcalc(q,s):
    """Calculates the radius of the node"""
    p = len(q.successors(s))
    return ( (p/5) + .7)


def colormod(s):
    """Determines what color a node should be"""
    try:
        year = int((re.search('[0-9]{4}', dates[s])).group(0))
        print year
        if year <= 1960:
            return 'violet'
        elif year <= 1970:
            return 'blue'
        elif year <= 1980:
            return 'green'
        elif year <= 1990:
            return 'yellow'
        elif year <= 2000:
            return '#FF7F00'
        elif year <= 2005:
            return '#F664AF'
        elif year <= 2010:
            return '#FF8ABA'
        elif year <= 2015:
           return 'red'
    except TypeError:
        print 'invalid string'






def attributeset(q, s, shape):
    """Sets a node's attributes"""
    q.node[s]['shape'] = shape
    q.node[s]['fixedsize'] = 'false'
    q.node[s]['width'] = widithcalc(q,s)
    q.node[s]['style'] = 'filled'
    q.node[s]['fillcolor'] = colormod(s)
    return ()


def massat(q):
    """Sets the attributes while dealing with possible key issues"""
    for x in range(0, len(allTitles)):
        print(allTitles[x])
        try:
            attributeset(q,allTitles[x],'circle')
        except KeyError:
            print "title mismatch, outputting formatting consquences "



def main():
    start = input("Input the wikipedia programming language page that you wish to start on:")
    one_page(start)
    massat(DG)
    nx.write_dot(DG,'results.dot')


if __name__ == '__main__':
    main()