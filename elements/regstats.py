import streamlit as st
from PIL import Image
import os.path, time
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnchoredOffsetbox)
import pandas as pd
import plotly.graph_objects as go

# Data
regional_stats = pd.read_parquet("assets/models/country-stats.parquet.gzip")
region_tl = pd.read_parquet('assets/models/regions-tl.parquet.gzip')
population = pd.read_csv('assets/ua-population.csv', usecols=['region','2020','2021'])

# File modification year
def modification_date(file):
    t = os.path.getmtime(file)
    year,month,day,hour,minute,second=time.localtime(t)[:-3]
    date = f"{year}"
    return date

# Colors
clr='#00ccd3'
biclr=['#faffff','#00595e']

# Watermark (for Plotly)
plotly_wtrmrk="data:image/png;base64,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%0APZtSCLNX4fV334cwm1nJAk4mYI1SjPHq3+bx6uY6rFdJwKIYqz+6ed60CU2qkqyAPASssVqvUliv%0Awn3A6ntv4DBx0t2bNU46e2pgfASs2rXObovaWADQAQGrdma3AcDZCVhV22kLxhjDer2Ml3+aN9vk%0ALADogoBVo2fbgvfBa7PxhaMA0AEBq2otbcGN4W0A0BUBq3b72oJWrgCgMwJWLbQFAWAwBKxaaAsC%0AwGAIWFXQFgSAIRGwSqYtCACDJGBVQVsQAIZEwKqFtiAADIaAVQttQQAYDOPjAQAyE7AAADITsAAA%0AMhOwAAAyE7AAADITsAAAMhOwAAAyE7AAADITsAAAMhOwAAAyE7AAADIzi7AWKaWQUvPPbeYSAsDZ%0ACVi1uJjGcDENIYTHw5436952CQDGSsCqQkrp02+LENI0rNfLLwErxnh5eROCVSwAOCcBq2T3lwPT%0A3d3t+7//7e3nIBVjDOv1Ml5dv3nz40/v4tX1PKzXyeVCADgPAasKKaW73xefH8YYQ0opTCbTEFIK%0AQa4CgHMSsGqxvTr1ELCsWAFALwSsWuy2Bx+2aRcCwNkJWLXTLgSAsxOwqqZdCAB9ELBqpF0IAL0S%0AsKqmXQgAfRCwaqddCABnJ2DV7th2IXRBqAdGRsAaq33tQuiC1iowMgLWKO1rF0IXtFaB8RGwxmRf%0AuxC6oLUKjJiANUo77ULogtYqMGIC1lhZRaBrWqvAiAlYY6U9yLl4rwEjNOl7BwAAaiNgAQBkJmAB%0AAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBk%0AJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZg%0AAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEA%0AZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGQm%0AYAEAZCZgAQBkJmABAGQmYAEAZCZgAQBkNu17BwCoVIzx0T+fk1LqcnfgnAQsALrxEJhSSsITYyNg%0AAZBfjHFyPZ+H9WoVprPZswErpbT5dHsriFELAQuAfGKMYR3C5Orm5s//ePfukGAVprPZZvH+/a8/%0AvH27+bhYhBijoEXpBCwA8osxTubz+bM/l1IK0xhDWK0OvlcLCiBgAdCN1QGrUCmlEGI86GehIAIW%0AAN04dEUq3v/svtahy4UUSMACYBi0DqmIgAVA//a1DrULKZSABUB/9rUOtQspnIAFQP92W4fahRRO%0AwAJgGLabhNqFFE7AAmAYdleqnmsX7uMyIgMgYAEwbNqFFEjAAmC4zDSkUAIWAMNjpiGFE7AAGC4z%0ADSmUgAXAsJlpSIEELACGzUxDCiRgAdCNfbGo65ijdcgACFgAdGP5r6e3T19195pmGjIQAhYAecUQ%0AwnIZ/vjl5yZkPVypSymE2avw+rvvQ5jN8q5kmWnIwAhYAHQghbD8I4TlXQhxcr9p02zv8hqhmYYM%0AhIAFQDfi5Muf7W1dM9OQARCwAKiLmYYMgIAFwGl240p8Ytsh/7l2IRURsAA4zW5bMMYQlsvQJKbt%0AJBWbbctl8/fdjNNHu3AfrUNOJGAB8DL72oIPVsvH22IMYXX/89v6aBfuo3VIJgIWACd4oi34YN8N%0A7cu7nafooV24j9YhmQhYAJzmqbbgcz9/yLbczDTkjAQsAMbBTEPOSMAC4DDHtgVf8vzHPJ/WIQMm%0AYAFwmIPbgsd6pl24j5mGDJiABUC7Y9uCRz//nnbhPmYaUgABC4ADvKAteKzdduHeXTHTkOETsAA4%0AzLFtwZc8fxc/+1JmGnICAQsAnmKmIScQsAB4rOu2YC5mGjJgAhYAj3XWFszFTEOGT8ACoNF1WzAX%0AMw0pgIAFwJYztAVzMdOQAROwAHis67ZgLmYaMmACFsBYfXW56v5+poc/uytBVmIaZhpyAAELYKym%0AT3wNQZqEcHERwmb29f1Wm/X59u0UZhoyAAIWwBillDaLnXZbjCEs/xXSp9snbnKPMV5e3gzjLvd9%0AzDRkOAQsgDG5v/l6s7i9/fWHt283i/fvd79uIK2WX34+xhjW62W8un7z5sef3sWr63lYr9MgLxea%0AaciACFgAY5RS2nxcLDa/f/zY+gH/8J9NJtMmkQwvV33FTEMGQMACGKtDRr48BKySwoCZhgyAgAVQ%0Au7TzAZ/uQ9MxN18//EzTMDwsHJQUyrpkpuEoCVgAtdtuC6bQnPl3G4SHuJjGcDENIYR4UCgovXWo%0AXcgJBCyAmu22BT/fZL1YHPehnlL69NsihDQN6/Xy+YBVQevQTENOMOA3PlC0+3t34uXVN//lf/zv%0Af8arm2/CejXMe3nSJoTZZXj9l7+GMHvV/crFOXxuCy4WT7YFj/7APjAwldQ6fLAbpLpsF355jcP+%0A99c6LJYVLICaHdoWPOSJ7n5fPPtjNbQOzTQkAwELoHa5RrUc8gFfS+vQTENOJGAB1CJHW/DQ5z/k%0AZ/e1DksKX10y07BqAhZALXK1BXPZ1zosvV24j9YhWwQsgBpkawtm3KEnW4cVtAv3MdOQLQN+gwNF%0A0yI8j+xtwVx2glQN7cJ9+mgdahcOnhUsgBpkawtm3KHt1mEN7cJ9zDTkCQIWQC2GdhP09n7U0i7M%0A8bMvZaZhUQQsgNJ03RbM5al9MNPw5cw0LIqABVCaobUFj2WmYV5DC9aEEAQsgLIMri14LDMN8760%0AmYZDNeA3LFA0LcK8BtsWPJaZhlmZaThYVrAASjK4tuCxzDTMykzDwRKwAEoztLbgscw0zMtMw0ES%0AsACGqpS24LHMNMzLTMNBErAAhqr0tmAuZhrmVXpAL4SABTBExbcFczHTMO8umWl4LgN+YwJF0yJ8%0A4b7U0hbMxUzDrMw0PBsrWABDVHxbMBczDbMy0/BsBCyAoXIzcsNMw7zMNDwLAWusSjo5UaYSPwj7%0AUmtbMBczDfMy0/AsBKyxcmBwLt5rz9MWfBkzDfMS6LMSsEaphPYNxXu4GfnyT/PmveZ8/SRtwRcy%0A0zDvS5tpmNuA32hk97nV9af5ffvmzWEnJjhFAR9sfbQItQVPZKZhVmYaZmcFa5RijFf/No9XN9eD%0Arc1Tl1IuzfRBW/CFzDTMykzD7ASssVqvUlivwn3A6ntvqJ0TcTttwZcx0zAvMw2zErBqt6/e3Px5%0A3BwBuqUtmJeZhnmZaZiVgFW7ffVm4Py0BftlpmFefjFoJWBVbc+ICa0uOD9twZ6ZaZh3l8w0fM6A%0A31C82LNtwRJOKHBGXbYItQUHwkzDrMw0fJYVrKq1tAVLWRKHWmgL9sxMw6zMNHyWgFW7fW1BBwCc%0An5uC+2WmYV5mGrYSsGqhLQjDoS04TGYa5rVvpiEhBAGrHtqCMBzagmUx05AOCFhV0BaEwdAWLIyZ%0AhnRDwCrZ57bg5U1rW3CzsWwLXfvcFry9bW0LPvws/br//yDd3d2+//vf3lY10zDGEFbL8McvPz/e%0Afo52IZ8JWFXQFoTB0BYsjJmGdEPAqoW2IAyHtmBZzDSkAwJWLbQFYTi0BctipiEdELAA4Bhjm2nY%0A9/MWSsACgIONcKbhIVIKIc1CWP4r33MWTsACgOfsax3W0C7MIaUQLqYhfboNabXM//wFErAA4GAj%0Amml4jJRC2Ey7ee5CCVgAcIwxzTQ8WGqeV0vxMwELIDdf01A3Mw05gIAFkJuvaRinWmca8iICFkBO%0AMcbJ9Xwe1qvVk6NyBK5K1TjTkFMIWAA5xBjDOoTJ1c3Nn//x7t3Xw57fv//1h7dvNx8XCyN0KlLz%0ATENOImAB5BRjnMzn88+P74dAh7Ba+RCtWcUzDXkRAQsgt9XW6lRKKYQYH22jTrXONORFBKxamI0F%0Aw7F73MUntlEfMw3ZImDVovTZWABj47xdNQGrCiXPxgIYI+ft2glYJathNhbAmDhvj4aAVYUKZmMB%0AjIrzdu0ErFqUPhsLYGyct6smYNXi2NlYDmKAfplpWDUBq3ZaKnC4GJ6+MuMbrDgnMw2rIGBVTUsF%0ADhNDCCmE5bL5++7CwfRVHzvFKJlpWAv/h1Rt58DTUoF2u0EqpRBmr8Lr774PYTZ72UrW/aiczYcP%0AH/79+2+/3fz24YNZhOx3YGAa2vk8pRQupjF9uv3wH//rv3+b7j6N/n1uBatqWipwlOXd48dpE5pU%0ANdrPCM7OTMNaCFi101KBw8XJYdugS2YaVkHAql2ulgoMQekfJnHrcv02xyHbcs00PKdmH0Z9SXCX%0AgDVWx7ZUYAhKb0s9fPg8fChCDkM4n6cUwsW02RdCCALWSB3bUoEhKLwtFWOcXM/nYb1ahelsth22%0ANp9ubwUuXmYg5/OUUri4mKVPHxdf13DHqcwTFScq/IOKcemzLZU2Icwuw+u//DWE2avT7nXfDVIp%0ApTCdzTaL9+9//eHt283HxWLsrSteYmjn85TS3d2tkGUFa6QObKnAENTSlooxTubz+efH91/fEMJq%0AZRWZl3M+HyoBa6yc0ClFTW2p1dZv9SmlEGJ8tA1eYmjHhlXYEIKANV4OAEpTw2zN3f2MT2yDYzmf%0AD5KABZSjr9maZhQCRxKwgEL0MVvTjELgZSxNA4XocbamGYXAkaxgAYXocbamGYXAkQQsoBx9zdY0%0AoxA4koAFlGPfbE2AgfErGABAZgIWAEBmAhYAQGYCFgBAZgIWAEBmWoRA+WqZUbi7vxqSUCwBCyhf%0A6TMKH4LUw0BroHgCFlC4wmcUxhgn1/N5WK9WYTqbbYetzafbW4ELylTG8jnAXoXPKNwNUimlMJ3N%0ANov373/94e3bzcfFwoxCKI8VLKBwhc8ojDFO5vP5l+dohkCHsFoVcw8Z8BUBCyhf6TMKV1urUyml%0AEGJ8tA0ojoAFlK/0GYW7YTA+sQ0oiu/BAgDITMACAMhMwAIAyEzAAgDITMACAMhMixColxmFQE8E%0ALKBefc0ozMWMQiiWgAVUqo8ZhRmZUQhFG/YJBuDFephRmDYhzC7D67/8NYTZq6Mm5nz9XGYUQsms%0AYAGV6nFGYQ5mFELRBCygXn3NKMzFjEIoloAF1MuMQqAnAhZAbjE8fQWynGgHnEjAAsgmhhBSCMtl%0A8/fdxbLpqz52CuiBgAWQS4whrJbhj19+frw9pRBmr8Lr774PYTazkgUjIGAB5La8e/w4bUKTqiQr%0AGAsBCyC3+MSY16e2AdVyxAMAZCZgAQBkJmABAGQmYAEAZCZgAQBkJmABAGTmaxqA8UkphZS+nktY%0Aypy/h/3c3d+S5ixC5QQsYHwupjFcTEMIIT4KKZt1b7t0lIcg1QRFoQoGSMACRial9Om3RQhpGtbr%0A5ZeAFWO8vLxp5t0MWIxxcj2fh/VqFaaz2XbY2ny6vRW4YBiGfSIByG4nSMUYw3q9jFfXb978+NO7%0AeHU9D+t1ynq5MG1CmF2G13/5awizV6dNzNkNUimlMJ3NNov373/94e3bzcfFIsQYBS3olxUsYGRS%0ASne/Lz4/fAgjk8m0mco88N87Y4yT+Xz++XFKKUxjDGG1KuYeMhgBAQsYn+0g8hCwSgonq63VqZRS%0ACDE+2gb0TsACxuepy2clXVLbDYPxiW1ArwQsgHOJ4ekrkOVEO+BAAhZA52IIIYWwXDZ/310sm77q%0AY6eADglYAF2LMYTVMvzxy8+Pt6cUwuxVeP3d9yHMZlayoCICFsC5LO8eP06b0KQqyQpqI2ABnEt8%0AYvzrU9uA4glYAA/MKAQyEbAAHphRCGQiYAGEEMwoBHIa9gkD4GzMKATysYIFEEIwoxDIScACeGBG%0AIZCJgAXwwIxCIBMBC6BvZhRCdQQsgN6YUQi1ErAA+mJGIVRLwALomxmFUB0BC6BvZhRCdRzBAACZ%0ACVgAAJkJWAAAmQlYAACZCVgAAJkJWAAAmfmaBoDnpJRCSl/PJSxlzt/Dfu7ub0lzFqEwAhbAcy6m%0AMVxMQwghPgopm3W3r5trRuFDkGqColAFZyBgAbRKKX36bRFCmob1evklYMUYLy9vmnk3uWWcURhj%0AnFzP52G9WoXpbLYdtjafbm8FLuhGGcvbAL3ZCVIxxrBeL+PV9Zs3P/70Ll5dz57vGX8AAATWSURB%0AVMN6nTq5XLgbpF4yo3A3SKWUwnQ22yzev//1h7dvNx8XixBjFLQgLytYAK1SSne/Lz4/fAgjk8m0%0ASTwd/p6aY0ZhjHEyn8+/PEdKYRpjCKtVMfeQQYEELIDnbAeRh4B1jnCSa0bhamt1KqUUQoyPtgHZ%0ACVgAz3nq8llJl9R2w2B8YhuQle/BAgDITMACAMhMwAIAyEzAAgDITMACAMhMixDgpUqfUQh0RsAC%0AeKm+ZhQCgydgAbxIHzMKgVIIWADHuL8cmO7ubt///W9ve5lRCAyegAXwIj3OKAQGT8ACeKm+ZhQC%0AgydgAbxULTMKd0NhSf8dYKAELICxeghSzddNCFWQkYAFMEYxxsn1fB7Wq1WYzmbbYWvz6fZW4ILT%0ACFgAYxJjDOsQJlc3N3/+x7t3j1axprPZZvH+/a8/vH27+bhYfL6vDDiagAUwRjHGyXw+//w4pRSm%0AMYawWrlRH04nYAGM1WprdSqlFEKMj7YBLyZgAYzV7kpVfGIb8CICFkBpYnj6e0ytPcFgCFgAxYgh%0AhBTCctn8ffdq3vRVHzsFPEHAAihFjCGsluGPX35+vD2lEGavwuvvvg9hNrOSBQMgYAGUZnn3+HHa%0AhCZVSVYwFAIWQGni5LBtQG8ELIDcmtEzX8/0K6WhZ0YhnEzAAsjtYhrDxTSEEOKjkLJZ97ZLRzGj%0AEE4mYAFklVL69NsihDQN6/XyS8CKMV5e3jR3qg+YGYWQxbAPdIDi7ASpGGNYr5fx6vrNmx9/ehev%0ArudhvU5ZLxemTQizy/D6L38NYfbqtHvdd4OUGYXwIlawALJKKd39vvj88CGMTCbT5vsUBv57rRmF%0AkIWABZDbdhB5CFglhRMzCuFkAhZAbk9dPivpkpoZhXAyAQugFmYUwmAIWADFM6MQhkbAAiidGYUw%0AOAIWQC3MKITBELAAamFGIQyGIw8AIDMBCwAgMwELACAzAQsAIDMBCwAgMwELACAzX9MAcC4ppZDS%0A13MJzfmD6ghYAOdyMY3hYhpCCPFRqNqsu33dfTMKz/XvwwgJWABnkVL69NsihDQN6/XyS8CKMV5e%0A3jTzbnJ7ZkbhIVIKIc1CWP4r985B1fxOAnAWO0EqxhjW62W8un7z5sef3sWr63lYr1MnlwtPGfac%0AUgoX05g+3X74j//547fp7tOHEGP86jIn8IgVLICzSCnd/b74/PAhpEwm02aZqMPfd3dnFB4jpRA2%0A09OeA0ZIwAI4l+3VqYeAdY4b3E+aR5iaf99MQziKgAVwLk9dVnOpDarkVxIAgMwELACAzAQsAIDM%0ABCwAgMwELACAzLQIAfpmRiFUR8AC6FtfMwqBzghYAL3qY0Yh0DUBC6AP95cD093d7fu//+1tLzMK%0Agc4IWAC96nFGIdAZAQugb33NKAQ6I2AB9M2MQqiO78ECAMhMwAIAyEzAAgDITMACAMhMwAIAyEyL%0AEGCo9s0oPP8+RK1GOI6ABTBU+2YUnlNKIVxMm30BDiZgAQzSvhmF59+NcHExS58+Lpq0BRzCbyQA%0AgzS0Yc8ppbu7WyELAADoxUB+MwLgK0ObR+hGdwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM7rPwE23XS4ZPnirAAAAABJRU5ErkJg%0Agg=="

matplotlib_wtrmrk='assets/cyan-tesseract-3d-200x200.png'


# Region population size
def region_population_end2021(region):
    pop = population.loc[population['region']==region,'2021'].iloc[0]
    return st.markdown(f"<span title='In 2021'><small>Population</small></span><br><font size='5.5'>{int(pop):,}</font>", unsafe_allow_html=True)
    

# Up to date total number of records in a region
def region_total_end2021(region):
    df = region_tl[(region_tl['region']==region)]
    
    current_yr = int(modification_date('assets/models/country-stats.parquet.gzip'))
    #current_yr = 2022
    previous_yr = current_yr-1

    previous_total = int(df[df['date'].dt.year==previous_yr]['total'])
    current_total = int(df[df['date'].dt.year==current_yr]['total'])
    yr_diff = current_total-previous_total

    if yr_diff == 0:
        delta_color='#DEDEDE'
        sign=''
    elif yr_diff < 0:
        delta_color='#00A86B'
        sign=''
    else:
        delta_color='#D92121'
        sign='+'

    return st.markdown(
        f"<span title='Number of records in {current_yr} compared to previous year'><small>Records<br>in {current_yr}</small></span><br><font size='5.5'>{current_total:,}</font><br><font size='2'><span style='color: {delta_color}'>{sign}{yr_diff:,}</span></font>", unsafe_allow_html=True)


#Yearly totals trend in a region
def region_yr_totals_linegarph(region):
    df = region_tl[
        (region_tl['region']==str(region))
    ]

    htext='%{y:,.0f} records<extra></extra>'

    ##Plotly interactive chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['date'].dt.year, y=df['total'], name='Total',
                            line=dict(color=clr, width=4), mode='lines', hovertemplate=htext))
    #Settings
    fig.update_layout(
        height=120, 
        width=280, 
        plot_bgcolor="#333333", 
        paper_bgcolor="#333333", 
        font_size=14,
        font_color="#DEDEDE",
        margin=dict(l=5, r=5, t=5, b=5), 
        showlegend=False,
        xaxis = dict(
            title=None,
            showticklabels=True,
            gridcolor='#484848',
            tickmode='array',
            tickvals=list(df["date"].dt.year)[::7],
            tickformat='%Y',
        ),
        yaxis = dict(
            title=None,
            showticklabels=True,
            gridcolor='#484848',
            zeroline=False
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(72,72,72,0.8)",#484848
            font_color='#DEDEDE'
        )
    )

    #Watermark
    fig.add_layout_image(
            dict(
                source=plotly_wtrmrk,
                x=0.3,
                y=0.8,
                sizex=0.7,
                sizey=0.7,
                sizing="contain",
                opacity=0.05,
                layer="above")
        )

    #Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    #Hide options bar above the chart
    config = {'displayModeBar': False}

    return st.plotly_chart(fig, config=config, use_container_width=True)


#Years of Max and Min number of cases in a region
def region_maxmin(region):
    df = region_tl[(region_tl['region']==region)]
    df = df[
        (df['date'].dt.year != 1991)
        ]

    max = df['total'].max()
    yr_max = (df.loc[df['total']==max,'date'].dt.year).iloc[0]
   
    min = df['total'].min()
    yr_min = (df.loc[df['total']==min,'date'].dt.year).iloc[0]

    return st.markdown(
        f"<br></br><font size='3'><b>Max:<br><b>{max:,}</b><br>({yr_max})</b></font>",
        unsafe_allow_html=True
        )


#Last 10 years trend of Theft and Loss cases in a region
def region_yr_totals_linegrph2012(region):

    current_yr = int(modification_date('assets/models/country-stats.parquet.gzip'))

    ## Plotly interactive chart
    df = region_tl[
            (region_tl['date']>=str(current_yr-10))&
            (region_tl['region']==str(region))
        ]

    theft_tr = df.loc[:,['region','date','theft']]
    loss_tr = df.loc[:,['region','date','loss']]

    htext='%{y:,.0f}'

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=theft_tr['date'].dt.year, y=theft_tr['theft'], name='Theft',
                            line=dict(color=biclr[0], width=3), marker=dict(size=6), mode='lines+markers', hovertemplate=htext))

    fig.add_trace(go.Scatter(x=loss_tr['date'].dt.year, y=loss_tr['loss'], name='Loss',
                            line=dict(color=biclr[1], width=3), marker=dict(size=6), mode='lines+markers', hovertemplate=htext))

    #Settings
    fig.update_layout(
        height=140, 
        width=210, 
        plot_bgcolor="#333333", 
        paper_bgcolor="#333333", 
        font_size=14,
        font_color="#DEDEDE",
        margin=dict(l=5, r=5, t=2.5, b=5), 
        showlegend=False,
        xaxis = dict(
            title=None,
            showticklabels=True,
            gridcolor='#484848',
            tickmode='array',
            tickvals=list(theft_tr["date"].dt.year)[::3],
            tickformat='%Y',
        ),
        yaxis = dict(
            title=None,
            tickfont_size=14,
            showticklabels=True,
            gridcolor='#484848',
            zeroline=False
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(72,72,72,0.8)",#484848
            font_color='#DEDEDE'
        )
    )

    #Watermark
    fig.add_layout_image(
            dict(
                source=plotly_wtrmrk,
                x=0.22,
                y=0.8,
                sizex=0.7,
                sizey=0.7,
                sizing="contain",
                opacity=0.05,
                layer="above")
        )

    #Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    #Hide options bar above the chart
    config = {'displayModeBar': False}

    return st.plotly_chart(fig, config=config, use_container_width=True)


#Country rank of a region in the country by total number of cases (rank #1 == the largest number of records) 
def region_rank_total(region):

    rank = regional_stats[regional_stats['region']==region].index[0]+1
    return st.markdown(
        f"<span title='Ranked by the total number of records, where rank #1 region has the most records in the country.'><small>Rank</small></span><br><font size='5.5'>#{rank}</font>", 
        unsafe_allow_html=True
        )



#Total number of records in a region
def region_total(region):
    df = region_tl[
        (region_tl['region']==region)
    ]

    total = df['total'].sum()
    
    return st.markdown(f"<font size='4'>Total records: <span style='color: {clr}'>{total:,}</span></font>",unsafe_allow_html=True)


#Pie chart with Theft and Loss proportions for a region
def region_theftloss_piechart(region):
    df = regional_stats.loc[:,['region','theft','loss']]
    df = df.melt(id_vars=['region'], value_vars=['theft', 'loss'], var_name='report', value_name='total')
    df = df.set_index('region')
    df = df.loc[region,:]

    fig, ax = plt.subplots(figsize=(1.4,1.4),frameon=False)
    patches, texts, pcts = ax.pie(
        df['total'], 
        colors=biclr,
        autopct='%.0f%%',
        radius=0.85,
        startangle = 90,
        pctdistance=1.2,
        wedgeprops=dict(
            width=0.55,
            edgecolor='#333333',
            lw=3
            ),
        #Segment labels font
        textprops=dict(
            weight='bold',
            size=8
            )
        )
    #Pct values color based on respective segment
    for i, num in enumerate(pcts):
        pcts[i].set_color(biclr[i])

    fig.set_facecolor('#333333')
    plt.axis('tight')

    def watermark2(ax):
        img = Image.open(matplotlib_wtrmrk)
        width, height = ax.figure.get_size_inches()*fig.dpi
        wm_width = int(width/4.5) # make the watermark 1/4 of the figure size
        scaling = (wm_width / float(img.size[0]))
        wm_height = int(float(img.size[1])*float(scaling))
        img = img.resize((wm_width, wm_height))

        imagebox = OffsetImage(img, zoom=1, alpha=0.02)
        imagebox.image.axes = ax

        ao = AnchoredOffsetbox('center', pad=0.01, borderpad=0, child=imagebox)
        ao.patch.set_alpha(0)
        ax.add_artist(ao)

    watermark2(ax)
    #Closing matplotlib 
    plt.close()
    return st.pyplot(fig)


#Total number of Theft and Loss records in a region
def region_theftloss_totals(region):
    df = region_tl[
        (region_tl['region']==region)
    ]

    theft = df['theft'].sum()
    loss = df['loss'].sum()

    return st.markdown(f"""
    <font size='4'>Theft:
    <br>{theft:,}</font>
    <br></br>
    <font size='4'><span style='color: {biclr[1]}'><b>Loss:
    <br>{loss:,}</b></span></font>
    """,
    unsafe_allow_html=True
    )

