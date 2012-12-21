python-BLICK
============

Python-BLICK is a Python implementation of BLICK (a phonotactic probability calculator for English), originally implemented in Visual Basic by Professor Bruce Hayes.  The original version can be found at http://www.linguistics.ucla.edu/people/hayes/BLICK/.

Phonotactic probability refers to a property of a string of segments, such as a word or nonword.  Strings with high phonotactic probability align with a language's phonotactics more closely than words with low phonotactic probability.  For instance, the titular nonword blick is highly probable given the phonotactics of English, but the nonword bnick is highly improbable as bn onsets are banned.

BLICK calculates the phonotactic probability of a string of phonological segments using weighted constraints.  The phonotactic probability scores are summations of all violations of constraints across the string.  Further discussion of how BLICK calculates phonotactic probability on the original version's website.

Typical usage
=============

    from blick import BlickLoader

    b = BlickLoader()

    #Evaluating single strings of phones

    score = b.assessWord("T EH1 S T") #Probable string
    
    score = b.assessWord("AH0 S NG IY1 R Y EH1 S T") #Improbable string

    #Evaluating a text file of strings of phones

    b.assessFile("/path/to/input/file")
