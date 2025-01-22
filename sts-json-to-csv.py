import sys
import os
import json
import csv
import gzip

# Place in a folder with or above the .json.gz files to parse 
# Run with "python sts-json-to-csv.py <outputFileNameWithoutExtension>"

# The data headers, ordered as they will appear in the csv
# Comment in/out things you want
# json_key: [Formatted Header, sub properties]
propertyInfo = {
    'play_id': ['Play Id', ''],
    'build_version': ['Build Version', ''],
    'timestamp': ['Timestamp', ''],
    'local_time': ['Local Time', ''],
    'playtime': ['Playtime', ''],

    'is_beta': ['Is Beta', ''],
    'is_prod': ['Is Prod', ''],
    'is_trial': ['Is Trial', ''],
    'is_daily': ['Is Daily', ''],
    'is_endless': ['Is Endless', ''],

    'seed_played': ['Seed Played', ''],
    # 'seed_source_timestamp': ['Seed Source Timestamp', ''],
    'chose_seed': ['Chose Seed', ''],
    # 'special_seed': ['Special Seed', ''],

    # This is redundant with ascension_level > 0 but maybe easier to work with
    'is_ascension_mode': ['Is Ascension Mode', ''],
    'ascension_level': ['Ascension Level', ''],

    'victory': ['Victory', ''],
    'score': ['Score', ''],
    'floor_reached': ['Floor Reached', ''],
    'killed_by': ['Killed By', ''],
    'character_chosen': ['Character Chosen', ''],
    'master_deck': ['Master Deck', ''],
    'relics': ['Relics', ''],
    # This is super niche, almost always 0, probably requires endless mode or cheating?
    # 'circlet_count': ['Circlet Count', ''],
    'neow_bonus': ['Neow Bonus', ''],
    'neow_cost': ['Neow Cost', ''],
    'gold': ['Gold', ''],
    'gold_per_floor': ['Gold Per Floor', ''],
    # Not sure what this is for, it's seemingly always 0
    # 'win_rate': ['Win Rate', ''],
    'player_experience': ['Player Experience', ''],
    
    'path_per_floor': ['Path Per Floor', ''],
    'path_taken': ['Path Taken', ''],
    
    # These are technically redundant with campfire_choices, but much easier to work with
    'campfire_rested': ['Campfire Rested', ''],
    'campfire_upgraded': ['Campfire Upgraded', ''],

    'campfire_choices': ['Campfire Choices', 'floor,key,data'],
    'max_hp_per_floor': ['Max Hp Per Floor', ''],
    'current_hp_per_floor': ['Current Hp Per Floor', ''],

    'damage_taken': ['Damage Taken', 'damage,enemies,floor,turns'],

    'card_choices': ['Card Choices', 'not_picked,picked,floor'],

    'relics_obtained': ['Relics Obtained', 'floor,key'],
    'boss_relics': ['Boss Relics', 'not_picked,picked'],

    # Interesting but large, annoying to parse, and highly variant
    'event_choices': ['Event Choices', 'floor,event_name,player_choice,damage_healed,damage_taken,max_hp_gain,max_hp_loss,gold_gain,gold_loss,cards_obtained,cards_removed,cards_upgraded,cards_transformed,relics_obtained,relics_lost,potions_obtained'],

    'items_purchased': ['Items Purchased', ''],
    'item_purchase_floors': ['Item Purchase Floors', ''],
    'items_purged': ['Items Purged', ''],
    'items_purged_floors': ['Items Purged Floors', ''],
    'purchased_purges': ['Purchased Purges', ''],

    'potions_obtained': ['Potions Obtained', 'floor,key'],
    'potions_floor_spawned': ['Potions Floor Spawned', ''],
    'potions_floor_usage': ['Potions Floor Usage', ''],
}

# Properties from the list above with values by which to filter runs
# The properties themselves will also not be included
excludes = {
    'is_beta': True,
    'is_prod': True,
    'is_trial': True,
    'is_daily': True,
    'is_endless': True,
    'chose_seed': True
}

# Use the first arg to name the csv
csvFileName = sys.argv[1]

# Open a file for writing
csvFile = open(csvFileName + '.csv', 'w', newline='')

# Create the csv writer object
csvWriter = csv.writer(csvFile)

# Write the headers
keys = propertyInfo.keys()
headers = []
subProperties = []
dataTypes = []
for key in keys:
    if key in excludes.keys(): continue
    headers.append(propertyInfo[key][0])
    skip = True
    for subProperty in propertyInfo[key][1].split(','):
        if not skip: headers.append('')
        subProperties.append(subProperty)
        skip = False
        
csvWriter.writerow(headers)
csvWriter.writerow(subProperties)

# Get the current directory
folder = os.getcwd()

# Recursively search the current directory for .json.gz files
extension = '.json.gz'
matches = []
for root, dirnames, filenames in os.walk(folder):
    for filename in filenames:
        if filename.endswith(extension):
            matches.append(os.path.join(root, filename))

# Function to process data of a run and write to the csv
def processRun(run):
    runData = []
    # Print out any keys we might be missing, or that we intentionally exclude
    # for key in run.keys():
    #     if key not in keys:
    #         print(key + ': ' + str(run[key]))
    for key in keys:
        # Filter out the entire run if any of the exclude properties match
        if key in excludes.keys():
            # Exclude the run
            if run[key] is excludes[key]: return
            # Keep the run, skip the data point
            else: continue

        subProps = propertyInfo[key][1].split(',')

        # Empty property, some properties aren't always in the json
        if key not in run.keys():
            runData.append('')

        # Basic property, a single value, or single array
        elif subProps == ['']:
            data = run[key]
            # If an array, turn it into a delimited string
            if isinstance(data, list):
                data = ', '.join(str(i) for i in data)
            runData.append(data)

        # Complex property with sub properties
        else:
            data = run[key]
            # If not an array, put it into one to process
            if not isinstance(data, list):
                data = [run[key]]

            for subProp in subProps:
                subData = []
                for element in data:
                    if subProp not in element.keys():
                        subData.append('')
                    else:
                        subValue = element[subProp]
                        # If an array, turn it into a delimited string
                        if isinstance(subValue, list):
                            subValue = ', '.join(str(i) for i in subValue)
                        subData.append(subValue)
                subData = '; '.join(str(i) for i in subData)
                runData.append(subData)

    csvWriter.writerow(runData)

# Open the files, get the json data, and process each run
for file in matches:
    with gzip.open(file, 'rb') as jsonFile:
        data = json.load(jsonFile)
        for element in data:
            run = element['event']
            processRun(run)

csvFile.close()