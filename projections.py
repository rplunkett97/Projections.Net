import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from cs50 import SQL

# pandas used to create dataframe for analysis
# sklearn used to make future projections based on past data points

db = sqlite3.connect("stats.db")

# transform SQL database into more workable format
pddb = pd.read_sql_query("SELECT * FROM nbadata", db)

# consolidate player-seasons by ensuring each name appears only once
players = pddb["Player"].unique()

# iterate over every player in dataframe
# obtain past stats
for player in players:
    
    FGpct = pd.read_sql('SELECT start_year, FGpct FROM nbadata WHERE Player = "{}"'.format(player), db)
 
    FTpct = pd.read_sql('SELECT start_year, FTpct FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    ThreePM = pd.read_sql('SELECT start_year, ThreePM FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    TRB = pd.read_sql('SELECT start_year, TRB FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    AST = pd.read_sql('SELECT start_year, AST FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    STL = pd.read_sql('SELECT start_year, STL FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    BLK = pd.read_sql('SELECT start_year, BLK FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    PTS = pd.read_sql('SELECT start_year, PTS FROM nbadata WHERE Player = "{}"'.format(player), db)
    
    # print commands used to pipe output into .txt file
    # .txt saved as .csv and then imported into new projections SQL database
    
    print(player, end="")
    print(",", end="")
    
    # cubic model used to project next season using past years as data points
    # .reshape(-1,1) used to transform data structure
    # if loops used to ensure projections are non-negative
    
    model = make_pipeline(PolynomialFeatures(3), Ridge())
    model.fit(FGpct['start_year'].values.reshape(-1,1), FGpct['FGpct'].values.reshape(-1,1))
    predictFG = model.predict([2016])
    projectFG = round(predictFG[0][0], 3)
    if projectFG > 1:
        projectFG = 1
    if projectFG < 0:
        projectFG = 0
    print(projectFG, end="")
    print(",", end="")
        
    model.fit(FTpct['start_year'].values.reshape(-1,1), FTpct['FTpct'].values.reshape(-1,1))
    predictFT = model.predict([2016])
    projectFT = round(predictFT[0][0], 3)
    if projectFT > 1:
        projectFT = 1
    if projectFT < 0:
        projectFT = 0
    print(projectFT, end="")
    print(",", end="")
    
    model.fit(ThreePM['start_year'].values.reshape(-1,1), ThreePM['ThreePM'].values.reshape(-1,1))
    predictThreeP = model.predict([2016])
    projectThreeP = round(predictThreeP[0][0], 1)
    if projectThreeP < 0:
        projectThreeP = 0
    print(projectThreeP, end="")
    print(",", end="")
        
    model.fit(TRB['start_year'].values.reshape(-1,1), TRB['TRB'].values.reshape(-1,1))
    predictTRB = model.predict([2016])
    projectTRB = round(predictTRB[0][0], 1)
    if projectTRB < 0:
        projectTRB = 0
    print(projectTRB, end="")
    print(",", end="")
        
    model.fit(AST['start_year'].values.reshape(-1,1), AST['AST'].values.reshape(-1,1))
    predictAST = model.predict([2016])
    projectAST = round(predictAST[0][0], 1)
    if projectAST < 0:
        projectAST = 0
    print(projectAST, end="")
    print(",", end="")
        
    model.fit(STL['start_year'].values.reshape(-1,1), STL['STL'].values.reshape(-1,1))
    predictSTL = model.predict([2016])
    projectSTL = round(predictSTL[0][0], 1)
    if projectSTL < 0:
        projectSTL = 0
    print(projectSTL, end="")
    print(",", end="")
        
    model.fit(BLK['start_year'].values.reshape(-1,1), BLK['BLK'].values.reshape(-1,1))
    predictBLK = model.predict([2016])
    projectBLK = round(predictBLK[0][0], 1)
    if projectBLK < 0:
        projectBLK = 0
    print(projectBLK, end="")
    print(",", end="")
    
    model.fit(PTS['start_year'].values.reshape(-1,1), PTS['PTS'].values.reshape(-1,1))
    predictPTS = model.predict([2016])
    projectPTS = round(predictPTS[0][0], 1)
    if projectPTS < 0:
        projectPTS = 0
    print(projectPTS)