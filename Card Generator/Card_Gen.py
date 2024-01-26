"""
https://docs.google.com/spreadsheets/d/1iKW1hRCv8PiR5Vgn4LiQMnJYzdpoxzDtPpbgXMK67N0/edit

Mode 1:
Inputs; dropdowns for each "Effect" with an input for the "Value" as displayed on the excel
Outputs; power level using the modifier value, only 1 output no need for multiples
Order of operations: Additives -> Multipliers -> AP Cost -> Power Level

Mode 2:
Inputs; power level range XOR (AP Cost & cooldown), number of cards to generate
Outputs; a number of cards that list their effects that fit the criteria

Weighted list of effects to randomly choose from
AOE must have only 1 target, vise versa, a card with more than one target cannot be AOE

AP Cost
Cooldown
Damage Dice
Heal
Negative Condition: Slow
Negative Condition: Weaken
Negative Condition: Vulnerable
Negative Condition: Immobilize
Negative Condition: Suppress
Positive Condition: Focus
Positive Condition: Fortify
Positive Condition: Ward
Targets
Number of Squares Affected
Range
Movement
Flying Movement
Forced Movement
"""

import tkinter as tk
from tkinter import ttk
from functools import partial
    
# Create the root window
root = tk.Tk()
root.title("Matt's Board Game App")
WIDTH = 300
HEIGHT = 490
root.geometry(str(WIDTH) + "x" + str(HEIGHT))
root.resizable(False, False)
# Create the Notebook
notebook = ttk.Notebook(root)

# Create object frames for each notebook tab
frame_GeneratePowerLevel = tk.Frame(notebook)
frame_GenerateCards = tk.Frame(notebook)
# Create additional frames
frame_NegativeConditions = tk.Frame(frame_GeneratePowerLevel)
frame_PositiveConditions = tk.Frame(frame_GeneratePowerLevel)
conditionFrames = [frame_NegativeConditions, frame_PositiveConditions]
frame_PowerLevel = tk.Frame(frame_GeneratePowerLevel)

# Config for frames
frame_GeneratePowerLevel.config(width=WIDTH, height=HEIGHT)
frame_GeneratePowerLevel.grid_propagate(False)
frame_GeneratePowerLevel.grid_columnconfigure(0, weight=1)
frame_NegativeConditions.grid_columnconfigure(0, weight=1)
frame_PositiveConditions.grid_columnconfigure(0, weight=1)
frame_PowerLevel.grid_columnconfigure(0, weight=1)
frame_NegativeConditions.grid(row=5, column=0, columnspan=2, sticky="nsew")
frame_PositiveConditions.grid(row=7, column=0, columnspan=2, sticky="nsew")
frame_PowerLevel.grid(row=16, column=0, columnspan=3, sticky="ew")


# Add the frames to the notebook as tabs
notebook.add(frame_GeneratePowerLevel, text='Generate Power Level')
notebook.add(frame_GenerateCards, text='Generate Cards')

# Pack the Notebook
notebook.pack(expand=True, fill='both')

effectData = {
    "AP_Cost":{"label":"AP Cost", "type":"additive_final", "value":{1:0, 2:-1, 3:-3, 4:-6, 5:-10}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=1), "row":0, "column":0},
    "Cooldown":{"label":"Cooldown", "type":"multiplier", "value":{1:1, 2:0.5, 3:0.25}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=1), "row":1, "column":0},
    "Damage_Dice":{"label":"Damage Dice", "type":"additive", "value":{0:0, 1:0.5, 2:1, 3:1.5, 4:2, 5:3}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":2, "column":0},
    "Heal_Dice":{"label":"Heal Dice", "type":"additive", "value":{0:0, 1:1, 2:2, 3:3, 4:4, 5:5}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":3, "column":0},
    "Negative_Condition":{"label":"Negative Condition", "type":"additive_condition", "value":{"None":0, "Slow":1, "Weaken":1, "Vulnerable":1.5, "Immobilize":1.5, "Suppress":3}, "frame":frame_GeneratePowerLevel, "currentValue":tk.StringVar(value="None"),  "row":4, "column":0},
    "Positive_Condition":{"label":"Positive Condition", "type":"additive_condition", "value":{"None":0, "Focus":0.5, "Fortify":1.5, "Ward":2}, "frame":frame_GeneratePowerLevel, "currentValue":tk.StringVar(value="None"), "row":6, "column":0},
    "Targets":{"label":"Targets", "type":"multiplier", "value":{1:1, 2:2, 3:3.5, 4:5, 5:7}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=1), "row":8, "column":0},
    "Squares_Affected":{"label":"Squares Affected", "type":"additive", "value":{1:0, 2:1.5, 3:3, 4:4, 5:5.5, 6:7, 7:8.5}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=1), "row":9, "column":0},
    "Range":{"label":"Range", "type":"additive", "value":{0:0, 1:1, 2:2, 3:2.5, 4:3, 5:3.5, 6:4}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":10, "column":0},
    "Movement":{"label":"Movement", "type":"additive", "value":{0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":11, "column":0},
    "Flying_Movement":{"label":"Flying Movement", "type":"additive", "value":{0:0, 2:3, 3:4.5, 4:6, 5:7, 6:8}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":12, "column":0},
    "Forced_Movement":{"label":"Forced Movement", "type":"additive", "value":{0:0, 1:1, 2:1.5, 3:2}, "frame":frame_GeneratePowerLevel, "currentValue":tk.IntVar(value=0), "row":13, "column":0} 
}

powerLevelUtility = {
    "Power_Level":{"label":"Power Level:      0", "tkWigit":tk.Label(), "frame":frame_PowerLevel, "row":0, "column":0},
}

conditions = {
    "Negative":[],
    "Positive":[]
}

def addInnerConditionFrame(type, frame, *args):
    frame_conditions_inner = tk.Frame(frame)
    frame_conditions_inner.grid_columnconfigure(0, weight=1)
    frame_conditions_inner.grid(row=len(conditions[type]), column=1, columnspan=2, sticky="ew")

    lbl_condition = tk.Label(frame_conditions_inner, text=conditions[type][-1])
    lbl_condition.grid(row=len(conditions[type]), column=0)
    lbl_condition.config(justify="left")
    lbl_condition.config(width=12, anchor="w")
    
    button_removeEffect = tk.Button(frame_conditions_inner, text="X", command=partial(removeCondition, type, frame, conditions[type][-1]))
    button_removeEffect.grid(row=len(conditions[type]), column=1)
    button_removeEffect.config(anchor="e")

def addCondition(type, frame, *args): 
    # Get the new condition from the dropdown
    newCondition = effectData[type+"_Condition"]["currentValue"].get()
    if newCondition != "None" and newCondition not in conditions[type]:
        if len(conditions[type]) == 0:
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=5 if type == "Negative" else 7, column=0, columnspan=2, sticky="nsew")
            
        conditions[type].append(newCondition)
        lbl_numCondition = tk.Label(frame, text=type+" Condition "+str(len(conditions[type])))
        lbl_numCondition.grid(row=len(conditions[type]), column=0, sticky="w")
        
        addInnerConditionFrame(type, frame)
        root.geometry(str(WIDTH) + "x" + str(HEIGHT+23*len(conditions["Negative"])+23*len(conditions["Positive"])))

effectData["Negative_Condition"]["currentValue"].trace("w", partial(addCondition, "Negative", frame_NegativeConditions))
effectData["Positive_Condition"]["currentValue"].trace("w", partial(addCondition, "Positive", frame_PositiveConditions))


def initPowerLevelLabels():    
    for effect in effectData:
        effectDict = effectData[effect]
        label = tk.Label(effectDict["frame"], text=effectDict["label"] + ":")
        label.grid(row=effectDict["row"], column=effectDict["column"], sticky="w")
        label.config(width=15, justify="left", anchor="w")
    
    for utility in powerLevelUtility:
        wigit = powerLevelUtility[utility]
        wigit_type = wigit["tkWigit"].winfo_class()
        if wigit_type == "Label":
            label = tk.Label(wigit["frame"], text=wigit["label"])
            label.grid(row=wigit["row"], column=wigit["column"], sticky="w")
            label.config(width=20, justify="left", anchor="w")
            wigit["tkWigit"] = label
        

def initPowerLevelDropdowns():
    for effect in effectData:
        # Set the default value of the dropdown to the first key in the value dictionary
        effectData[effect]["currentValue"].set(list(effectData[effect]["value"].keys())[0])
        dropdownOptions = []
        for value in effectData[effect]["value"]: # Add keys to the dropdown's option list
            dropdownOptions.append(value)
        # Create the dropdown, place in frame, and set its config values
        dropdown = tk.OptionMenu(effectData[effect]["frame"], effectData[effect]["currentValue"], *dropdownOptions)
        dropdown.grid(row=effectData[effect]["row"], column=effectData[effect]["column"]+1, sticky="e")
        dropdown.config(width=10, anchor="e", justify="right")
        # Store dropdown in the effect's dictionary
        effectData[effect]["dropdown"] = dropdown

def removeCondition(type, frame, condition):
    # Find the row number of the condition
    row = conditions[type].index(condition) + 1  # Adding 1 because grid row numbers start from 1
    # Get the widgets in the row
    widgets = frame.grid_slaves(row=row)
    # Call destroy on each widget
    for widget in widgets:
        widget.destroy()

    # Remove the condition from the list
    conditions[type].remove(condition)

    # Shift up the rows by looping from the current row down
    for i in range(row, len(conditions[type]) + 2):  # Adding 2 because grid row numbers start from 1 and we want to include the last row
        widgets = frame.grid_slaves(row=i)
        for widget in widgets:
            # Get the current grid options
            options = widget.grid_info()
            # Remove the widget from the grid
            widget.grid_forget()
            # Re-grid the widget to the new position
            widget.grid(row=options["row"] - 1, column=options["column"], sticky=options["sticky"])
            
            # If the widget is a label, update text
            if isinstance(widget, tk.Label):
                widget.config(text=f"{type} Condition {options['row'] - 1}")
    
    # If there are no more conditions, hide the frame
    if len(conditions[type]) == 0:
        frame.grid_forget()
    
    # Resize the window
    root.geometry(str(WIDTH) + "x" + str(HEIGHT+20*len(conditions["Negative"])+20*len(conditions["Positive"])))

def calculatePowerLevel():
    # Reset the power level to 0
    powerLevel = 0
    print("--------------------")
    # Add up the additive effects
    for effect in effectData:
        if effectData[effect]["type"] == "additive":
            powerLevel += effectData[effect]["value"][effectData[effect]["currentValue"].get()]
            print(f"{effect}: +{effectData[effect]['value'][effectData[effect]['currentValue'].get()]}, Power Level: {powerLevel}")
    
    # Add the negative conditions
    for condition in conditions["Negative"]:
        powerLevel += effectData["Negative_Condition"]["value"][condition]
        print(f"{condition}: +{effectData['Negative_Condition']['value'][condition]}, Power Level: {powerLevel}")
    
    # Add the positive conditions
    for condition in conditions["Positive"]:
        powerLevel += effectData["Positive_Condition"]["value"][condition]
        print(f"{condition}: +{effectData['Positive_Condition']['value'][condition]}, Power Level: {powerLevel}")
    
    # Multiply the multiplier effects
    for effect in effectData:
        if effectData[effect]["type"] == "multiplier":
            powerLevel *= effectData[effect]["value"][effectData[effect]["currentValue"].get()]
            print(f"{effect}: *{effectData[effect]['value'][effectData[effect]['currentValue'].get()]}, Power Level: {powerLevel}")

    
    powerLevel += effectData["AP_Cost"]["value"][effectData["AP_Cost"]["currentValue"].get()]
    print("Power Level: ", powerLevel)

    # Update the power level label
    powerLevelUtility["Power_Level"]["tkWigit"].config(text=("Power Level:      " + str(powerLevel)))

# Create text input fields
# entry1 = tk.Entry(frame_GenerateCards)
# # Set the size of the text input fields
# entry1.config(width=20)

# Create a button
# generateCard_button = tk.Button(frame_GenerateCards, text="Retrieve Input", command=retrieve_input)
# generateCard_button.config(width=20, height=2)

# Bind the button to the left mouse click
# generateCard_button.bind("<Button-1>", lambda event: retrieve_input) # retrieve_input is a function name, not a function call

# Pack widgets
# entry1.pack()
# generateCard_button.pack()

def resetValues():
    initPowerLevelDropdowns()
    # Call removeCondition for each condition
    for frame in conditionFrames:
        conditionType = "Negative" if frame == frame_NegativeConditions else "Positive"
        for i in range(len(conditions[conditionType])):
            removeCondition(conditionType, frame, conditions[conditionType][0])
    
    powerLevelUtility["Power_Level"]["tkWigit"].config(text=powerLevelUtility["Power_Level"]["label"])

button_generatePowerLevel = tk.Button(frame_GeneratePowerLevel, text="Calculate", command=calculatePowerLevel)
button_generatePowerLevel.grid(row=15, column=0, columnspan=1, sticky="ew")
button_generatePowerLevel.config(width=20, height=1)
button_resetPowerLevel = tk.Button(frame_GeneratePowerLevel, text="Reset", command=resetValues)
button_resetPowerLevel.grid(row=15, column=1, columnspan=1, sticky="ew")
button_resetPowerLevel.config(width=20, height=1)

# Create labels and dropdowns
initPowerLevelLabels()
initPowerLevelDropdowns()

# Start the main event loop
root.mainloop()
    