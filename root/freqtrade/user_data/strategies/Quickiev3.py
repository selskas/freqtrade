
# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# from technical.indicators import cmf
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class Quickiev3(IStrategy):
	"""
	Sample strategy implementing Informative Pairs - compares stake_currency with USDT.
	Not performing very well - but should serve as an example how to use a referential pair against USDT.
	author@: xmatthias
	github@: https://github.com/freqtrade/freqtrade-strategies

	How to use it?
	> python3 freqtrade -s InformativeSample
	"""
	plot_config ={
	  "main_plot": {
		  "ema": {
			"color": "magenta"
		  },
			  "ema_low": {
				"color": "orange"
			  },
			  "tema_short": {
				"color": "pink"
			  },
			  "tema_med": {
				"color": "olive"
			  },
			"tema_long": {
			  "color": "red"
			},
		"sma_200": {
		  "color": "yellow"
		},
	  "sar": {
		"color": "black"
	  },
	 # "ema_200": {
	#	"color": "brown"
	 # },
	#"ema_50": {
	#  "color": "brown"
	#},
		"bb_lowerband": {
		  "color": "#CCC"
		},
		"bb_middleband": {
		  "color": "#FFF"
		}
	  },
	  "subplots": {

		"CCI": {
			"cci": {}
		},
				# "ema_growth_adx_bbspread": {
				# 	 "ema_growth_adx_bbspread": {}
				# },
		  "RSI": {
			"rsi": {
			  "color": "yellow"
			},
			"rsi30": {"color": "black"},
			"rsi70": {"color": "black"},

			  "adx": {
				"color": "white"
			  },
			  # "ema_growth_adx": {},
				"adx40": {
				  "color": "black"
				}
		  },
		  # "SELL": {
			# "tema_short": {},
			#   "tema_med": {},
			#   "tema_long": {},
			# "bb_middleband": {},
		  # },
		 # "DI": {
		#	"plus_di": {
		#	  "color": "green"
		#	},
		#	"minus_di": {
		#	  "color": "red"
		#	}
		 # },
		  #"MOM": {
		#	"mom": {
		#	  "color": "green"
		#	}
		 # },
		  "BBSPREAD": {
			"bb_spread": {
			  "color": "green"
			},
			  "bb_spread_mark": {
				"color": "black"
			  }
		  },
		   # "EMA": {
			#    "ema1": {"color": "red"},
			# 	   "ema2": {"color": "green"},
			# 	"ema13": {},
			# 	"ema34": {},
			# 	"ema21": {},
			# 	"ema50": {},
			# 	"ema200": {},
		   # },
		  # "VOLUME": {
			#   "volume_mean": {},
			#   "volume": {}
		  # },
			"cmf": {
				"cmf": {},
			},
			  "macd": {
				  "macd": {},
					  "macdsignal": {},
						  "macdhist": {},
							  "macd_mark": {"color": "black"},
			  }
	  }
	}

	#
	# # Minimal ROI designed for the strategy.
	# # This attribute will be overridden if the config file contains "minimal_roi"
	# minimal_roi = {
	# 	"60":  0.01,
	# 	"30":  0.03,
	# 	"20":  0.04,
	# 	"0":  0.05
	# }

	# Optimal stoploss designed for the strategy
	# This attribute will be overridden if the config file contains "stoploss"
	stoploss = -0.30

	# Optimal timeframe for the strategy
	timeframe = '5m'

	# trailing stoploss
	# trailing_stop = False
	# trailing_stop_positive = 0.01
	# trailing_stop_positive_offset = 0.02

	# run "populate_indicators" only for new candle
	# ta_on_candle = False

	# Experimental settings (configuration will overide these if set)
	# use_sell_signal = True
	# sell_profit_only = True
	# ignore_roi_if_buy_signal = False

	# Optional order type mapping
	order_types = {
		'buy': 'limit',
		'sell': 'limit',
		'stoploss': 'market',
		'stoploss_on_exchange': False
	}

	def informative_pairs(self):
		return [("BTC/USDT", "5m"),
		]

	def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

		# fetch live / historical candle (OHLCV) data for the first informative pair
		if self.dp:
			inf_pair, inf_timeframe = self.informative_pairs()[0]
			informative = self.dp.get_pair_dataframe(pair=inf_pair,
													 timeframe=inf_timeframe)

		#  BTC
		dataframe['close_BTC'] = informative['close']
		dataframe['tema_BTC'] = ta.TEMA(informative, timeperiod=9)
		dataframe['tema20_BTC'] = ta.TEMA(informative, timeperiod=12)
		dataframe['tema3_BTC'] = ta.TEMA(informative, timeperiod=3)
		bollinger = qtpylib.bollinger_bands(informative['close'], window=20, stds=2)
		dataframe['bb_lowerband_BTC'] = bollinger['lower']
		dataframe['bb_middleband_BTC'] = bollinger['mid']
		dataframe['bb_upperband_BTC'] = bollinger['upper']
		dataframe['bb_spread_BTC'] = dataframe['bb_lowerband_BTC'] / dataframe['bb_middleband_BTC']
		dataframe['bb_spread_mark'] = 0.96
		dataframe['adx_BTC'] = ta.ADX(informative)
		dataframe['adx_mark'] = 40
		dataframe['sma_200_BTC'] = ta.SMA(informative, timeperiod=200)
		dataframe['sar_BTC'] = ta.SAR(informative)
		dataframe['rsi_BTC'] = ta.RSI(informative)
		dataframe['cci_BTC'] = ta.CCI(informative, timeperiod=10)

		# Current pair
		dataframe['close'] = dataframe['close']
		dataframe['tema_med'] = ta.TEMA(dataframe, timeperiod=9)
		dataframe['tema_short'] = ta.TEMA(dataframe, timeperiod=2)
		dataframe['tema_long'] = ta.TEMA(dataframe, timeperiod=26)

		bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
		dataframe['bb_lowerband'] = bollinger['lower']
		dataframe['bb_middleband'] = bollinger['mid']
		dataframe['bb_upperband'] = bollinger['upper']
		dataframe['bb_spread'] = dataframe['bb_lowerband'] / dataframe['bb_middleband']

		dataframe['adx'] = ta.ADX(dataframe)
		dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)
		dataframe['sar'] = ta.SAR(dataframe)

		dataframe['mfi'] = ta.MFI(dataframe)
		stoch_fast = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)
		dataframe['fastd'] = stoch_fast['fastd']
		dataframe['fastk'] = stoch_fast['fastk']
		dataframe['cci'] = ta.CCI(dataframe, timeperiod=10)
		dataframe['rsi'] = ta.RSI(dataframe)
		dataframe['rsi30'] = 30
		dataframe['rsi70'] = 70

		# dataframe['cmf'] = cmf(dataframe, 10)

		# MACD
		macd = ta.MACD(dataframe)
		dataframe['macd'] = macd['macd']
		dataframe['macdsignal'] = macd['macdsignal']
		dataframe['macdhist'] = macd['macdhist']
		dataframe['macd_mark'] = 0


		dataframe['ema'] = ta.EMA(dataframe, timeperiod=10)
		dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=26)
		# dataframe['ema1'] = ta.EMA(dataframe, timeperiod=3)
		# dataframe['ema2'] = ta.EMA(dataframe, timeperiod=14)
		dataframe['ema_low'] = ta.EMA(dataframe, timeperiod=5, price='low')
		# dataframe['ema_reversed'] = dataframe['ema'].shift(1)
		# dataframe['ema_growth'] = (dataframe['ema']-dataframe['ema_reversed'])/dataframe['ema']*100
		# dataframe['ema_growth_adx'] = dataframe['ema_growth'] * dataframe['adx']
		# dataframe['ema_growth_adx_bbspread'] = dataframe['ema_growth'] * dataframe['adx'] * dataframe['bb_spread'] * dataframe['macd'].shift(1)

		return dataframe

	def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		"""
		Based on TA indicators, populates the buy signal for the given dataframe
		:param dataframe: DataFrame
		:return: DataFrame with buy column
		"""
		dataframe.loc[
			(
				# BTC
				(
					(dataframe['adx_BTC'] > 30) &
					(dataframe['tema3_BTC'] < dataframe['bb_middleband_BTC']) &
					(dataframe['tema3_BTC'] > dataframe['tema3_BTC'].shift(1)) &
					(dataframe['sma_200_BTC'] > dataframe['bb_middleband_BTC']) &
					(dataframe['sma_200_BTC'] > dataframe['close_BTC']) &
					(dataframe['tema3_BTC'] < dataframe['sar_BTC']) &
					(dataframe['bb_spread_BTC'] < 0.97) &
					(dataframe['rsi_BTC'] > 34) &

					# Current pair
					(dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
					(dataframe['adx'] > 30)
				)

				# Current PAIR
				|
				(
					(dataframe['adx'] > 49) &
					(dataframe['tema_short'] < dataframe['bb_middleband']) &
					(dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
					(dataframe['sma_200'] > dataframe['bb_middleband']) &
					(dataframe['sma_200'] > dataframe['close']) &
					(dataframe['tema_short'] < dataframe['sar']) &
					(dataframe['bb_spread'] < 0.97) &
					(dataframe['rsi'] > 30)
				)
				|
				(
					(dataframe['open'] < dataframe['ema_low']) &
					(dataframe['adx'] > 35) &
					(dataframe['mfi'] < 30) &
					(
						(dataframe['fastk'] < 30) &
						(dataframe['fastd'] < 30) &
						(qtpylib.crossed_above(dataframe['fastk'], dataframe['fastd']))
					) &
					(dataframe['cci'] < -150) &
					(dataframe['bb_spread'] < 0.95)
				)
				|
				(
					# (qtpylib.crossed_above(dataframe['ema1'], dataframe['ema2'])) &
					(qtpylib.crossed_above(dataframe['tema_short'], dataframe['tema_long'])) &
					# (dataframe['volume'] > dataframe['volume'].rolling(window=4).mean()) &
					(dataframe['tema_short'] < dataframe['bb_middleband']) &
					(dataframe['bb_spread'] < 0.95) &
					(dataframe['cci'] < 0) &
					(dataframe['adx'] > 38) &
					(dataframe['tema_med'] > dataframe['tema_med'].shift(1)) &
					(dataframe['tema_short'] < dataframe['sar'])
				)
				|
				(
					(dataframe['rsi'] > 40) &
					(dataframe['rsi'] < dataframe['rsi_long']) &
					(dataframe['adx'] < 25 & dataframe['adx'] > 15) &
					(dataframe['tema_short'] < dataframe['tema_long']) &
					(dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
					(dataframe['adx'] > dataframe['adx'].shift(1)) &
					# (dataframe['bb_upperband'] > dataframe['bb_upperband'].shift(1)) &
					(dataframe['volume'] > dataframe['volume'].rolling(window=4).mean())*1.9
				)
				|
				(
					# (dataframe['rsi'] > 40) &
					(dataframe['rsi'] > dataframe['rsi_long']) &
					(dataframe['adx'] < 70) &
					(dataframe['tema_short'] < dataframe['tema_long']) &
					(dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
					(dataframe['adx'] > dataframe['adx'].shift(1)) &
					# (dataframe['bb_upperband'] > dataframe['bb_upperband'].shift(1)) &
					(dataframe['volume'] > dataframe['volume'].rolling(window=4).mean())*1.9
				)

						# (
						# 	(dataframe['ema_growth_adx_bbspread'] > dataframe['ema_growth_adx_bbspread'].shift(1)) &
						# 	(dataframe['tema_long'] > dataframe['tema_long'].shift(1)) &
						# 	(dataframe['ema_low'] < dataframe['sar'])
						# )





						# |
						# (
						# 	(dataframe['adx'] > 45) &
						# 	# (dataframe['tema_short'] < dataframe['sar']) &
						# 	(dataframe['tema_short'] > dataframe['ema']) &
						# 	(dataframe['tema_short'] > dataframe['tema_long']) &
						# 	(dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
						# 	(dataframe['tema_long'] > dataframe['tema_long'].shift(1)) &
						# 	(dataframe['tema_med'] < dataframe['bb_middleband']) &
						# 	# (dataframe['cci'] < -40) &
						# 	 # (dataframe['rsi'] < 60)
						# 	(dataframe['bb_spread'] < 0.97)
						# )
						# |
						# (
						# 	# qtpylib.crossed_above(dataframe['tema_short'], dataframe['ema'])
						# 	# & (dataframe['ema'] > dataframe['ema'].shift(1))
						# 	 (dataframe['tema_short'] > dataframe['tema_short'].shift(1)) &
						# 	  (dataframe['macdhist'] > dataframe['macdhist'].shift(1)) &
						# 	   (dataframe['macdsignal'] > dataframe['macdsignal'].shift(1)) &
						# 	   (dataframe['tema_long'] > dataframe['tema_long'].shift(1)) &
						# 	  (dataframe['tema_short'] < dataframe['sar']) &
						# 	  (dataframe['adx'] < 20)& (dataframe['rsi'] > 50)&
						# 	  (dataframe['bb_spread'] < 0.99)
						# 	 # & (dataframe['sma_200'] > dataframe['sma_200'].shift(1))
						# 	# & (dataframe['close'] < dataframe['bb_lowerband'])
						# 	# (dataframe['bb_spread'] < 0.96) &
						# 	# & (dataframe['cci'] < 0)
						# 	#
						# )
						# |
						# (
						# 	qtpylib.crossed_above(dataframe['tema_short'], dataframe['ema'])
						# 	# & (dataframe['ema'] > dataframe['ema'].shift(1))
						# 	# & (dataframe['bb_lowerband'] > dataframe['bb_lowerband'].shift(1))
						# 	& (dataframe['close'] < dataframe['bb_middleband'])
						# 	# (dataframe['bb_spread'] < 0.96) &
						# 	# & (dataframe['cci'] < 0)
						# 	# (dataframe['rsi'] > 40)
						# )

			),
			'buy'] = 1

		return dataframe

	def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		"""
		Based on TA indicators, populates the sell signal for the given dataframe
		:param dataframe: DataFrame
		:return: DataFrame with buy column
		"""
		dataframe.loc[
			(
				# (
				# 	(dataframe['adx'] > 25) & # 60
				# 	(dataframe['tema_med'] > dataframe['bb_middleband']) &
				# 	(dataframe['tema_med'] < dataframe['tema_med'].shift(1))
				# )
				# |
				# (
				# 	(dataframe['tema_short'] < dataframe['tema_short'].shift(1)) &
				# 	(dataframe['tema_short'] > dataframe['sar']) &
				# 	(dataframe['tema_short'] > dataframe['bb_middleband'])
				# )
				# |
				# (
				# 	(dataframe['tema_med'] < dataframe['tema_med'].shift(1)) &
				# 	(dataframe['tema_med'] > dataframe['sar']) #&
				# 	#(dataframe['tema3'] > dataframe['bb_middleband'])
				# )
				# |
				# (
				# 	(dataframe['tema_short'] < dataframe['tema_short'].shift(1)) &
				# 	(dataframe['tema_med'] < dataframe['tema_med'].shift(1))
				# 	 # & (dataframe['tema'] > dataframe['bb_middleband'])
				# )

				# (dataframe['tema_short'] < dataframe['tema_short'].shift(1))
				(qtpylib.crossed_below(dataframe['tema_short'], dataframe['tema_long']))
			),
			'sell'] = 1
		return dataframe
