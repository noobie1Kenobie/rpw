#!/usr/bin/python
########################################################################################################
#                                                                                                      #
# The following code has been tested and it works '24Nov2020'                                          #
#                                                                                                      #
# Note: It is important that the 'nodes', 'edges' and 'labels' all match in terms                      #
# of their dictionary structures. If the key for the nodes are in integer then                         #
# all the keys for 'edges' and 'labels' must also be in integer. If it is in string                    #
# then all of them needs to be a string.                                                               #
# Note: The indexing for every tuple and list must be correct. Like most arrays we reference it        #
#       starting with zero. But on the assignment to the node number for the processes, we start of    #
#       with 1. Beware of this. To ensure that everything is in sync, always check the contents of     #
#       the tuple of list.                                                                             #
#                                                                                                      #
# Program note:                                                                                        #
#     weight used in defining 'G' digraph is the task time for each node.                              #
#     rpw_weight will be the weight used to 'rank' each of the node, in accordance to the rules in     #
#                Ranked Positional Weight Method. It will be the sum of all the task time that follows #
#                the node being calculated.                                                            #
#                                                                                                      #
# author: noobie1Kenobie                                                                               #
# date: 08 March 2022                                                                                  #
# version: 1.00                                                                                        #
#                                                                                                      #
# New implementation, the graph will be drawn/plotted using the graphviz library. This will simplify   #
# the process of drawing or visualizing the process. The api:                                          #
#     https://graphviz.readthedocs.io/en/stable/examples.html                                          #
#                                                                                                      #
########################################################################################################

import networkx as nx
import pylab as plt
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv
import numpy as np
import matplotlib.pyplot as myplt
import matplotlib.image as mpimg
import sys, os
import re
import argparse
from datetime import datetime
from datetime import date
import time

scriptName = ""
scriptVersion = ""

tasktimes_file = 'tasktime.txt'
taskNames_file = 'tasknames.txt'
edges_nodes_file = 'edges_nodes.txt'
workdays_worktime_annualDemand_file = 'demand_worktime.txt'
timeMultiplier = {'hrs':1, 'min':60, 'sec':3600}

def getDataFromFiles(workingDir):
    # Begin by reading in the data from text files
    with open(workingDir + "/" + tasktimes_file) as f:
        taskTimes = f.read().splitlines()
    
    with open(workingDir + "/" + taskNames_file) as f:
        taskNames = f.read().splitlines()
    
    with open(workingDir + "/" + edges_nodes_file) as f:
        edges_nodes = f.read().splitlines()
    
    with open(workingDir + "/" + workdays_worktime_annualDemand_file) as f:
        worktimeDemand = f.read().splitlines()

    return [taskTimes, taskNames, edges_nodes, worktimeDemand];
# End of getDataFromFile()

# function to draw/plot the graph to a file
def plotGraph(G, ofname, title):
    G.graph['graph']={'rankdir':'LR'} 
    G.graph['node'] = {'shape':'circle'}
    G.graph['edges'] = {'arrowsize':'2.0'}
    G.graph['labelloc'] = "t"
    G.graph['label'] = title
    G.graph['fontsize'] = 20
    A = to_agraph(G)
    print(A)
    A.layout('dot')
    A.draw(ofname)
# End of plotGraph()

# function to show the image file on screen, result validation
def showImg(fname):
    img = mpimg.imread(fname)
    imgplot = myplt.imshow(img)
    myplt.axis('off')
    myplt.show(block=False)
    myplt.pause(3)
    myplt.close()
# End of showImg()

# funtion to plot bar graph to file
#~valist: it is a dictionary variable that contains the list required to construct the stacked bar graph
#~This list must contain the following list:
#~  'task times'  - task time or the processing time for each task on the production line
#~  'idle times'  - idle time faced by each task on the production line
#~  'title'       - title for the bar chart
#~  'xTickLabels' - The labels for each of the task
#~  'xlabel'      - Label for x axis
#~  'ylabel'      - Label for y axis
#~  'output file' - name of the output file to save the figure to
def plotStackBarChart(varlist):
    # plot the bar graph for the unbalanced line showing idle times and task times
    N = len(varlist['task times'])

    ind = np.arange(1,N+1)
    width = 0.55
    fig = myplt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax = fig.add_subplot(111)
                              
    ax.bar(ind, varlist['task times'], width, color='b')
    ax.bar(ind, varlist['idle times'], width, bottom=varlist['task times'], color='r')
    ax.set_title(varlist['title'])
    
    myplt.xticks( [ k for k in range(1, N+1) ] )
    ax.set_xticklabels( varlist['xTickLabels'] )

    ax.set_xlabel(varlist['xLabel'])
    ax.set_ylabel(varlist['yLabel'])
    
    maxYVal = max([ varlist['task times'][k]+varlist['idle times'][k] for k in range(len(varlist['task times'])) ])
    
    numExp = np.floor(np.log10(np.abs(maxYVal))).astype(int)
    maxYExp = numExp + 1

    box = ax.get_position() 
    ax.set_position( [box.x0, box.y0, box.width*0.8, box.height] ) 
    ax.legend(labels=['Task time','Idle time'], loc='center left', bbox_to_anchor=(1.0, 0.5), ncol=1)
    ax.set_yticks(np.arange(0, maxYVal+float(10**maxYExp/10), float(10**maxYExp/10)), minor=False)
    
    ax.axhline(y=maxYVal, color='g', linestyle=':')
    trans = ax.get_yaxis_transform()
    ax.text(0, maxYVal, "{:.2f}".format(maxYVal), color="green", transform=trans, ha="left", va="center")
    ax.yaxis.grid(True, which='major')

    myplt.savefig(varlist['output file'])
# End of plotBar() function

def writeToTextFile(fname, content):
    try:
        fout = open(fname, 'w')
    except IOError as e:
        errorPrint( "Unable to open {}, error no: ".format(fname, str(e.errno)) , e.errno )
    
    for line in content:
        fout.write(str(line)+"\n")
    
    fout.close()
#~End of writeToTextFile()

def createReport(reportVarList):
    # Create a report of the calculations
    takttime = reportVarList['takttime']
    workdays = reportVarList['workdays']
    workhours = reportVarList['workhours']
    demand = reportVarList['demand']
    totalworktime = reportVarList['totalworktime']
    argsUnit = reportVarList['unit for cal']
    G = reportVarList['G']
    G_takt_balanced = reportVarList['G_takt_balanced']
    G_highest_balanced = reportVarList['G_highest_balanced']

    maxTaskTime = max([ G.nodes[k].get('weight') for k in G.nodes ])
   
    totalProcessingTime = sum([ G.nodes[k].get('weight') for k in G.nodes ])
    taktIdle = sum( [ takttime-G.nodes[k].get('weight') for k in G.nodes ] )
    highestIdle = sum( [ maxTaskTime-G.nodes[k].get('weight') for k in G.nodes ] )
    smoothnessTakt = np.sqrt( sum([ np.power((takttime-G.nodes[k].get('weight')),2) for k in G.nodes ]) )
    smoothnessHighest = np.sqrt( sum([ np.power((maxTaskTime-G.nodes[k].get('weight')),2) for k in G.nodes ]) )
    reportStr=list()
    reportStr.append("  Report generated on " + date.today().strftime("%d %B %Y") + " at " + datetime.now().strftime("%H:%M:%S") )
    reportStr.append("  ")
    reportStr.append("  ")
    reportStr.append( "  Total working days in one year                : "+"{:12.2f} ".format(float(workdays)) +"days") 
    reportStr.append( "  Total working hours in one day                : "+"{:12.2f} ".format(float(workhours)) + "hours") 
    reportStr.append( "  Total available time for processing           : "+"{:12.2f} ".format(totalworktime)+argsUnit) 
    reportStr.append( "  The annual demand                             : "+"{:12.2f} ".format(float(demand)) + "units" ) 
    reportStr.append( "  The takt time for this process                : "+ "{:12.2f} ".format(takttime) + argsUnit)  
    reportStr.append( "  The highest processing time for this line     : "+ "{:12.2f} ".format(maxTaskTime) + argsUnit)  
    reportStr.append( "  The total task time for this line             : "+ "{:12.2f} ".format(totalProcessingTime) + argsUnit)  
    reportStr.append( "  Number of nodes                               : "+ "{:12.0f} ".format(len(G.nodes.keys())) )  
    reportStr.append( "  Number of edges                               : "+ "{:12.0f} ".format(len(G.edges)) )  
    reportStr.append(" ")
    reportStr.append(" ")
    reportStr.append("  ----------------------------------------- Unbalanced Line -------------------------------------------------")
    reportStr.append("        task name                                                          task time   idle time   idle time")
    reportStr.append("                                                                                          (takt)   (highest)")
    reportStr.append("  -----------------------------------------------------------------------------------------------------------")
    res = [ "["+"{0:>3}".format(k)+"] "+"{0:<64}".format(G.nodes[k].get('name'))+"{:12.2f}".format(G.nodes[k].get('weight'))+"{:12.2f}".format(takttime-G.nodes[k].get('weight'))+"{:12.2f}".format(maxTaskTime-G.nodes[k].get('weight')) for k in G.nodes ]
    [ reportStr.append("  " + res[k]) for k in range(0,len(res)) ]
    reportStr.append(" ")
    
    reportStr.append( "  Total idle time (takt)                          : "+"{:12.2f} ".format(float(taktIdle)) + argsUnit) 
    reportStr.append( "  Total idle time (highest)                       : "+"{:12.2f} ".format(float(highestIdle)) + argsUnit) 
    reportStr.append( "  Smoothness index based on takt time             : "+"{:12.2f} ".format(smoothnessTakt) ) 
    reportStr.append( "  Smoothness index based on the highest task time : "+"{:12.2f} ".format(smoothnessHighest) ) 
    reportStr.append( "  Line efficiency (takt)                          : "+"{:12.2f} %".format( (totalProcessingTime/(totalProcessingTime+taktIdle)) * 100 ) ) 
    reportStr.append( "  Line efficiency (highest)                       : "+"{:12.2f} %".format( (totalProcessingTime/(highestIdle+totalProcessingTime)) * 100 ) ) 
    reportStr.append(" ")
    reportStr.append(" ")
    reportStr.append("  ---------------------------------------- Balanced Line (takt) ---------------------------------------------")
    reportStr.append("        task groupings                                                     task time               idle time")
    reportStr.append("  -----------------------------------------------------------------------------------------------------------")
    res = [ "["+"{0:>3}".format(k)+"] "+"{0:<64}".format(str(G_takt_balanced.nodes[k].get('group')))+"{:12.2f}".format(G_takt_balanced.nodes[k].get('weight'))+"{:24.2f}".format(takttime-G_takt_balanced.nodes[k].get('weight')) for k in G_takt_balanced.nodes ]
    takt_res = res
    [ reportStr.append("  " + res[k]) for k in range(0,len(res)) ]
    reportStr.append(" ")
    global taktBalancedIdle
    taktBalancedIdle = sum( [ takttime-G_takt_balanced.nodes[k].get('weight') for k in G_takt_balanced.nodes ] )
    smoothnessTaktBalanced = np.sqrt( sum([ np.power((takttime-G_takt_balanced.nodes[k].get('weight')),2) for k in G_takt_balanced.nodes ]) )
    reportStr.append( "  Total idle time                                 : "+"{:12.2f} ".format(float(taktBalancedIdle)) + argsUnit) 
    reportStr.append( "  Smoothness index                                : "+"{:12.2f} ".format(smoothnessTaktBalanced) ) 
    reportStr.append( "  Maximum units with this setup (annual demand)   : "+"{:12.2f} ".format(totalworktime/max([ G_takt_balanced.nodes[k].get('weight') for k in G_takt_balanced.nodes ]) ) )  
    reportStr.append( "  Line efficiency                                 : "+"{:12.2f} %".format( (totalProcessingTime/(float(taktBalancedIdle)+totalProcessingTime)) * 100 ) ) 
    reportStr.append(" ")
    reportStr.append(" ")
    reportStr.append("  -------------------------------------- Balanced Line (highest) --------------------------------------------")
    reportStr.append("        task groupings                                                     task time               idle time")
    reportStr.append("  -----------------------------------------------------------------------------------------------------------")
    res = [ "["+"{0:>3}".format(k)+"] "+"{0:<64}".format(str(G_highest_balanced.nodes[k].get('group')))+"{:12.2f}".format(G_highest_balanced.nodes[k].get('weight'))+"{:24.2f}".format(maxTaskTime-G_highest_balanced.nodes[k].get('weight')) for k in G_highest_balanced.nodes ]
    [ reportStr.append("  " + res[k]) for k in range(0,len(res)) ]
    reportStr.append(" ")
    highestBalancedIdle = sum( [ maxTaskTime-G_highest_balanced.nodes[k].get('weight') for k in G_highest_balanced.nodes ] )
    smoothnessHighestBalanced = np.sqrt( sum([ np.power((maxTaskTime-G_highest_balanced.nodes[k].get('weight')),2) for k in G_highest_balanced.nodes ]) )
    reportStr.append( "  Total idle time                                 : "+"{:12.2f} ".format(float(highestBalancedIdle)) + argsUnit) 
    reportStr.append( "  Smoothness index                                : "+"{:12.2f} ".format(smoothnessHighestBalanced) ) 
    reportStr.append( "  Maximum units with this setup (highest)         : "+"{:12.2f} ".format(totalworktime/max([ G_highest_balanced.nodes[k].get('weight') for k in G_highest_balanced.nodes ]) ) ) 
    reportStr.append( "  Line efficiency                                 : "+"{:12.2f} %".format( (totalProcessingTime/(float(highestBalancedIdle)+totalProcessingTime)) * 100 ) ) 
    reportStr.append("  \n  ")
    reportStr.append("  Report generated by " + scriptName + " v" + scriptVersion)
    reportStr.append("  End of report ")

    writeToTextFile( workingDir + "/" + "Line_Balancing_Report.txt", reportStr )
#~End of createReport()

def cmdLineArgs(argv):
    global scriptName
    global scriptVersion
    
    scriptName = os.path.realpath(__file__)
    #print (sys.argv)
    with open(scriptName) as fname:
        for line in fname:
            results = re.search('.*version: ([0-9][.][0-9][0-9]).*', line, re.M|re.I)
            if results:
                scriptVersion = str(results.group(1))
    parser = argparse.ArgumentParser( 
                description="Program to determine the order for a Balanced Line using Ranked Positional Weight Method", 
                epilog = "Ranked Positional Weight Method v" + scriptVersion + " This is where you can add more information."
                                    )
    parser.add_argument(  
            "-d", "--dir", 
            default=os.getcwd(), # if no argument is supplied then use the current working directory
            help="The directory to work on, there should be a folder 'data' containing all the data to process."
                        )
    parser.add_argument(  
            "-u", "--unit", 
            default="hrs",
            help="Specifies the base unit for calculations. " + 
                  "Values to use 'hrs'=hours, 'min'=minutes and 'sec'=seconds"
                        )
    return parser.parse_args() 
#~End of cmdLineArgs()

def calculateRPW(G_digraph, limit):
    rpw_weights = { i : sum([ G_digraph.nodes[j].get('weight') for j in list(nx.dfs_tree(G_digraph, source=i)) ]) for i in G_digraph.nodes }
    sorted_rpw_weights = \
            { k:v for k, v in sorted(rpw_weights.items(), key=lambda item: item[1], reverse=True) }
    sorted_rpw_weights_keys = list(sorted_rpw_weights.keys())    
    
    print(rpw_weights)
    print(sorted_rpw_weights)
    print(limit)

    count=0;totalweight=0;group={};group_key=1;tmpgrp=list();nodeweight=list(); 
    for count in range(len(sorted_rpw_weights_keys)):
        totalweight += G_digraph.nodes[sorted_rpw_weights_keys[count]].get('weight')
        tmpgrp += [sorted_rpw_weights_keys[count]]
        print("Adding " + sorted_rpw_weights_keys[count] + " to group " + str(group_key))
        print(tmpgrp)
        print("Total weight now: " + str(totalweight))
        if (count+1 > len(sorted_rpw_weights_keys)-1):
            group[group_key] = tmpgrp
            nodeweight.append(totalweight)
            break
        if (totalweight + G_digraph.nodes[sorted_rpw_weights_keys[count+1]].get('weight')) > limit:
            group[group_key] = tmpgrp
            tmpgrp = []
            group_key += 1
            nodeweight.append(totalweight)
            totalweight = 0
    
    reverse_sorted_task_times = sorted( { i: G_digraph.nodes[i].get('weight') for i in G_digraph.nodes }.items(), key=lambda kv:(kv[1],kv[0]), reverse=True )
    G_balanced_line = nx.DiGraph()
    str1 = ", "
    G_balanced_line.add_nodes_from({ k: (str1.join(group[k])) for k in range(1, len(group)+1) })
    G_balanced_line.add_edges_from({ k: (k,k+1) for k in range(1,len(group)+1) if (k+1 < len(group)+1) }.values())
    nx.set_node_attributes(G_balanced_line, {k: {'label':str(k)+" "+str(group[k])} for k in group.keys()} )
    
    nx.set_node_attributes(G_balanced_line, { k+1: {'weight':nodeweight[k]} for k in range(0,len(nodeweight)) })
    nx.set_node_attributes(G_balanced_line, {k: {'group':group[k]} for k in group.keys()} )
    return G_balanced_line
#~End of calculateRPW

def main(argv):
    global workingDir
    global G
    global G_takt_balanced
    global G_highest_balanced
    args = cmdLineArgs(argv) 
    workingDir = args.dir 

    print( " [~ " + str(time.strftime("%Y %b %d-%H:%M:%S")) + " Starting " + scriptName + " v"+ scriptVersion +"]" ) 
    
    taskTimes, taskNames, edges_nodes, worktimeDemand = getDataFromFiles(workingDir)
    
    workdays, workhours, demand = worktimeDemand[0].split(',')
    totalworktime = float(workdays) * float(workhours) * float(timeMultiplier[args.unit])
    takttime = totalworktime / float(demand)
    
#----------------------- Construction of the diGraph and calculations ----------------------------------- 
    G = nx.DiGraph()

    G.add_nodes_from( [str(i) for i in range(1, len(taskTimes)+1)] )
    nx.set_node_attributes(G, { str(i): {'name':taskNames[i-1]} for i in range(len(taskNames)+1) } )
    nx.set_node_attributes(G, { str(i): {'weight':float(taskTimes[i-1])} for i in range(len(taskTimes)+1) } )
    [ G.add_edges_from([ i.split(',') ]) for i in edges_nodes ]
    labels = { str(k) : (str(k) + ", w: " + taskTimes[k-1]) for k in range(1,len(taskNames)+1) }
    nx.set_node_attributes(G, {str(i): {'label': str(i)+"-("+str(taskTimes[i-1])+")" } for i in range(1,len(taskTimes)+1)} )
    
    plotGraph(G,workingDir + "/" + "rpw_out.png", "Unbalanced line")
    
    showImg(workingDir + "/" + "rpw_out.png")
    print("Takttime: "+str(takttime))
    G_takt_balanced = calculateRPW(G, takttime)
    plotGraph(G_takt_balanced,workingDir + "/" + "rpw_out_takt_balanced.png", "Balanced line using takt time")
    
    showImg(workingDir + "/" + "rpw_out_takt_balanced.png")
    maxTaskTime = max([ G.nodes[k].get('weight') for k in G.nodes ])

    G_highest_balanced = calculateRPW(G, maxTaskTime)
    plotGraph(G_highest_balanced,workingDir + "/" + "rpw_out_highest_balanced.png", "Balanced line using highest time")
    
    showImg(workingDir + "/" + "rpw_out_highest_balanced.png")
#--------------------- End of Construction of the diGraph and calculations ------------------------------  

    # Create the reportVarList, a dictionary of all the variables needed to generate the report
    reportVarList = {}
    reportVarList['workdays'] = workdays
    reportVarList['workhours'] = workhours
    reportVarList['totalworktime'] = totalworktime
    reportVarList['unit for cal'] = args.unit
    reportVarList['takttime'] = takttime
    reportVarList['demand'] = demand
    reportVarList['G'] = G
    reportVarList['G_takt_balanced'] = G_takt_balanced
    reportVarList['G_highest_balanced'] = G_highest_balanced
    createReport(reportVarList)
    
    # plot the bar graph for the unbalanced line showing idle times and task times
    unbalanced_task_times = [ G.nodes[k].get('weight') for k in G.nodes ]
    unbalanced_idle_times = [ takttime - j for j in unbalanced_task_times ]
    
    barPlotVar = {}
    barPlotVar['task times'] = unbalanced_task_times
    barPlotVar['idle times'] = unbalanced_idle_times
    barPlotVar['title'] = "Unbalanced line with task times and idle times"
    barPlotVar['xTickLabels'] = [ k for k in G.nodes.keys() ]
    barPlotVar['xLabel'] = "Task numbers"
    barPlotVar['yLabel'] = "Processing time (hrs)"
    barPlotVar['output file'] = workingDir + "/" + "rpw_stackBar_unbalanced.png"
    plotStackBarChart(barPlotVar)
    showImg(barPlotVar['output file'])
    
    # plot the bar graph for the unbalanced line showing idle times and task times
    takt_balanced_task_times = [ G_takt_balanced.nodes[k].get('weight') for k in G_takt_balanced.nodes ]
    takt_balanced_idle_times = [ takttime - j for j in takt_balanced_task_times ]
    
    barPlotVar = {}
    barPlotVar['task times'] = takt_balanced_task_times
    barPlotVar['idle times'] = takt_balanced_idle_times
    barPlotVar['title'] = "Task times and idle times distribution (takt time)"
    barPlotVar['title'] = "Takt time balanced line with task times and idle times"
    barPlotVar['xTickLabels'] = [ k for k in G_takt_balanced.nodes.keys() ]
    barPlotVar['xLabel'] = "Task numbers"
    barPlotVar['yLabel'] = "Processing time (" + args.unit + ")"
    barPlotVar['output file'] = workingDir + "/" + "rpw_stackBar_takt_balanced.png"
    plotStackBarChart(barPlotVar)
    showImg(barPlotVar['output file'])

    # plot the bar graph for the unbalanced line showing idle times and task times
    highest_balanced_task_times = [ G_highest_balanced.nodes[k].get('weight') for k in G_highest_balanced.nodes ]
    highestTaskTime = np.max([ G.nodes[k].get('weight') for k in G.nodes ])
    highest_balanced_idle_times = [ highestTaskTime - j for j in highest_balanced_task_times ]
    
    barPlotVar = {}
    barPlotVar['task times'] = highest_balanced_task_times
    barPlotVar['idle times'] = highest_balanced_idle_times
    barPlotVar['title'] = "Task times and idle times distribution (highest task time)"
    barPlotVar['xTickLabels'] = [ k for k in G_highest_balanced.nodes.keys() ]
    barPlotVar['xLabel'] = "Task numbers"
    barPlotVar['yLabel'] = "Processing time (" + args.unit + ")"
    barPlotVar['output file'] = workingDir + "/" + "rpw_stackBar_highest_balanced.png"
    plotStackBarChart(barPlotVar)
    showImg(barPlotVar['output file'])

    print( " [~ " + str(time.strftime("%Y %b %d-%H:%M:%S")) + " Ending " + scriptName + " v"+ scriptVersion +"]" ) # indicates the execution end of the script

# End of main()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    #sys.exit()

