#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import json
from urllib.request import urlopen


# In[2]:


import re


# In[3]:


def nowarn(func):
    pd.options.mode.chained_assignment = None
    func()
    pd.options.mode.chained_assignment = 'warn'


# In[4]:


def get_game_data(url):
    response = urlopen(url)
    df = pd.read_json(response)
    df = pd.json_normalize(df['DataList'])
    
    return df


# In[5]:


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


# In[6]:


def get_char_skill():
    print("Fetching character skill data... ", end="")
    
    df = get_game_data("https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/CharacterSkillListExcelTable.json")
    
    print("Done")
    return df


# In[7]:


def get_skill_table():
    print("Fetching skill table... ", end="")
    
    df = get_game_data('https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/SkillExcelTable.json')
    
    print("Done")
    return df


# In[8]:


def get_skill_localisation_table():
    print("Fetching skill localisation table... ", end="")
    
    df = get_game_data('https://raw.githubusercontent.com/aizawey479/ba-data/jp/Excel/LocalizeSkillExcelTable.json')
    
    print("Done")
    return df


# In[9]:


skill_type_map = {
    "ExSkillGroupId": "ex",
    "PublicSkillGroupId": "normal",
    "PassiveSkillGroupId": "passive",
    "ExtraPassiveSkillGroupId": "sub"
}


# In[10]:


jp_stat_name_map = {
    '会心ダメージ': "crit_dmg",
    '会心ダメージ率': "crit_dmg",
    '被回復値': "recovery",
    '被回復率': "recovery",
    'HP': "hp",
    '攻撃力': "attack",
    '通常攻撃': "attack", # hacky key to make Shun's EX work
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
    '治癒力': "heal",
    'コスト回復力': "cost_recovery",
    '射程': "range",
    '移動速度': "move_speed",
    '会心抵抗値': "crit_res",
    '会心ダメージ抵抗率': "crit_dmg_res",
    'CC強化力': "cc_strength",
    'CC抵抗力': "cc_res",
    'ダメージ量': "damage_taken"
}


# In[11]:


action_map = {
    'ダメージ': "damage",
    '回復': "heal",
    'シールド': "shield",
    '持ち': "summon",
    '増加': "buff",
    '減少': "debuff"
}


# In[12]:


# compile regex based on list of known stat names
stat_names_joined = "|".join(jp_stat_name_map.keys())
actions_joined = "|".join(action_map.keys())
# compile regex for splitting buff skill description
re_skill_desc = re.compile(fr'({stat_names_joined})(?:の|を)\[c]\[007eff](\d+\.?\d*%?)\[-]\[\/c].*?({actions_joined})', flags=re.S)


# In[13]:


def parse_skill_desc(df):
    # Check if all required columns are present
    needed_cols = ('CharacterId', 'SkillCategory', 'DescriptionJp')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    # sort by level, ascending
    df.sort_values(by='Level', inplace=True)
    # regex magic to split skill description
    df2 = df.DescriptionJp.str.split(re_skill_desc, expand=True)
    
    # compute number of effects the skills has based on how many groups regex managed to capture
    df2_n_effects = (len(df2.columns) - 1) // 4
    # initialise list to store effects
    skill_effects = []
    for n in range(df2_n_effects):
        # temp dataframe
        d = df2[range(4*n+1, 4*n+4)]
        effect = {
            "Action": d.iloc[-1,2],
            "Status": d.iloc[-1,0],
            "Values": d.iloc[:,1].fillna('0%').tolist() # need to fill null values with placeholder to avoid errors
        }
        skill_effects.append(effect)
    
    return pd.DataFrame(skill_effects)


# In[14]:


## Main ##

if __name__=='__main__':
    name_map, display_name_map = get_id_name_map()
    
    # fetch the character skills data
    char_skill_df = get_char_skill()
    
    
    # select only students and only base skills without UE
    char_skill_df = char_skill_df[(char_skill_df['CharacterId'].isin(list(name_map.keys()))) & (char_skill_df['MinimumGradeCharacterWeapon']==0)]
    
    # remove duplicated entries
    char_skill_df = char_skill_df[~char_skill_df.CharacterId.duplicated()]
    
    # fetch the skill table
    skill_df = get_skill_table()
    
    # fetch the skill localisation table
    localisation_df = get_skill_localisation_table()
    
    # Rename the columns to more familiar names
    # EX -> EX, Public -> Normal, Passive -> Passive, ExtraPassive -> Sub
    char_skill_df = char_skill_df.rename(columns=skill_type_map)
    
    
    # melt the SkillGroupId column into long format
    char_skill_df2 = pd.melt(char_skill_df, id_vars=['CharacterId'], value_vars=['ex', 'normal', 'passive', 'sub'],                        var_name='SkillCategory', value_name='GroupId')
    
    
    # de-list the skill group ids
    char_skill_df2.GroupId = char_skill_df2.GroupId.map(lambda x: x[0])
    
    char_skill_df2 = char_skill_df2.merge(skill_df, how='left', on='GroupId').merge(localisation_df, how='left', left_on='LocalizeSkillId', right_on='Key')
    
    # get skill information from description
    char_skill_df3 = char_skill_df2.groupby(['CharacterId', 'SkillCategory']).apply(parse_skill_desc)
    
    # map column names to english
    char_skill_df3.Action = char_skill_df3.Action.map(action_map)
    char_skill_df3.Status = char_skill_df3.Status.map(jp_stat_name_map)
    
    # clean up DF a bit
    char_skill_df3 = char_skill_df3.reset_index().rename(columns={'level_2': 'Component'})
    char_skill_df3['CharacterName'] = char_skill_df3.CharacterId.map(name_map)
    char_skill_df3['CharacterDisplayName'] = char_skill_df3.CharacterId.map(display_name_map)
    
    
    # Exporting to JSONs
    print("Exporting compiled data to JSON")
    
    from pathlib import Path
    import json
    
    data_path = Path('.')
    while True:
        try:
            data_path_name = input('Specify output directory (default=skills): ')
            if data_path_name=='':
                data_path_name = 'skills'
            # make directory to store character data
            data_path = Path(data_path_name)
            data_path.mkdir(exist_ok=True)
            break
        except OSError as err:
            print(f'Failed to create directory: {err}')
            continue
    
    
    # iterate through rows in the DF
    # can use the value()s of action_map if want everything
    actions = ['damage', 'heal', 'buff', 'debuff']
    for act in actions:
        skills_act = char_skill_df3[char_skill_df3.Action==act]
        with (data_path / (act + '.json')).open('w', encoding='utf-8') as f:
            skills_data = {}
            # initialise skill data in the right format
            for index, row in skills_act.iterrows():
                # debug line to process only one skill for testing
                # if index!=0: continue
                
                # initialise vars for skill bonus type
                skill_value_type = ''
                # find out if it's a flat bonus or percentage multiplier
                if row.Values[-1].endswith('%'):
                    skill_value_type = 'mult'
                elif ~row.Values[-1].endswith('%'):
                    skill_value_type = 'flat'
                skill_values = list(map(lambda x: float(x.strip('%')), row.Values))
                
                # write to skill data
                skills_data[f'{row.CharacterName}_{row.SkillCategory}_{row.Component}'] = {
                    "display_name": f"{row.CharacterDisplayName} {row.SkillCategory.capitalize()} {row.Component}",
                    "action": row.Action,
                    "category": row.SkillCategory,
                    "status": row.Status,
                    "type": skill_value_type,
                    "value": skill_values
                }
    
            json.dump(skills_data, f)
    
