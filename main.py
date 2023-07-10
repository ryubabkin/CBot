import pandas as pd
import json
import openai
import numpy as np
import re
import sys
# %%
key = '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'
openai.api_key = key

text = sys.argv[1]
with open("./CBot_DB_UseCaseGroups.JSON", 'r') as file:
    UCG_db = pd.DataFrame(json.load(file))
    file.close()

with open("./CBot_DB_UseCases.JSON", 'r') as file:
    UC_db = pd.DataFrame(json.load(file))
    file.close()

with open("DB.JSON", 'r') as file:
    Kadence_db = pd.DataFrame(json.load(file))
    file.close()


UC_groups_text = '; '.join((UCG_db['id'].astype(str) + '.' + UCG_db['name']).values)
UC_groups_content = f'For the text "{text}", choose the best description from the below:\n{UC_groups_text}\nThe response should contain only a single digit number of the best choice without any extra symbols.'
UC_groups_result = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": UC_groups_content}])
UC_group_id = int(re.search(r'\d+', UC_groups_result.choices[0].message.content).group())
UC_selected = UC_db[UC_db['group_id'].isin(UCG_db[UCG_db['id'] == UC_group_id]['group_id'].unique())]
print(f'Detected UC group: {UCG_db[UCG_db["id"] == UC_group_id]["name"].iloc[0]}')

UC_text = '; '.join((UC_selected['id'].astype(str) + '.' + UC_selected['description']).values)
UC_content = f'For the text "{text}", choose the best description from the below:\n{UC_text}\nThe response should contain only a single digit number of the best choice without any extra symbols.'
UC_result = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": UC_content}])
UC_id = int(re.search(r'\d+', UC_result.choices[0].message.content).group())
UC = UC_db.loc[UC_db['id'] == UC_id].iloc[0]
print(f'Detected UC: {UC["name"]}')

if UC["name"] != 'Other':
    entities_text = f'For the text "{text}", find the following entities:\n{", ".join(UC["entities"])}\nThe result should be provided in a JSON format containing "entity name" as a key and found entity as a value. If there is no appropriate option - use "------" instead'
    entities_result = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": entities_text}])
    print(entities_result.choices[0].message.content)

