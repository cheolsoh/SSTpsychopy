from psychopy import visual, event, core
from psychopy.hardware import keyboard
from psychopy.visual import ShapeStim
from psychopy import gui

import numpy as np
import random
from datetime import datetime

win = None # Initialize with invalid value none means basically empty

# Define basic settings for experimental design
class settings:
    pass
kb = None

# SubjectInformation() gets subject information
# Input: data entered to the dialogue
# Output: subject information stored in subdata

def SubjectInformation():
    
    # Make a GUI dialogue to receive sub data
    dataDlg = gui.Dlg(title = "Subject data")
    dataDlg.addText('For subject ID, change the last two digits only!')
    dataDlg.addField('Subject ID (three digit):', 100)
    dataDlg.addField('Age:', 1)
    dataDlg.addField('Gender:', choices=["Male", "Female"])
    dataDlg.addField('Race:', choices=["Caucasian", "African-American", "Asian", "Hispinic", "Native-American"])
    
    # define a flag to use in a while loop
    vflag=True
    
    # Check the entered information
    while vflag:
        IDflag = False
        AGEflag = False
        
        subdata = dataDlg.show()
        
        # Sub ID should be an integer with 3 digits and should be less than 200
        # Example correct inputs: 101, 120 (last two digits are sub ID)
        if isinstance(subdata[0], int) and len(str(subdata[0])) ==3 and subdata[0]<200 and subdata[0]>100:
            IDflag = True
        else: 
            errorDlg = gui.Dlg()
            errorDlg.addText('Subject ID should be 3 digit integer starting with 1')
            errorDlg.addText('For example, 101 or 106')
            errorDlg.show()
            continue
            
        # Subject age should be an two-digit integer bigger than 18
        if isinstance(subdata[1], int) and len(str(subdata[1])) ==2 and subdata[1]>=18:
            AGEflag = True
        else: 
            errorDlg = gui.Dlg()
            errorDlg.addText('AGE should be 2 digit integer. You should be older than 18.')
            errorDlg.show()
            continue
             
        
        # If sub ID and age are correctly entered, exit the while loop
        if IDflag==True and AGEflag==True:
            vflag=False
            
    
    # Show winodw informing that the sub data are correctly registered
    ConfirmDlg = gui.Dlg()
    ConfirmDlg.addText('Subject information succesfully registered!')
    ConfirmDlg.show()
    
    subdata[0] = str(subdata[0])
    subdata[1] = str(subdata[1])
    
    # return subdata
    return(subdata)

# This function initialize the necessary things. 
# Input: subdata, it uses sub ID to generate different logfile name that includes sub ID
# Output: loads all visual stimuli (arrows); defines experimental parameters (settings); and initilize kb
def Initialize(subdata):
    global win # Declare win as global variable!
    global settings
    global kb
    
    win = visual.Window([1680,1050], monitor="testMonitor", units="deg", screen=1, color = 'white', fullscr=True)
    #win = visual.Window([1680,1050], monitor="testMonitor", units="deg", screen=1, color = 'white')
    #win.setMouseVisible(False)
    settings.TotalBlocks = 5 # How many blocks?
    settings.TotalTrials = 300 # How many total trials?
    settings.TrialsPerBlock = int(settings.TotalTrials/settings.TotalBlocks) # How many trials per block?
    
    LarrowVert = [(0.2,0.05),(0.2,-0.05),(0,-0.05),(0,-0.1),(-.2,0),(0,0.1),(0,0.05)]
    RarrowVert = [(-0.2,0.05),(-0.2,-0.05),(0,-0.05),(0,-0.1),(.2,0),(0,0.1),(0,0.05)]
    
    # Predefine Left and Right arrow images
    settings.Larrow = ShapeStim(win, vertices=LarrowVert, fillColor='black', size=8, lineColor=None)
    settings.Rarrow = ShapeStim(win, vertices=RarrowVert, fillColor='black', size=8, lineColor=None)
    settings.LarrowSTOP = ShapeStim(win, vertices=LarrowVert, fillColor='red', size=8, lineColor=None)
    settings.RarrowSTOP = ShapeStim(win, vertices=RarrowVert, fillColor='red', size=8, lineColor=None)
    
    # Staircase for stopsignal delay tracking
    settings.initSSD = 200
    settings.staircase = 50
    
    # Arrow Duration (1s)
    settings.arrowDuration = 1
    
    # Trial duration (3s)
    settings.trialDuration = 3
    
    # Output filename
    now = datetime.now()
    dt_string = now.strftime("%H%M%d%m") # Get time and date
    
    # logfile format: Subject1XX_TIME and DATE: Subject101_10041904
    # TIME and DATE were added to avoid overwritting filename with same subID
    settings.outfile = "Subject" + subdata[0] + "_" + dt_string + ".csv"
    
    # Initialize keyboard
    kb = keyboard.Keyboard()
    

# This function generates trial sequence
# Input: get experimental paramaters included in settings.Larrow
# Output: returns trialseq that includes randomized trial sequence

def GenSequence(settings):
    global win
    
    # Use shorter variable names
    TotalBlocks = settings.TotalBlocks
    TotalTrials = settings.TotalTrials
    TrialsPerBlock = settings.TrialsPerBlock
    
    # Make arrays with 0z
    ALLrstims = np.repeat(0,TotalTrials)
    ALLarrows = np.repeat(0,TotalTrials)
    ALLblocknum = np.repeat(0,TotalTrials)
    ALLblockEndIdx = np.repeat(0,TotalTrials)
    
    
    for bi in range(TotalBlocks):
        blocknum = np.repeat(bi+1,TrialsPerBlock) # Mark block number
        blockEndIdx = np.repeat(0,TrialsPerBlock)
        blockEndIdx[-1] = 1 # Mark when a block ends
        
        
        # trial sequence for each block
        # Make a flag for a while loop
        sflag =  False
        
        # Make sure stop signals appears maximum 4 trials in a row 
        while sflag == False:
            stims = [0,0,1] # 33% trials include stops signals
            rstims = np.repeat(stims,TrialsPerBlock/len(stims)) # Make 60 trials by repeating stims 20 times
            random.shuffle(rstims) # Shuffle trial sequence
            check=np.repeat(0,len(rstims)-4) # Define a matrix with 0s to check every 5 trials
            
            if any(rstims[0:3]) == 1: # First 3 trials should not be stop trials
                continue
            
            for i in range(len(rstims)-4):
                # Check every 5 trials to see how many stop trials are included
                check[i] = sum(rstims[i:i+5]) 
                
            if 5 in check: # If 5 consecutive trials, re-generate trials
                continue
            else: 
                sflag = True 
                
        
        arrows = np.repeat(0,len(rstims)) # Pre-define arrow
        init_arrow = [1,2] # Define types of arrows: 1=left; 2=right
        temp_arrows_stop = np.repeat(init_arrow, sum(rstims)/len(init_arrow)) # Counterbalance arrow type within stop trials
        temp_arrows_go = np.repeat(init_arrow, (len(rstims) - sum(rstims))/len(init_arrow)) # Counterbalance arrow type within GO trials
        random.shuffle(temp_arrows_stop) # Randomize arrow type for stop trials
        random.shuffle(temp_arrows_go) # Randomize arrow type for GO trials
        
        # Get stop signal indices
        stop_idx = [i for i, val in enumerate(rstims==1) if val] # Find stop trials
        go_idx = [i for i, val in enumerate(rstims==0) if val] # Find GO trials
        
        # Generate arrow sequence
        for ii in range(len(temp_arrows_stop)):
            arrows[stop_idx[ii]] = temp_arrows_stop[ii] # Insert arrow type for stop trials
        for ii in range(len(temp_arrows_go)):
            arrows[go_idx[ii]] = temp_arrows_go[ii] # Insert arrow type for GO trials
            
        
        ALLrstims[range((TrialsPerBlock*bi),(TrialsPerBlock*(bi+1)))] = rstims # Stack block-wise trial types 
        ALLarrows[range((TrialsPerBlock*bi),(TrialsPerBlock*(bi+1)))] = arrows # Stack block-wise arrow types 
        ALLblocknum[range((TrialsPerBlock*bi),(TrialsPerBlock*(bi+1)))] = blocknum # Stack block-wise block numbers 
        ALLblockEndIdx[range((TrialsPerBlock*bi),(TrialsPerBlock*(bi+1)))] = blockEndIdx
    
    if ( len(ALLrstims)+len(ALLblocknum)+len(ALLarrows) ) / 3 == 300:
        class trialseq:
            pass
        trialseq.blocknum = ALLblocknum
        trialseq.BlockEndIdx = ALLblockEndIdx
        trialseq.stop = ALLrstims
        trialseq.arrows = ALLarrows
        
    return(trialseq)

# This function generates instruction screen
def ShowInstructions():
    global window 
    
    # define instruction contents
    ins = visual.TextStim(win, height=.6, wrapWidth=25, color = 'black',pos=[0,0])
    ins.text ='You will perform a stop signal task. \n'
    ins.text += 'Press q to left arrow and p to right arrow as fast as possible! \n'
    ins.text += 'Sometimes arrow color will change into red. \n' 
    ins.text += 'If that happens please withhold your response. \n'
    ins.text += 'Making fast responses and stopping are equally important! \n'
    ins.text += 'Press any key to continue'
    
    # display until any inputs
    while not event.getKeys():
        ins.draw()
        win.flip()
    

# This function displays count down from 3 - 1 seconds

def CountDown():
    global window
    count3 = visual.TextStim(win, height=.6, wrapWidth=10, color = 'black',pos=[0,0])
    count2 = visual.TextStim(win, height=.6, wrapWidth=10, color = 'black',pos=[0,0])
    count1 = visual.TextStim(win, height=.6, wrapWidth=10, color = 'black',pos=[0,0])
    
    count3.text = 'Task will begin in 3 s'
    count2.text = 'Task will begin in 2 s'
    count1.text = 'Task will begin in 1 s'
    
    count3.draw()
    win.flip()
    core.wait(.5)
    count2.draw()
    win.flip()
    core.wait(.5)
    count1.draw()
    win.flip()
    core.wait(.5)

# This function runs experiment according to data stored in trialseq
# Input: experimental parameters (settings), trial sequence (trialseq), and subdata
# Output: Runs experiment

def RunTask(settings, trialseq, subdata):
    global window
    
    
    # Pre-define fixation, trial feedback
    fix = visual.TextStim(win, height=1, text = "+", wrapWidth=10, color = 'black',pos=[0,0])
    warning = visual.TextStim(win, text = "TOO SLOW!!!",height=.6, wrapWidth=10, color = 'red',pos=[0,0])
    BlockFeedback = visual.TextStim(win, height=.6, wrapWidth=25, color = 'black',pos=[0,0]) # Block feedback content will be filled later
    
    # Use shorter names for experimental parameters
    LeftSSD = settings.initSSD
    RightSSD = settings.initSSD
    stairsize = settings.staircase
    
    # Get current block data to provide feedback
    class blockdata:
        pass
    
    blockdata.arrow = []
    blockdata.resp = []
    blockdata.LeftSSD = []
    blockdata.RightSSD = []
    blockdata.RT = []
    blockdata.acc = []
    blockdata.DATA = []
    blockdata.GOidx = []
    blockdata.blockNum =[]
    
    # Get task onset
    task_start_time = core.getTime()
    
    for i in range(len(trialseq.stop)):
        # Reset clock
        kb.clock.reset()
        kb.clearEvents()
        
        # Get stopsignal depending on arrow type for the current trial
        StopSignal=[] # Reset stopsignal
        
        if trialseq.arrows[i] == 1: # If LEFT arrow, 
            arrow = settings.Larrow
            if trialseq.stop[i] ==1:
                StopSignal = settings.LarrowSTOP # StopSignal is LEFT red arrow
        else:
            arrow = settings.Rarrow
            if trialseq.stop[i] == 1: # If RIGHT arrow, 
                StopSignal = settings.RarrowSTOP # StopSignal is RIGHT red arrow
        
        # Get trial onset
        trial_onset = core.getTime()
        
        # Present fixation cross for 500 ms
        fix.draw()
        win.flip()
        core.wait(0.5)
        
        # Present GO stimulus
        arrow.draw()
        win.flip()
        
        # Get arrow onset
        arrow_onset = core.getTime()
        
        
        if trialseq.stop[i] ==0: # if currne trial is GO trial
            
            blockdata.GOidx = np.hstack((blockdata.GOidx,1)) # Mark this trial as GO in block data
            
            event.clearEvents() # Reset event que
            
            resp=None # reset response
            resp = event.waitKeys(maxWait=settings.arrowDuration, keyList=['q','p']) # Get response (deadline:1s)
            
            if resp: # if response was made
                RT = core.getTime() - arrow_onset # Check RT
                # Check accuaracy
                if trialseq.arrows[i] == 1: # if LEFT arrow
                    if resp == ['q']: # 'q' response is correct
                        acc=1
                    else: # else incorrect
                        acc=0
                elif trialseq.arrows[i] == 2:# if RIGHT arrow
                    if resp == ['p']: # 'p' response is correct
                        acc=1
                    else: # else incorrect
                        acc=0
                
                
                
            elif resp == None: # if no response
                acc = -1
                RT = 0 # enter impossible RT
                warning.draw()
                win.flip() # present warning screen
                core.wait(3 - (core.getTime() - trial_onset) ) # Maintain the trial duration of 3s
            
        else: # if current trial is STOP trial
            blockdata.GOidx = np.hstack((blockdata.GOidx,0)) # Mark this trial as STOP in block data
            event.clearEvents() # clear event que
            
            resp=None # reset response
            
            # SSD for current trial (separately for left and right reponse)
            if trialseq.arrows[i] == 1: # if left arrow, use leftSSD staircase
               core.wait(LeftSSD/1000) # convert ms to sec
            else: # if right arrow, use rightSSD staircase
               core.wait(RightSSD/1000) # convert ms to sec
            
            # After SSD, present stop signal (red arrow)
            StopSignal.draw()
            win.flip() # Replace black arrow into red arrow after certain SSD defined above
            ActualStopSignalDelay = core.getTime() - arrow_onset # Check actual SSD
            
            
            # Get response after stop signal JIC people respond to despite stop signal
            # Contingent on stop accuracy, update staircase tracking for left and right SSD
            
            if trialseq.arrows[i] == 1: # left SSD tracking 
                resp = event.waitKeys(maxWait=settings.arrowDuration-LeftSSD/1000, keyList=['q','p'])
                
                if trialseq.stop[i] == 1 and resp: #Failed Stop
                    acc=4
                    RT = core.getTime() - arrow_onset # Check RT
                    
                    # Make sure SSD does not go below zero
                    if LeftSSD >= stairsize:
                        LeftSSD = LeftSSD - stairsize
                    else:
                        LeftSSD = LeftSSD #if SSD goes below zero, maintain same SSD
                        
                elif trialseq.stop[i] == 1 and not resp: #Succesful Stop
                    acc=3
                    RT = 0
                    # Make sure SSD does not go below zero
                    LeftSSD = LeftSSD + stairsize
                    
            else: # right SSD tracking
                resp = event.waitKeys(maxWait=settings.arrowDuration-RightSSD/1000, keyList=['q','p'])
                
                if trialseq.stop[i] == 1 and resp: #Failed Stop
                    acc=4
                    RT = core.getTime() - arrow_onset # Check RT
                    
                    if RightSSD >= stairsize:
                        RightSSD = RightSSD - stairsize
                    else:
                        RightSSD = RightSSD
                    
                elif trialseq.stop[i] == 1 and not resp: # Succesful Stop
                    acc=3
                    RT = 0
                    
                    RightSSD = RightSSD + stairsize
        
        # Convert resp to number because I dont's want strings in my logfiles
        if resp == ['q']:
            resp = 1
        elif resp == ['p']:
            resp = 2
        else:
            resp = 0 
        
        # Store parameters and data after each trial in blockdata classs
        blockdata.RT = np.hstack((blockdata.RT,int(RT*1000)))
        blockdata.arrow = np.hstack((blockdata.arrow,trialseq.arrows[i]))
        blockdata.resp = np.hstack((blockdata.resp,resp))
        blockdata.blockNum = np.hstack((blockdata.blockNum,trialseq.blocknum[i]))
        blockdata.acc = np.hstack((blockdata.acc,acc))
        blockdata.LeftSSD = np.hstack((blockdata.LeftSSD,LeftSSD))
        blockdata.RightSSD = np.hstack((blockdata.RightSSD,RightSSD))
        
        # If not MISSED, present fixation during ITI
        if acc != -1:
            fix.draw()
            win.flip()
            core.wait(2.5 - (core.getTime() - trial_onset) )
        
        # If current trial is the end of current block, provide blockfeedback            
        if trialseq.BlockEndIdx[i] == 1:
            
            # Find GO trial RTs only and compute mean (failed stop trials have RTs too)
            STOPidx = blockdata.GOidx == 0 # Find STOP trial indices (boolean)
            MISSidx = blockdata.acc == -1 # Find MISSED GO trial indices (boolean)
            RJTidx = STOPidx+MISSidx # Include indices from both STOP and MISSED trials
            GOrtOnly = np.delete(blockdata.RT, np.where(RJTidx), 0) # Delete MISSED and STOP trial RT
            meanGOrt = np.mean(GOrtOnly) # Compute GO RT
            
            # Compute accuracy
            GOtrials = np.sum(blockdata.GOidx == 1) # Count # of entire GO trials
            CorrectGO = np.sum(blockdata.acc == 1) # Count # of correct GO trials
            
            # Compute probability of stopping = p(STOP)
            STOPtrials = np.sum(blockdata.GOidx == 0) # Count # of entire STOP trials
            SuccesfulStop = np.sum(blockdata.acc == 3) # Count # of all succesful stop trials
            
            # Generate block feedback
            BlockFeedback.text = "End of Block #"+str(trialseq.blocknum[i]) +"\n"
            BlockFeedback.text += "Mean GO RT : " + f"{meanGOrt:.2f}" + " ms" +"\n"
            BlockFeedback.text += "Accuracy : " + f"{CorrectGO/GOtrials*100:.2f}" + " %" +"\n" # display  2 digits after decimal point
            BlockFeedback.text += "p(STOP) : " + f"{SuccesfulStop/STOPtrials*100:.2f}" + " %" +"\n" # display  2 digits after decimal point
            
            # Combine all parameters and data into a matrix structure (Yes I am so used to matlab)
            temp = []
            temp = np.hstack([blockdata.blockNum.reshape(-1,1), abs(blockdata.GOidx-1).reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.arrow.reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.resp.reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.LeftSSD.reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.RightSSD.reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.acc.reshape(-1,1)] )
            temp = np.hstack( [temp, blockdata.RT.reshape(-1,1)] )
            
            # Stack block-wise data on top of previous block data
            if trialseq.blocknum[i] == 1:
                blockdata.DATA = temp # At the first block, can't stack due to emptiness of the variable
            else:
                blockdata.DATA = np.vstack([blockdata.DATA,temp])
            
            # Save logfile after each block
            np.savetxt(settings.outfile, blockdata.DATA, \
            header="Block,TrialType,Arrow,Response,leftSSD,rightSSD,ACC,RT", \
            fmt='%4i', delimiter=',', footer = subdata[0]+","+subdata[1]+","+subdata[2]+","+subdata[3])
            
            # Present block feedback
            while not event.getKeys():
                BlockFeedback.draw()
                win.flip()
            
            # Displays different performance feedback contingent on stopping performance
            if trialseq.blocknum[i] < 5:
                PerformanceFeedack = visual.TextStim(win, height=.6, wrapWidth=25, color = 'black',pos=[0,0])
                if SuccesfulStop/STOPtrials <= .45:
                    PerformanceFeedack.text = "Your are doing great in terms of making fast responses. \n"
                    PerformanceFeedack.text += "However, you are not stopping accurately. \n"
                    PerformanceFeedack.text += "Please concentrate more on stopping on the next block! \n"
                    PerformanceFeedack.text += "Thanks."
                    
                elif SuccesfulStop/STOPtrials >= .55:
                    PerformanceFeedack.text = "Your are doing great in terms of stopping. \n"
                    PerformanceFeedack.text += "However, your response time is too slow. \n"
                    PerformanceFeedack.text += "Please concentrate more on making fast responses on the next block! \n"
                    PerformanceFeedack.text += "Thanks."
                else:
                    PerformanceFeedack.text = "Your are doing great! \n" 
                    PerformanceFeedack.text += "Keep doing what you've been doing!"
                # Present performance feedback
                while not event.getKeys():
                    PerformanceFeedack.draw()
                    win.flip()
                    
                # Reset block-wise data if current block is not the last one
                blockdata.arrow = []
                blockdata.resp = []
                blockdata.LeftSSD = []
                blockdata.RightSSD = []
                blockdata.RT = []
                blockdata.acc = []
                blockdata.GOidx = []
                blockdata.blockNum = []
                
                # Count down begins again 
                CountDown()
            
            
            


# After completion of the last block, close everything!
def TerminateTask():
    global widow
    
    outro = visual.TextStim(win, height=.6, wrapWidth=25, color = 'black',pos=[0,0])
    outro.text = "Thanks for participation!"
    
    while not event.getKeys():
        outro.draw()
        win.flip()
    
    win.close()
    core.quit()


subdata=SubjectInformation()
Initialize(subdata)
ShowInstructions()
CountDown()
trialseq=GenSequence(settings)
print(trialseq.stop)
RunTask(settings, trialseq, subdata)
TerminateTask()