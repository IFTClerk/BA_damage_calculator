#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import json
from urllib.request import urlopen
import re

damage_type_map = {
    "Explosion": "red",
    "Pierce": "yellow",
    "Mystic": "blue",
    "Siege": "purple",
    "Normal": "white"
}
armour_type_map = {
    "LightArmor": "red",
    "HeavyArmor": "yellow",
    "Unarmed": "blue"
}
adaptation_multiplier_map = {
    'S': 1.2,
    'A': 1.1,
    'B': 1.0,
    'C': 0.9,
    'D': 0.8
}
adaptation_multiplier_UE_map = {
    'StreetBattleAdaptation_Base': [0.1, 0.0, 0.0],
    'OutdoorBattleAdaptation_Base': [0.0, 0.1, 0.0],
    'IndoorBattleAdaptation_Base': [0.0, 0.0, 0.1]
}
bond_stat_type_map = {
    'AttackPower_Base': 'attack',
    'DefensePower_Base': 'defence',
    'HealPower_Base': 'heal',
    'MaxHP_Base': 'hp'
}
jp_stat_name_map = {
    '会心ダメージ': "crit_dmg",
    '被回復値': "recovery",
    'HP': "hp",
    '攻撃力': "attack",
    '防御力': "defence",
    '命中値': "accuracy",
    '攻撃速度': "attack_speed", 
    '会心値': "crit",
    '装弾数': "ammo_count",
    'CC強化力': "cc_strength", 
    '防御貫通値': "defence_penetration", 
    '回避値': "evasion",
    '遮蔽成功値': "block_rate",
    '安定値': "stability",
    '治癒力': "heal"
}

def nowarn(func):
    pd.options.mode.chained_assignment = None
    func()
    pd.options.mode.chained_assignment = 'warn'

def get_game_data(url):
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df

def get_id_name_map():
    
    print("Preparing name map ...")    
    # grab game data from public git
    url = 'https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterAcademyTagsExcelTable.json'
    response = urlopen(url)
    data = json.loads(response.read())['DataList']
    
    # initialise both return values
    name_map = {}
    display_name_map = {}
    for node in data:
        # get the name from tags
        name = [tag for tag in node["FavorItemUniqueTags"] if tag.startswith("F_")][0]
        name = name[2:]

        # De-japonise the name
        name = name.replace("Zunko", "Junko")
        name = name.replace("Hihumi", "Hifumi")
        
        # add name to dict
        name_map[node["Id"]] = name.lower()
        
        # format display names
        name_components = name.split("_")
        display_name = ""
        # first word is full name
        if len(name_components)==1:
            display_name = name_components[0]
        # name has a description term
        elif len(name_components)>1 and name_components[1]!="default":
            # fix name suffix capitalisation
            name_suffix_cap = map(lambda s: s.capitalize(), name_components[1:])
            # format name into 'name (suffix)'
            display_name = f"{name_components[0]} ({' '.join(name_components[1:])})"
        else:
            display_name = name_components[0]
        
        display_name_map[node["Id"]] = display_name
        
    print(f"Found {len(name_map.keys())} character names")
    return name_map, display_name_map

def get_char_stats():
    print("Fetching character stats data... ", end="")
    
    df = get_game_data('https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterStatExcelTable.json')
    
    print("Done")
    return df

def get_char_details():
    print("Fetching character details data... ", end="")
    
    df = get_game_data("https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterExcelTable.json")
    
    print("Done")
    return df

def get_ue_stats():
    print("Fetching unique equipment stats data... ", end="")
    
    df = get_game_data("https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterWeaponExcelTable.json")
    
    print("Done")
    return df

def get_bond_stats():
    print("Fetching character bond stats data... ", end="")
    
    df = get_game_data("https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/FavorLevelRewardExcelTable.json")
    
    print("Done")
    return df

def split_bond_stat(df):
    # Check if all required columns are present
    needed_cols = ('FavorLevel', 'StatType', 'StatValue')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    
    # get the two bond stats by looking at the final row
    df_stat1, df_stat2 = df.StatType.iloc[-1]
    
    # map to easier names
    df_stat1 = bond_stat_type_map[df_stat1]
    df_stat2 = bond_stat_type_map[df_stat2]
    
    # cumsum of stats 
    # str[0/1] access the first/second element of the list
    # non-existent entries are stored as NaN
    # fillna converts NaNs to 0
    # cast to int to make everything consistent
    # and finally convert to list
    df_stat1_value = df.StatValue.str[0]\
            .fillna(0)\
            .astype(int)\
            .cumsum()\
            .tolist()
    df_stat2_value = df.StatValue.str[1]\
            .fillna(0)\
            .astype(int)\
            .cumsum()\
            .tolist()
    
    # insert a 0 at the beginning for bond level 1
    df_stat1_value.insert(0, 0)
    df_stat2_value.insert(0, 0)

    return pd.Series({'BondStat1': df_stat1, 'BondStat1Value': df_stat1_value, 'BondStat2': df_stat2, 'BondStat2Value': df_stat2_value})

def get_char_skill():
    print("Fetching character skill data... ", end="")
    
    df = get_game_data("https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterSkillListExcelTable.json")
    
    print("Done")
    return df

def get_skill_table():
    print("Fetching skill table... ", end="")
    
    df = get_game_data('https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/SkillExcelTable.json')
    
    print("Done")
    return df

def get_skill_localisation_table():
    print("Fetching skill localisation table... ", end="")
    
    df = get_game_data('https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/LocalizeSkillExcelTable.json')
    
    print("Done")
    return df

# compile regex for splitting UE passive description
re_split_ue_desc = re.compile(r'^(.+?)を\[c]\[007eff]([0-9]+)%?\[-]\[\/c]増加\/\n.*')

def get_ue_passive_stats(df):
    # Check if all required columns are present
    needed_cols = ('CharacterId', 'DescriptionJp')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    # sort by level, ascending
    df.sort_values(by='Level', inplace=True)
    # regex magic to split skill description
    df2 = df.DescriptionJp.str.split(re_split_ue_desc, expand=True)
    
    # get stat name from first element of first column
    # then use dictionary to map to English
    stat_name = jp_stat_name_map[df2[1].iloc[0]]
    # convert stat values to a list
    stat_values = df2[2].astype(int).tolist()
    
    return pd.Series({ "CharacterId": df.CharacterId.iloc[0], "UEPassiveStatName": stat_name, "UEPassiveStatValue": stat_values })

# function that aggregates the BattleAdaptation columns to a single column of arrays
def aggregate_terrain_affinity(row):
    affinity = []
    try:
        affinity.append(adaptation_multiplier_map[row.StreetBattleAdaptation])
        affinity.append(adaptation_multiplier_map[row.OutdoorBattleAdaptation])
        affinity.append(adaptation_multiplier_map[row.IndoorBattleAdaptation])
    except AttributeError:
        print(f'Failed to find BattleAdaptation values for {row.CharacterId}')
    
    return affinity


## Main ##
if __name__=="__main__":
    name_map, display_name_map = get_id_name_map()
    
    # fetch character stats
    chars_df = get_char_stats()
    
    # filter the table to keep only the students via valid id's
    chars_df = chars_df[chars_df['CharacterId'].isin(list(name_map.keys()))]
    
    # get additional character details from other table
    details_df = get_char_details()
    details_df = details_df[details_df['Id'].isin(list(name_map.keys()))]
    
    # rename id to make joining easier
    details_df = details_df.rename(columns={"Id": "CharacterId"})
    
    # get most of the UE stats from the UE table
    ue_df = get_ue_stats()
    
    # keep only students
    ue_df = ue_df[ue_df['Id'].isin(list(name_map.keys()))]
    
    # rename Id column to make joining easier
    ue_df = ue_df.rename(columns={"Id": "CharacterId"})
    
    # get character bond stats from game data
    bond_df = get_bond_stats()
    
    # process the bond stat and then reset index to get CharacterId back
    bond_stats_df = bond_df.groupby('CharacterId').apply(split_bond_stat).reset_index()
    
    # fetch the character skills data
    char_skill_df = get_char_skill()
    
    # select only students and only UE tier 2 entries to get UE passive info
    char_ue_skill_df = char_skill_df[(char_skill_df['CharacterId'].isin(list(name_map.keys()))) & (char_skill_df['MinimumGradeCharacterWeapon']==2)]
    
    # remove duplicated entries
    char_ue_skill_df = char_ue_skill_df[~char_ue_skill_df.CharacterId.duplicated()]
    
    # de-list the passive skill group id
    char_ue_skill_df.PassiveSkillGroupId = char_ue_skill_df.PassiveSkillGroupId.map(lambda x: x[0])
    
    # fetch the skill table
    skill_df = get_skill_table()
    
    # fetch the skill localisation table
    localisation_df = get_skill_localisation_table()
    
    # join both tables with character skill table with the appropriate keys
    char_ue_skill_df = char_ue_skill_df.merge(skill_df, how='left', left_on='PassiveSkillGroupId', right_on='GroupId')
    char_ue_skill_df = char_ue_skill_df.merge(localisation_df, how='left', left_on='LocalizeSkillId', right_on='Key')
    
    # group by passive skill group id and get UE passive bonus
    ue_passive_df = char_ue_skill_df.groupby('PassiveSkillGroupId', sort=False).apply(get_ue_passive_stats).reset_index()
    
    # merge all tables on CharacterId
    chars_df = chars_df.merge(details_df, how='left', on='CharacterId')
    # suffixes required because of conflicting column names
    chars_df = chars_df.merge(ue_df, how='left', on='CharacterId', suffixes=[None, '_UE'])
    chars_df = chars_df.merge(bond_stats_df, how='left', on='CharacterId')
    chars_df = chars_df.merge(ue_passive_df, how='left', on='CharacterId')
    
    print('Doing additional processing on DataFrame')
    
    # dictionary to rename all the columns to something sensible
    # and keep only useful columns
    # 'StatType' is the terrain affinty that is being modified
    # 'AfterSkillGroupId' is the new passive from UE 2*
    column_dict = {
        'CharacterId': 'CharacterId',
        #'StabilityRate': 'StabilityRate', # don't know what this is
        'MaxHP1': 'MaxHP1',
        'MaxHP100': 'MaxHP100',
        'AttackPower1': 'AttackPower1',
        'AttackPower100': 'AttackPower100',
        'DefensePower1': 'DefensePower1',
        'DefensePower100': 'DefensePower100',
        'HealPower1': 'HealPower1',
        'HealPower100': 'HealPower100',
        'DodgePoint': 'Evasion',
        'AccuracyPoint': 'Accuracy',
        'CriticalPoint': 'Crit',
        'CriticalResistPoint': 'CritRes',
        'CriticalDamageRate': 'CritDmg',
        'CriticalDamageResistRate': 'CritDmgRes',
        # 'BlockRate': 'BlockRate', # probably don't need this
        'HealEffectivenessRate': 'Recovery',
        'OppressionPower': 'CCStrength',
        'OppressionResist': 'CCRes',
        'Range': 'Range',
        'StabilityPoint': 'Stability',
        'DefensePenetration1': 'DefensePenetration1',     # probably useless but keeping in anyways
        'DefensePenetration100': 'DefencePenetration100',
        'BulletType': 'BulletType',
        'ArmorType': 'ArmorType',
        # 'AmmoCount': 'AmmoCount',
        # 'AmmoCost': 'AmmoCost',
        # 'IgnoreDelayCount': 'IgnoreDelayCount',
        # 'NormalAttackSpeed': 'NormalAttackSpeed',
        # 'InitialRangeRate': 'InitialRangeRate',
        # 'MoveSpeed': 'MoveSpeed',
        # 'SightPoint': 'SightPoint',
        # 'ActiveGauge': 'ActiveGauge',                # irrelevant columns for damage calc
        # 'GroggyGauge': 'GroggyGauge',
        # 'GroggyTime': 'GroggyTime',
        # 'StrategyMobility': 'StrategyMobility',
        # 'ActionCount': 'ActionCount',
        # 'StrategySightRange': 'StrategySightRange',
        # 'DamageRatio': 'DamageRatio',
        # 'DamagedRatio': 'DamagedRatio',
        'StreetBattleAdaptation': 'StreetBattleAdaptation',
        'OutdoorBattleAdaptation': 'OutdoorBattleAdaptation',
        'IndoorBattleAdaptation': 'IndoorBattleAdaptation',
        # 'RegenCost': 'RegenCost',
        'EquipmentSlot': 'EquipmentSlot',
        'MaxHP': 'MaxHP1_UE',
        'MaxHP100_UE': 'MaxHP100_UE',
        'AttackPower': 'AttackPower1_UE',
        'AttackPower100_UE': 'AttackPower100_UE',
        'HealPower': 'HealPower1_UE',
        'HealPower100_UE': 'HealPower100_UE',
        'AfterSkillGroupId': 'PassiveSkillId_UE',
        'StatType': 'TerrainMultiplier_UE',
        'BondStat1': 'BondStat1',
        'BondStat1Value': 'BondStat1Value',
        'BondStat2': 'BondStat2',
        'BondStat2Value': 'BondStat2Value',
        'UEPassiveStatName': 'UEPassiveStatName',
        'UEPassiveStatValue': 'UEPassiveStatValue'
    }
    
    # store renamed/reordered DF in new dataframe
    chars_df2 = chars_df.rename(columns=column_dict)
    chars_df2 = chars_df2[list(column_dict.values())]
    # set defaults for empty bond values
    chars_df2.BondStat1 = chars_df2.BondStat1.fillna('hp')
    chars_df2.BondStat2 = chars_df2.BondStat2.fillna('attack')
    chars_df2 = chars_df2.fillna(0)
    
    # Modifying columns
    # add columns with character names
    chars_df2['CharacterName'] = chars_df2.CharacterId.map(name_map)
    chars_df2['CharacterDisplayName'] = chars_df2.CharacterId.map(display_name_map)
    
    # un-capitalise the equipment list with maps and lambdas
    chars_df2.EquipmentSlot = chars_df2.EquipmentSlot.map(lambda x: list(map(lambda y: y.lower(), x)))
    
    # map the bullet & armour type names to simpler colours
    chars_df2.BulletType = chars_df2.BulletType.map(damage_type_map)
    chars_df2.ArmorType = chars_df2.ArmorType.map(armour_type_map)
    
    # pick out the only useful indices
    chars_df2.TerrainMultiplier_UE = chars_df2.TerrainMultiplier_UE.map(lambda x: x[2])
    chars_df2.PassiveSkillId_UE = chars_df2.PassiveSkillId_UE.map(lambda x: x[1])
    
    # convert terrain affinity to array for each row in the DF
    chars_df2['TerrainMultiplier'] = chars_df2.apply(aggregate_terrain_affinity, axis=1)
    
    # map the UE terrain affinity bonus to arrays
    chars_df2.TerrainMultiplier_UE = chars_df2.TerrainMultiplier_UE.map(adaptation_multiplier_UE_map)


    # Exporting to JSONs
    print("Exporting compiled data to JSON")
    from pathlib import Path
    import json
    
    # user input for directory
    data_path = Path('.')
    while True:
        try:
            data_path_name = input('Specify output directory (default=characters): ')
            if data_path_name=='':
                data_path_name = 'characters'
            # make directory to store character data
            data_path = Path(data_path_name)
            data_path.mkdir(exist_ok=True)
            break
        except OSError as err:
            print(f'Failed to create directory: {err}')
            continue
    
    # iterate through rows in the DF
    print("Exporting...")
    for index, row in chars_df2.iterrows():
        # debug line to process only one character for testing
        # if index!=0: continue
        with (data_path / (row.CharacterName + '.json')).open('w', encoding='utf-8') as f:
            # initialise character data in the right format
            character_data = {
                "display_name": row.CharacterDisplayName,
                "is_playable": True,
                "damage_type": row.BulletType,
                "armour_type": row.ArmorType,
                "status": {
                    "hp": [row.MaxHP1, row.MaxHP100],
                    "attack": [row.AttackPower1, row.AttackPower100],
                    "defence": [row.DefensePower1, row.DefensePower100],
                    "heal": [row.HealPower1, row.HealPower100],
                    "evasion": row.Evasion,
                    "accuracy": row.Accuracy,
                    "crit": row.Crit,
                    "crit_res": row.CritRes,
                    "crit_dmg": row.CritDmg,
                    "crit_dmg_res": row.CritDmgRes,
                    "recovery": row.Recovery,
                    "cc_strength": row.CCStrength,
                    "cc_res": row.CCRes,
                    "range": row.Range,
                    "stability": row.Stability
                },
                "terrain_mod": row.TerrainMultiplier,
                "equipment": row.EquipmentSlot,
                "unique_equipment": {
                    "innate_status_bonus": [],
                    "ps_status_bonus": {
                        "status": row.UEPassiveStatName,
                        "value": row.UEPassiveStatValue
                    },
                    "terrain_mod_bonus": row.TerrainMultiplier_UE
                },
                "bond": [
                    {
                        "status": row.BondStat1,
                        "value": row.BondStat1Value
                    },
                    {
                        "status": row.BondStat2,
                        "value": row.BondStat2Value
                    }
                ]
            }
            
            ue_stat_name = ['hp', 'attack', 'heal']
            # separately process UE innate stat bonus
            for index, (lo, hi) in enumerate([(row.MaxHP1_UE, row.MaxHP100_UE),\
                    (row.AttackPower1_UE, row.AttackPower100_UE),\
                    (row.HealPower1_UE, row.HealPower100_UE)]):
                if hi==0:
                    # don't add to bonus list
                    continue
                else:
                    this_bonus = {
                        "status": ue_stat_name[index],
                        "value": [lo, hi]
                    }
                    # append to bonus list
                    character_data['unique_equipment']['innate_status_bonus'].append(this_bonus)
            
            json.dump(character_data, f)

    print("Script finished, exiting")

