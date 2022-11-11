###############################################################################
## Steve Reich - Piano Phase (1967)
## Extended to full score from
## https://git.sr.ht/~marcevanstein/music.py/tree/master/item/musicShort7.py
## by M. Selim Yavuz
## 2022-11-11
###############################################################################
from scamp import * # for all the playing
import numpy as np # for math stuff

##################################GLOBAL VARS##################################
## piece range: E4-E5
E4 = 64; F4 = 65; Fs4 = 66; G4 = 67; Gs4 = 68; A4 = 69; As4 = 70; B4 = 71;
C5 = 72; Cs5 = 73; D5 = 74; Ds5 = 75; E5 = 76;
###############################################################################

## first melody:  E4>Fs4>B4>Cs5>D5>Fs4>E4>Cs5>B4>Fs4>D5>Cs5 (12 notes)
melody1 = [E4, Fs4, B4, Cs5, D5, Fs4, E4, Cs5, B4, Fs4, D5, Cs5]
## second melody: E4>Fs4>B4>Cs5>D5>Fs4>B4>Cs5 (8 notes)
melody2 = [E4, Fs4, B4, Cs5, D5, Fs4, B4, Cs5]
## third melody: E4>E5>A4>B4>D5>E5>A4>B4 (8 notes)
melody3 = [E4, E5, A4, B4, D5, E5, A4, B4]
## fifth melody:  A4>B4>D5>E5 (4 notes)
melody4 = melody3[2:6] # it's a subset of the third melody
## main tempo
tempo1 = 114 # tempo 1
###############################################################################

###################################FUNC DEFS###################################
def piano_part(session, which_piano, repeats, amp, melody, piano_num, op):
    i = 0
    while i < repeats:
        currentAmp = amp[i]
        print(f"Piano #{piano_num} playing iteration #{i+1} for melody {melody}, repeating for total {repeats} times")
        if op == "su" and piano_num == 2 and (i + 1) == repeats:
            melody = melody + [melody[0]]
        for pitch in melody:
            which_piano.play_note(pitch, currentAmp, 0.25)
        i += 1

def speedUp(session, section_su, piano1, piano2, melody_1, melody_2, repeatMin, repeatMax):
    #melodicShift = section_su - 2
    repeats = np.random.randint(repeatMin, repeatMax)
    ampCurve = [1.0]*repeats # same dynamics
    beatNum = len(melody_1)*repeats
    ## calculate tempo to get ahead by 1 note
    targetTempo = (tempo1 / beatNum) * (beatNum + 1)
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve, melody_1, 1, "su"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve, melody_2, 2, "su"))
    clock2.set_tempo_target(targetTempo, beatNum)
    wait_for_children_to_finish()

    melodyNew = melody_2[1:] + melody_2[:1]

    return melodyNew

def holding(session, section_hld, piano1, piano2, melody_1, melody_2, repeatMin, repeatMax):
    repeats = np.random.randint(repeatMin, repeatMax)
    ampCurve = [1.0]*repeats # same dynamics
    melodicShift = section_hld - 2
    melodyNew = melody_2[melodicShift:] + melody_2[:melodicShift]
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve, melody_1, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve, melodyNew, 2, "hld"))
    wait_for_children_to_finish()
###############################################################################

###################################MAIN FUNC###################################
def main():
    ## session with a soundfont with better piano and a nice tempo
    session = Session(tempo = tempo1,
                        default_soundfont = "Essential Keys-sforzando-v9.6.sf2")
    # soundfont: https://drive.google.com/file/d/1VZkoiVOonffpJWxZah-AdQkxaTFIzZ6q/view?usp=sharing
    # s.print_default_soundfont_presets() # see what's in the font
    # session.fast_forward_in_beats(1900) ## REMOVE THIS, FOR TEST PURPOSES ONLY
    ## two pianos with a nice concert grand sound
    piano1 = session.new_part("Yamaha C5 Grand")
    piano2 = session.new_part("Yamaha C5 Grand")

    print("######################## Section 1 #########################")
    print("############## Piano #1 begins with melody #1 ##############")
    section = 1
    repeats = np.random.randint(4, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody1, 1, "hld"))
    wait_for_children_to_finish()

    print("#################### Section 2, Part 1 ######################")
    print("############# Piano #2 fades in with melody #1 ##############")
    section += 1
    repeats = np.random.randint(12, 18)
    ampCurve1 = [1.0]*repeats # same dynamics
    crescendoSteps = list(np.arange(4, 11, 1)) # define crescendo steps, finish crescendo in 7 repeats
    addAmpForNotes = [1.0] * (repeats-len(crescendoSteps))
    ampCurve2 = list(np.log10(crescendoSteps)) # make it logarithmic so that amp increases faster
    ampCurve2 = ampCurve2 + addAmpForNotes # max amp beyond 10 notes
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody1, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve2, melody1, 2, "hld"))
    wait_for_children_to_finish()

    i = 0
    melodyNew = melody1 # initialize new melody for the iterations
    ###########MAIN LOOP FROM SECTION 2, PART 2 TO SECTION 13, PART 1###########
    while i < 11:
        section += 1
        speedRepeatMin = 4
        speedRepeatMax = 16
        if section < 9:
            holdRepeatMin = 16
            holdRepeatMax = 24
        else:
            holdRepeatMin = 12
            holdRepeatMax = 24

        print(f"#################### Section {section-1}, Part 2 ######################")
        print("############## Piano #2 speeds up to get ahead ##############")
        melodyNew = speedUp(session, section, piano1, piano2, melody1, melodyNew, speedRepeatMin, speedRepeatMax)

        print(f"#################### Section {section}, Part 1 ######################")
        print("############ Everyone holds with melody shifted #############")
        holding(session, section, piano1, piano2, melody1, melody1, holdRepeatMin, holdRepeatMax)
        i += 1
    ############################################################################
    section += 1
    print(f"#################### Section {section-1}, Part 2 ######################")
    print("############## Piano #2 speeds up to get ahead ##############")
    melodyNew = speedUp(session, section, piano1, piano2, melody1, melodyNew, 4, 16)

    print(f"#################### Section {section}, Part 1 ######################")
    print("### Everyone holds with melody now aligned and piano #2 fades out ###")
    repeats = np.random.randint(4, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    decrescendoSteps = list(np.arange(11, 0, 2)) # define decrescendo steps, finish crescendo in 7 repeats
    addAmpForNotes = [0] * (repeats-len(decrescendoSteps))
    ampCurve2 = decrescendoSteps + addAmpForNotes # max amp beyond 10 notes
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody1, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve2, melody1, 2, "hld"))
    wait_for_children_to_finish()
    ##############################MELODY 1 OVER#################################

    #############################MELODY 2-3 SECT################################
    print("######################## Section 15 #########################")
    print("################# Piano #1 repeats melody #1 ################")
    section += 1
    repeats = np.random.randint(4, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody1, 1, "hld"))
    wait_for_children_to_finish()

    print("######################## Section 16 #########################")
    print("############## Piano #1 begins with melody #2 ##############")
    section += 1
    shift = 1
    repeats = np.random.randint(6, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody2, 1, "hld"))
    wait_for_children_to_finish()

    print("#################### Section 17, Part 1 ######################")
    print("############# Piano #2 fades in with melody #3 ##############")
    section += 1
    shift += 1
    repeats = np.random.randint(16, 32)
    ampCurve1 = [1.0]*repeats # same dynamics
    crescendoSteps = list(np.arange(4, 11, 1)) # define crescendo steps, finish crescendo in 7 repeats
    addAmpForNotes = [1.0] * (repeats-len(crescendoSteps))
    ampCurve2 = list(np.log10(crescendoSteps)) # make it logarithmic so that amp increases faster
    ampCurve2 = ampCurve2 + addAmpForNotes # max amp beyond 10 notes
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve1, melody2, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve2, melody3, 2, "hld"))
    wait_for_children_to_finish()

    melodyNew = melody3 # initialize new melody for the iterations
    #################################MAIN LOOP##################################
    while section < 24:
        section += 1
        shift +=1
        speedRepeatMin = 6
        speedRepeatMax = 18
        if section < 24:
            holdRepeatMin = 16
            holdRepeatMax = 32
        else:
            holdRepeatMin = 8
            holdRepeatMax = 24

        print(f"#################### Section {section-1}, Part 2 ######################")
        print("############## Piano #2 speeds up to get ahead ##############")
        melodyNew = speedUp(session, shift, piano1, piano2, melody2, melodyNew, speedRepeatMin, speedRepeatMax)

        print(f"#################### Section {section}, Part 1 ######################")
        print("############ Everyone holds with melody shifted #############")
        holding(session, shift, piano1, piano2, melody2, melody3, holdRepeatMin, holdRepeatMax)
    ############################################################################
    section += 1
    shift += 1
    print(f"#################### Section {section-1}, Part 2 ######################")
    print("############## Piano #2 speeds up to get ahead ##############")
    melodyNew = speedUp(session, shift, piano1, piano2, melody2, melodyNew, 6, 18)

    print(f"####################### Section {section} #########################")
    print("### Everyone holds with melody now aligned and piano #1 fades out ###")
    repeats = np.random.randint(4, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    decrescendoSteps = list(np.arange(11, 0, 2)) # define decrescendo steps
    addAmpForNotes = [0] * (repeats-len(decrescendoSteps))
    ampCurve2 = decrescendoSteps + addAmpForNotes # max amp beyond 10 notes
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve2, melody2, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve1, melody3, 2, "hld"))
    wait_for_children_to_finish()
    ##############################MELODY 2-3 OVER#################################

    ##############################MELODY 4 SECT#################################
    print("######################## Section 26 #########################")
    print("################# Piano #2 repeats melody #4 ################")
    section += 1
    repeats = np.random.randint(4, 8)
    ampCurve1 = [1.0]*repeats # same dynamics
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve1, melody3, 2, "hld"))
    wait_for_children_to_finish()

    print("######################## Section 26a ########################")
    print("################## Piano #2 plays two notes #################")
    clock2 = session.fork(piano_part, args=(session, piano2, 1, [1.0, 1.0], melody3[0:2], 2, "hld"))
    wait_for_children_to_finish()

    print("######################## Section 27 #########################")
    print("############### Piano #2 begins with melody #4 ##############")
    section += 1
    shift = 1
    repeats = np.random.randint(8, 24)
    ampCurve1 = [1.0]*repeats # same dynamics
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve1, melody4, 2, "hld"))
    wait_for_children_to_finish()

    print("#################### Section 28, Part 1 ######################")
    print("############## Piano #1 fades in with melody #4 ##############")
    section += 1
    shift += 1
    repeats = np.random.randint(16, 32)
    ampCurve1 = [1.0]*repeats # same dynamics
    crescendoSteps = list(np.arange(4, 11, 1)) # define crescendo steps, finish crescendo in 7 repeats
    addAmpForNotes = [1.0] * (repeats-len(crescendoSteps))
    ampCurve2 = list(np.log10(crescendoSteps)) # make it logarithmic so that amp increases faster
    ampCurve2 = ampCurve2 + addAmpForNotes # max amp beyond 10 notes
    clock1 = session.fork(piano_part, args=(session, piano1, repeats, ampCurve2, melody4, 1, "hld"))
    clock2 = session.fork(piano_part, args=(session, piano2, repeats, ampCurve1, melody4, 2, "hld"))
    wait_for_children_to_finish()

    #################################MAIN LOOP##################################
    melodyNew = melody4 # init
    while section < 31:
        section += 1
        shift +=1
        speedRepeatMin = 16
        speedRepeatMax = 32
        holdRepeatMin = 48
        holdRepeatMax = 60

        print(f"#################### Section {section-1}, Part 2 ######################")
        print("############## Piano #2 speeds up to get ahead ##############")
        melodyNew = speedUp(session, shift, piano1, piano2, melody4, melodyNew, speedRepeatMin, speedRepeatMax)

        print(f"#################### Section {section}, Part 1 ######################")
        print("############ Everyone holds with melody shifted #############")
        holding(session, shift, piano1, piano2, melody4, melody4, holdRepeatMin, holdRepeatMax)

    ############################################################################
    section += 1
    shift += 1
    print(f"################## Section {section-1}, Part 2 #####################")
    print("################# Piano #2 speeds up to get ahead ###################")
    melodyNew = speedUp(session, shift, piano1, piano2, melody4, melodyNew, 16, 32)

    print(f"####################### Section {section} ##########################")
    print("############## Pianos, now aligned, finish the piece ################")
    holding(session, shift, piano1, piano2, melody4, melody4, 24, 48)
    ##################################PIECE END#################################
    return 0

if __name__=="__main__":
    main()
