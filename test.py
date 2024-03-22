import pyupbit
import pandas as pd
import matplotlib.pyplot as plt

access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)



period = 20
multiplier = 2
ratio = 0.9
interval = "minute1"
ticker = "KRW-AXS"

isValidBuy = True
isValidSell = False

# 테스트에 필요한 데이터 가져오기. 4시간봉

df = pyupbit.get_ohlcv(ticker=ticker, interval=interval)
df['middleBand'] = df['close'].rolling(period).mean()  # 중간 밴드
df['upperBand'] = df['close'].rolling(period).mean() + df['close'].rolling(period).std() * multiplier  # 상단 밴드
df['sellingPrice'] = df['middleBand'] + (df['upperBand'] - df['middleBand']) * ratio  # 목표가 밴드


# 비교를 쉽게하기 위해 같은 행에 이전 데이터 값을 불러오기

df['prevHigh'] = df['high'].shift(1)
df['prevMiddle'] = df['middleBand'].shift(1)
df['prevClose'] = df['close'].shift(1)
df['prevSellingPrice'] = df['sellingPrice'].shift(1)

df['isBuying'] = (df['prevMiddle'] <= df['high']) & (df['prevHigh'] < df['prevMiddle'])
df['isSelling'] = df['high'] >= df['prevSellingPrice']

def getROR(row):
    """
    기대 수익률 계산 함수
    """
    global isValidBuy, isValidSell, buyingPrice, sellingPrice

    # 매수
    if (row['prevMiddle'] <= row['high']) & (row['prevHigh'] < row['prevMiddle']) & isValidBuy:
        isValidBuy = False
        isValidSell = True
        buyingPrice = row['prevMiddle']  # 매수가격은 이전 중간밴드

    # 매도
    if (row['high'] >= row['prevSellingPrice']) & isValidSell:
        isValidBuy = True
        isValidSell = False
        sellingPrice = row['prevSellingPrice']  # 매도 가격은 이전 판매 목표가

        return sellingPrice / buyingPrice  # 수익률 = 매도가/매수가

    return 1  # 매도가 일어나지 않은 경우엔 1


# dataframe의 apply 메서드를 적용하면 각 행의 값을
df['ror'] = df.apply(getROR, axis=1)

# 열의 모든 값을 곱하는 cumprod 메서드
ror = df['ror'].cumprod()[-1]

# 백테스팅 수익률 계산 결과
print(df)

df.to_csv('data.csv')

ax = plt.gca()

df.plot(kind="line", y='middleBand', ax=ax)
df.plot(kind="line", y='upperBand', ax=ax)
# df.plot(kind="line", y='LowerBand', ax=ax)
df.plot(kind="line", y='sellingPrice', ax=ax)

buying_points = df[df['isBuying']]
plt.scatter(buying_points.index, buying_points['sellingPrice'], color='red', label='Buying Points')
ax.legend()

plt.show()
plt.savefig('coingraph.png')
print(df['ror'].cumprod()[-1])
#ratio = 0.9 -> 0.9963022678605019
#ratio = 0.8 -> 0.9953447316715252