'''
Created on 2012-10-02

@author: michael
'''
import os


class BlickLoader:
    def __init__(self,grammarType="default",debug=False):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.debug = debug
        if debug:
            #print "Debugging mode enabled."
            #print "Creating log file"
            self.initLog()

        if debug:
            self.updatelogfile("Loading syllabification information...")
        from blick.syllabification import ONSETS,VOWELS
        self.onsets = ONSETS
        self.vowels = VOWELS

        if debug:
            self.updatelogfile("Loading grammar...")
        if grammarType == 'HayesWhite':
            from blick.grammars import hayesWhiteConstraints as constraints
        elif grammarType == 'NoStress':
            from blick.grammars import noStressConstraints as constraints
        else:
            from blick.grammars import defaultConstraints as constraints
        self.grammar = constraints
        if debug:
            self.updatelogfile("Loading natural classes...")
        if grammarType == 'HayesWhite':
            from blick.naturalClasses import hayesWhiteNC as nc
        elif grammarType == 'NoStress':
            from blick.naturalClasses import noStressNC as nc
        else:
            from blick.naturalClasses import defaultNC as nc
        self.segMapping = nc
        if debug:
            self.updatelogfile("Done initializing!")

    def initLog(self):
        f = open(os.path.join(self.basedir,"PyBlickLog.txt"),'w')
        f.write("Begin operation\n")
        f.close()

    def updatelogfile(self,linetowrite):
        f = open(os.path.join(self.basedir,"PyBlickLog.txt"),'a')
        f.write(linetowrite+"\n")
        f.close()

    #def _loadOnsets(self):
    #    f = open(os.path.join(self.basedir,"Syllabification","Onsets.txt")).read().splitlines()
    #    return set(f)

    #def _loadVowels(self):
    #    f = open(os.path.join(self.basedir,"Syllabification","Vowels.txt")).read().splitlines()
    #    return set(f)

    #def _loadGrammar(self,grammarType):
    #    if grammarType == 'custom':
    #        fileName = 'CustomGrammar.txt'
    #    elif grammarType == 'HayesWhite':
    #        fileName = 'HayesWhiteGrammar.txt'
    #    elif grammarType == 'NoStress':
    #        fileName = 'NoStressGrammar.txt'
    #    else:
    #        fileName = 'DefaultGrammar.txt'
    #    f = open(os.path.join(self.basedir,"Grammars",fileName)).read().splitlines()
    #    cons = []
    #    for i in range(len(f)):
    #        if self.debug:
    #            if i % 50 == 0:
    #                self.updatelogfile(" ".join(['Added constraint',str(i),'of',str(len(f))]))
    #        cons.append(Constraint(f[i]))
    #    return cons

    #def _loadNaturalClasses(self,grammarType):
    #    if grammarType == 'custom':
    #        fileName = 'NaturalClassesForCustomGrammar.txt'
    #    elif grammarType == 'HayesWhite':
    #        fileName = 'NaturalClassesForHayesWhiteGrammar.txt'
    #    elif grammarType == 'NoStress':
    #        fileName = 'NaturalClassesForNoStressGrammar.txt'
    #    else:
    #        fileName = 'NaturalClassesForDefaultGrammar.txt'
    #    f = open(os.path.join(self.basedir,"Grammars",fileName)).read().splitlines()
    #    for i in range(len(f)):
    #        if self.debug:
    #            if i % 50 == 0:
    #                self.updatelogfile(" ".join(['Processed natural class',str(i),'of',str(len(f))]))
    #        l = f[i].split("\t")
    #        segs = l[-1].split(",")
    #        feats = l[0].split(": ")[-1].split(",")
    #        for s in segs:
    #            if s in self.segMapping:
    #                self.segMapping[s] = self.segMapping[s] | set(feats)
    #            else:
    #                self.segMapping[s] = set(feats)
        #This gives a segment to feature set mapping that includes any feature that corresponds to
        #a segment across all the natural class definitions

    def _syllabify(self,inputword):
        segs = inputword.split(" ")
        seglist = []
        cons = []
        #Convert the segment list into a list of Vowels and Consonant lists
        for i in range(len(segs)-1):
            if segs[i] in self.vowels:
                seglist.append(segs[i]) #Vowels appended as strings
            else:
                cons.append(segs[i]) #Consonant(s) are appended as lists
                if segs[i+1] in self.vowels:
                    seglist.append(cons)
                    cons=[]
        #Deal with leftover segment at the end
        if cons != []:
            seglist.append(cons)
        if type(seglist[-1]) is not list:
            if segs[-1] in self.vowels:
                seglist.append(segs[-1])
            else:
                seglist.append([segs[-1]])
        else:
            if segs[-1] in self.vowels:
                seglist.append(segs[-1])
            else:
                seglist[-1].append(segs[-1])
        #At this point, seglist should look like: [['C','C'],'V',['C'],'V','V']
        #Make Consonants either onsets or codas
        returnlist = []
        VowAdded = False #Tracks whether the first vowel is present
        for i in range(len(seglist)):
            s = seglist[i]
            if type(s) is not list: #Append vowels as is
                returnlist.append(s)
                VowAdded = True
                continue
            if not VowAdded: #If a vowel hasn't been found yet, everything is an onset
                for o in s:
                    returnlist.append(o)
                continue
            if i != len(seglist)-1:
                for j in range(len(s)):
                    if " ".join(s[j:]) in self.onsets: #Look for maximal acceptable onsets
                        for c in s[:j]: #Whatever comes before the maximal onset is a coda
                            returnlist.append(c+"Coda")
                        for o in s[j:]:
                            returnlist.append(o)
                        continue
                    for c in s:
                        returnlist.append(c+"Coda")
            else: #All consonants at the end are codas
                for c in s:
                    returnlist.append(c+"Coda")
        return returnlist



    def assessWord(self,inputword,includeConstraints=False):
        segs = self._syllabify(inputword) #Syllabify segments
        segs = ["#"] + segs + ["#"]
        f = [] #Convert segments into feature sets
        for s in segs:
            f.append(self.segMapping[s])
        score = 0.0
        cons = []
        #For each constraint, evaluate the word and sum scores on each constraint
        for c in self.grammar:
            cScore = c.assess(f)
            if cScore != 0.0:
                score += cScore
                cons.append(str(c))
        if includeConstraints:
            return score,cons
        return score

    def assessFile(self,path,outpath=None,includeConstraints=False):
        if self.debug:
            self.updatelogfile(" ".join(["Assessing",os.path.abspath(path)]))
        inputF = open(path).read().splitlines()
        if self.debug:
            self.updatelogfile(" ".join(["Creating output file",os.path.abspath(outpath)]))
        if outpath is None:
            mod = os.path.split(path)
            outpath = os.path.join(mod[0],mod[1].replace(".","-output."))
        outputF = open(outpath,'w')
        outlines = []
        for i in range(len(inputF)):
            if self.debug:
                if i % 50 == 0:
                    self.updatelogfile(" ".join(['Done with item',str(i),'of',str(len(inputF))]))
            line = inputF[i].split("\t")
            segs = line[0].strip()
            outline = [segs]
            if includeConstraints:
                score,cons = self.assessWord(segs,includeConstraints=True)
                outline.extend([str(score),','.join(cons)])
            else:
                score = self.assessWord(segs)
                outline.append(str(score))
            outputF.write("\t".join(outline+line[1:]))
            outputF.write("\n")
        outputF.close()
        if self.debug:
            self.updatelogfile(" ".join(["Finished assessing",os.path.abspath(path)]))

class Constraint:
    def __init__(self,textdesc,score,tier='default'):
        self.score = score
        self.tier = tier
        if self.tier == "Main": #Features that determine inclusion in a tier
            self.tierFeats = set(['+mainstress'])
        elif self.tier == "Stress":
            self.tierFeats = set(['+stress'])
        elif self.tier == "Syllable":
            self.tierFeats = set(['+syllabic'])
        else:
            self.tierFeats = set([])
        #Convert description of constraint into feature sets
        desc = textdesc.split("][")
        self.description = []
        for i in desc:
            self.description.append(set(i.replace("]","").replace("[","").split(",")))

    #def _convertOriginalTextFiles(self,line):
    #    l = line.split("\t")
    #    score = float(l[-1])
    #    tier = l[1].replace("(tier=","").replace(")","")
    #    #Convert description of constraint into feature sets
    #    des = l[0].replace("*","").split("][")
    #    description = []
    #    for i in des:
    #        description.append(set(i.replace("]","").replace("[","").split(",")))
    #    return description,score,tier


    def _getTierSegs(self,segs):
        tierSegs = []
        for s in segs:
            if s >= self.tierFeats or s == set(['+word_boundary']):
                tierSegs.append(s)
        return tierSegs

    def assess(self,segs):
        if self.tier != 'default': #Only look at segments relevant for a tier
            segs = self._getTierSegs(segs)
        wLength = len(self.description)
        if wLength > 1: #Create all possible comparisons based on window length of constraint
            assessList = [segs[i:i+wLength] for i in range(len(segs)-(wLength-1))]
        else:
            assessList = [segs[i:i+1] for i in range(len(segs)-1)]
        score = 0.0
        for w in assessList:
            match = True
            for i in range(wLength): #Compare all feature sets of a constraint to the corresponding feature sets of segments
                #If the constraint feature sets are not subsets of the segment feature set
                #then that comparison doesn't meet constraint criteria
                if len(self.description[i] - w[i]) != 0:
                    match = False
                    break
            if match: #For each match, find the product of number of instances and the score
                score += self.score
        return score

    def writeDescription(self):
        output = ''
        for x in self.description:
            output += '['
            output += ','.join(x)
            output += ']'
        return output

    def __str__(self): #Recreate string description of constraint
        output = '*'
        output += self.writeDescription()
        output += ' ('+str(self.score)+')'
        if self.tier != 'default':
            output += ' ('+ self.tier+" tier)"
        return output



#if __name__ == "__main__":
#    b = BlickLoader()

    #print b.assessWord("T EH1 S T")
    #print b.assessWord("AH0 S NG IY1 R Y EH1 S T")
#    b.assessFile("/home/michael/dev/LingTools/BLICK/Input/Simple.txt")



