# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:29:42 2018

@author: Adeola
"""

''' 
This project measures the  Minority Population Change in Charleston, South Carolina.
It examines the population in Charleston in  2000, 2010 and 2016. The population is 
categorized into whites and minorities.
'''

import geopandas as gpd
import pandas as pd
from pysal.esda import mapclassify
import matplotlib.pyplot as plt

'''To read in the census data'''
charleston_2000=pd.read_csv(r'../demographic_data/DEC_00_SF3_P006_with_ann.csv')
charleston_2010=pd.read_csv(r'../demographic_data/DEC_10_SF1_P3_with_ann.csv')
charleston_2016=pd.read_csv(r'../demographic_data/ACS_16_5YR_B02001_with_ann.csv')

''' To select relevant columns, removing the descriptive first column and renaming them'''
charleston_2000_clean = charleston_2000[['GEO.id2','VD01','VD02']]
charleston_2000_cleaned = charleston_2000_clean.drop(charleston_2000.index[0])
charleston_2000_cleaned.rename(columns = {'GEO.id2':'GeoId','VD01':'Pop_00','VD02': 'White_00'}, inplace=True)

charleston_2010_clean = charleston_2010[['GEO.id2','D001','D002']]
charleston_2010_cleaned = charleston_2010_clean.drop(charleston_2010.index[0])
charleston_2010_cleaned.rename(columns = {'GEO.id2':'GeoId','D001':'Pop_10','D002': 'White_10'}, inplace=True)

charleston_2016_clean = charleston_2016[['GEO.id2','HD01_VD01','HD01_VD02']]
charleston_2016_cleaned = charleston_2016_clean.drop(charleston_2016.index[0])
charleston_2016_cleaned.rename(columns = {'GEO.id2':'GeoId','HD01_VD01':'Pop_16','HD01_VD02': 'White_16'}, inplace=True)

'''To convert the columns that would be used to perform arithmetic functions to appropraite datatype'''
charleston_2000_cleaned[['Pop_00','White_00']] = charleston_2000_cleaned[['Pop_00','White_00']].apply(pd.to_numeric)
charleston_2010_cleaned[['Pop_10','White_10']] = charleston_2010_cleaned[['Pop_10','White_10']].apply(pd.to_numeric)
charleston_2016_cleaned[['Pop_16','White_16']] = charleston_2016_cleaned[['Pop_16','White_16']].apply(pd.to_numeric)

''' To create the two new columns needed for the analysis'''
charleston_2000_cleaned['Minority_00'] = charleston_2000_cleaned['Pop_00'] - charleston_2000_cleaned['White_00']
charleston_2000_cleaned['Min_Perc_00'] = charleston_2000_cleaned['Minority_00']/charleston_2000_cleaned['Pop_00'] * 100

charleston_2010_cleaned['Minority_10'] = charleston_2010_cleaned['Pop_10'] - charleston_2010_cleaned['White_10'] 
charleston_2010_cleaned['Min_Perc_10'] = charleston_2010_cleaned['Minority_10']/charleston_2010_cleaned['Pop_10'] * 100

charleston_2016_cleaned['Minority_16'] = charleston_2016_cleaned['Pop_16'] - charleston_2016_cleaned['White_16']  
charleston_2016_cleaned['Min_Perc_16'] = charleston_2016_cleaned['Minority_16']/charleston_2016_cleaned['Pop_16'] * 100

'''  To create copies so as noy to disturb original data'''
charleston_00 = charleston_2000_cleaned.copy()
charleston_10 = charleston_2010_cleaned.copy()
charleston_16 = charleston_2016_cleaned.copy()

''' To merge all the data from the three years'''
charleston = pd.merge(pd.merge(charleston_00,charleston_10,on='GeoId'),charleston_16,on='GeoId')

''' To create the column for percent change in minorities over the periods'''
charleston['MP00_10']= charleston['Min_Perc_10'] - charleston['Min_Perc_00']
charleston['MP10_16']= charleston['Min_Perc_16'] - charleston['Min_Perc_10']
charleston['MP00_16']= charleston['Min_Perc_16'] - charleston['Min_Perc_00']


''' To read in the South Carolina census tract data'''
south_carolina=gpd.read_file(r'../south_carolina_census_tract/cb_2017_45_tract_500k.shp')


'''To select the census tracts identified in the charleston population data'''
charleston_tracts=charleston['GeoId'].unique()


''' To extract the tracts identified in the population data from the south carolina boundary shapefile'''
charleston_boundary=south_carolina.loc[south_carolina['GEOID'].isin(charleston_tracts)]

''' To merge the attribute file of the charleston boundary to the population data'''
charleston_w_pop=charleston_boundary.merge(charleston, left_on='GEOID', right_on='GeoId', how='inner')



''' To set a background colur for the maps and title format for the maps'''
plt.style.use('dark_background')
f_fict = {'family': 'serif',
        'weight': 'normal',
        'size': 24}


''' To create the classes for percent minority change from 2000 to 2010'''
binning_pm_00_10 = mapclassify.User_Defined(charleston['MP00_10'], bins=[-1, 1, 25])

binedges_pm_00_10 = [charleston['MP00_10'].min()] + binning_pm_00_10.bins.tolist()
classes_pm_00_10 = ['{0:,.0f} - {1:,.0f}'.format(binedges_pm_00_10[i], binedges_pm_00_10[i+1])
                      for i in range(len(binedges_pm_00_10)-1)]
''' To create the map for percent minority change from 2000 to 2010'''
mp_00_10=charleston_w_pop.to_crs(epsg=6570).plot(column='MP00_10', k=3,legend=True, 
                                   scheme='Quantiles',cmap='coolwarm', figsize=(10,10))

mp_00_10.axis('off')
mp_00_10.set_title('Percent Minority change from 2000 to 2010 \nin Charleston, South Carolina', loc='center',fontdict=f_fict)

leg = mp_00_10.get_legend()

leg.set_bbox_to_anchor((0, 0.6, 0.2, 0.2))
leg.set_frame_on(True)

leg.set_title('Change in Percent Minority\n    from 2000 to 2010')

for text, new_text in zip(leg.get_texts(), classes_pm_00_10):
    text.set_text(new_text)
    text.set_color('white')
  
mp_00_10.annotate('Map made in Python by Adeola Awe \nSource: US Census Bureau 2000\n             US Census Bureau 2010\n             2016 ACS ',
            (0.6, 0.03),xycoords='axes fraction')

mp_00_10.annotate(u'\u25B2 \nN', (0.9,0.95), xycoords='axes fraction')
  
plt.tight_layout()
fig=mp_00_10.get_figure()
'''To export the 2000 to 2010 change'''
fig.savefig(r'../result/Percent_minority_change_from 2000_to_2010.png')




''' To create the classes for percent minority change from 2010 to 2016'''
binning_pm_10_16 = mapclassify.User_Defined(charleston['MP10_16'], bins=[-1, 1, 20])

binedges_pm_10_16 = [charleston['MP10_16'].min()] + binning_pm_10_16.bins.tolist()
classes_pm_10_16 = ['{0:,.0f} - {1:,.0f}'.format(binedges_pm_10_16[i], binedges_pm_10_16[i+1])
                      for i in range(len(binedges_pm_10_16)-1)]
''' To create the map for percent minority change from 2010 to 2016'''
mp_10_16=charleston_w_pop.to_crs(epsg=6570).plot(column='MP10_16', k=3,legend=True, 
                                   scheme='Quantiles',cmap='coolwarm', figsize=(10,10))

mp_10_16.axis('off')
mp_10_16.set_title('Percent Minority change from 2010 to 2016 \nin Charleston, South Carolina', loc='center',fontdict=f_fict)

leg = mp_10_16.get_legend()

leg.set_bbox_to_anchor((0, 0.6, 0.2, 0.2))
leg.set_frame_on(True)

leg.set_title('Change in Percent Minority\n    from 2010 to 2016')

for text, new_text in zip(leg.get_texts(), classes_pm_10_16):
    text.set_text(new_text)
    text.set_color('white')
  
mp_10_16.annotate('Map made in Python by Adeola Awe \nSource: US Census Bureau 2000\n             US Census Bureau 2010\n             2016 ACS ',
            (0.6, 0.03),xycoords='axes fraction')

mp_10_16.annotate(u'\u25B2 \nN', (0.9,0.95), xycoords='axes fraction')
  
plt.tight_layout()
fig=mp_10_16.get_figure()
'''To export the 2010 to 2016 change'''
fig.savefig(r'../result/Percent_minority_change_from 2010_to_2016.png')



''' To create the classes for percent minority change from 2000 to 2016'''
binning_pm_00_16 = mapclassify.User_Defined(charleston['MP00_16'], bins=[-1, 1, 26])

binedges_pm_00_16 = [charleston['MP00_16'].min()] + binning_pm_00_16.bins.tolist()
classes_pm_00_16 = ['{0:,.0f} - {1:,.0f}'.format(binedges_pm_00_16[i], binedges_pm_00_16[i+1])
                      for i in range(len(binedges_pm_00_16)-1)]
''' To create the map for percent minority change from 2000 to 2016'''
mp_00_16=charleston_w_pop.to_crs(epsg=6570).plot(column='MP00_16', k=3,legend=True, 
                                   scheme='Quantiles',cmap='coolwarm', figsize=(10,10))

mp_00_16.axis('off')
mp_00_16.set_title('Percent Minority change from 2000 to 2016 \nin Charleston, South Carolina', loc='center',fontdict=f_fict)

leg = mp_00_16.get_legend()

leg.set_bbox_to_anchor((0, 0.6, 0.2, 0.2))
leg.set_frame_on(True)

leg.set_title('Change in Percent Minority\n    from 2000 to 2016')

for text, new_text in zip(leg.get_texts(), classes_pm_00_16):
    text.set_text(new_text)
    text.set_color('white')
  
mp_00_16.annotate('Map made in Python by Adeola Awe \nSource: US Census Bureau 2000\n             US Census Bureau 2010\n             2016 ACS ',
            (0.6, 0.03),xycoords='axes fraction')

mp_00_16.annotate(u'\u25B2 \nN', (0.9,0.95), xycoords='axes fraction')
  
plt.tight_layout()
fig=mp_00_16.get_figure()
'''To export the 2000 to 2016 change'''
fig.savefig(r'../result/Percent_minority_change_from 2000_to_2016.png')


'''To save the table that was created from the study'''
charleston_w_pop.to_csv(r'../result/Charleston_Temporal_Population_Data.csv', index=False)

''' To create the variables for the report'''
Pop_2000 = ("{0:.0f}".format(charleston['Pop_00'].sum()))
Minority_2000 = ("{0:.0f}".format(charleston['Minority_00'].sum()))
Minority_2000_pct = ("{0:.2f}".format(charleston['Min_Perc_00'].mean()))
Pop_2010 = ("{0:.0f}".format(charleston['Pop_10'].sum()))
Minority_2010 = ("{0:.0f}".format(charleston['Minority_10'].sum()))
Minority_2010_pct = ("{0:.2f}".format(charleston['Min_Perc_10'].mean()))
Pct_change_00_10 = ("{0:.2f}".format(charleston['MP00_10'].mean()))
Pop_2016 = ("{0:.0f}".format(charleston['Pop_16'].sum()))
Minority_2016 = ("{0:.0f}".format(charleston['Minority_16'].sum()))
Minority_2016_pct = ("{0:.2f}".format(charleston['Min_Perc_16'].mean()))
Pct_change_10_16 = ("{0:.2f}".format(charleston['MP10_16'].mean()))
Pct_change_00_16 = ("{0:.2f}".format(charleston['MP00_16'].mean()))

''' Filling in the report template'''
charleston_report='According to realtor.com, the city of Charleston, South Carolina has been described as the city experiencing the fastest rate of gentrification in the United States. It has achieved a gentrification potential of 62.5%. Home prices have increased from $152,100 in 2000 to $270,000 in 2015. In 2000, Charleston had a population of ', Pop_2000, ' made up of ', Minority_2000,'.'' With a minority percentage of ', Minority_2000_pct, ' this set the base level of this study. In 2010, Charleston population was ', Pop_2010, ' consisting of ' , Minority_2010, ' minoroties i.e. ' , Minority_2010_pct, ' percent of the population. From 2000 to 2010, there was a percent change of ', Pct_change_00_10, ' experienced in Charleston. The American Community Survey in 2016 estimated Charleston population to be ' , Pop_2016, '; ' , Minority_2016, ' of which were minorities which is ', Minority_2016_pct, ' percent of the population. This was a ' , Pct_change_10_16, ' percent change from 2010. Over the sixteen year period, from 2000 to 2016, there was a minority percentage change of ', Pct_change_00_16, ' experienced in Charleston.'

print (charleston_report)

'''To export the report text file'''
with open(r'../result/charleston_report.txt','w', encoding = 'utf-8') as  d:
    for x in charleston_report:
        d.write(x)