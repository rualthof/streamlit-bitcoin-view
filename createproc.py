import os

with open('Procfile', "w") as file1:
    toFile = 'web: sh setup.sh && streamlit run bitapp.py'

    file1.write(toFile)