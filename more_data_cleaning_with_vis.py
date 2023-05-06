######## Further data cleaning and preprocessing for VARIOUS methods :

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
#!pip install --upgrade matplotlib
### Wordclouds by news source:

data = pd.read_csv('data/processed_data/preprocessed_data.csv')


#### WORDCLOUDS FOR CONTENT

rt = data[data['source'] == 'RussiaToday']['content']
rt = ' '.join(rt)
rt

fnc = data[data['source'] == 'FoxNews']['content']
fnc = ' '.join(fnc)
fnc

nyt = data[data['source'] == 'NYTimes']['content'].dropna()
nyt = ' '.join(nyt)
nyt

kp = data[data['source'] == 'KomsomolskayaPravda']['content']
kp = ' '.join(kp)
kp


import matplotlib.font_manager as fm
import os

abs_path = os.path.abspath('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
abs_path

fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')
for font in fonts:
    print(font)

font_path = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
prop = fm.FontProperties(fname=font_path)
prop

print(fm.get_cachedir())

font_path='./opt/X11/share/system_fonts/Supplemental/Gurmukhi.ttf'

wordcloud = WordCloud(stopwords=STOPWORDS).generate(rt)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()


def make_cloud(text,name_for_plot):
    wordcloud = WordCloud(stopwords=STOPWORDS,
                          background_color='white',
                          color_func=(lambda *args, **kwargs: 'black'),
                          font_path=font_path,
                          width = 3000,
                          height = 2000,
                          max_words=500)
    wordcloud.generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(f'data/processed_data/plots/wordcloud_{name_for_plot}')
    plt.show()

make_cloud(rt, 'RT_content')

##### GIVE UP WORD CLOUDS IN PYTHON. TRY R INSTEAD.

with open('data/processed_data/rt_content_all.txt', 'w') as file:
    file.write(rt)

with open('data/processed_data/nyt_content_all.txt', 'w') as file:
    file.write(nyt)

with open('data/processed_data/kp_content_all.txt', 'w') as file:
    file.write(kp)

with open('data/processed_data/fnc_content_all.txt', 'w') as file:
    file.write(fnc)


## Giving up wordclouds altogether


