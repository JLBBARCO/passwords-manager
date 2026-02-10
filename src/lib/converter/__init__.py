import pandas as pd
import json

def convertToCSV():
    # Read CSV
    csvArchive = pd.read_csv('passwords.csv', sep=';')

    # Convert to list of dictionaries
    data = []
    for _, row in csvArchive.iterrows():
        entry = {
            "Address": row["Address"],
            "User": row["User"],
            "Password": row["Passwords"]
        }
        data.append(entry)

    # Write to JSON file
    with open('passwords.json', 'w') as jsonFile:
        json.dump(data, jsonFile, indent=4)

    # Print JSON string
    print(json.dumps(data, indent=4))