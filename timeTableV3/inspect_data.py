import pandas as pd
import os

files = ['instructors.xlsx', 'courses.xlsx', 'rooms.xlsx', 'timeslots.xlsx']
data_dir = 'data'

for f in files:
    fp = os.path.join(data_dir, f)
    print('===', f, '===')
    try:
        df = pd.read_excel(fp)
        print('cols:', df.columns.tolist())
        print(df.head(10).to_string())
    except Exception as e:
        print('Error reading', fp, ':', e)
    print('\n')
