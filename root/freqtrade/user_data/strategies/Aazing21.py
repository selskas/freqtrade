# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy.interface import IStrategy

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class Amazing21(IStrategy):
	INTERFACE_VERSION = 2

	# minimal_roi = {
	#     "0": 0.1,
	#     "100": 0.08,
	#     "200": 0.06,
	#     "300": 0.04,
	#     "400": 0.02,
	#     "500": 0.01,
	#     "600": 0
	# }

	minimal_roi = {
		"0": 0.10,
		"5": 0.05,
		"10": 0.01,
		"15": 0
	}

	stoploss = -0.5

	# Trailing stoploss
	trailing_stop = False
	# trailing_only_offset_is_reached = False
	# trailing_stop_positive = 0.01
	# trailing_stop_positive_offset = 0.0  # Disabled / not configured

	# Optimal ticker interval for the strategy.
	timeframe = '5m'

	# Run "populate_indicators()" only for new candle.
	process_only_new_candles = False

	# These values can be overridden in the "ask_strategy" section in the config.
	use_sell_signal = True
	sell_profit_only = True
	ignore_roi_if_buy_signal = True

	# Number of candles the strategy requires before producing valid signals
	#startup_candle_count: int = 1

	# Optional order type mapping.
	order_types = {
		'buy': 'limit',
		'sell': 'limit',
		'stoploss': 'market',
		'stoploss_on_exchange': False
	}

	# Optional order time in force.
	# order_time_in_force = {
	#     'buy': 'gtc',
	#     'sell': 'gtc'
	# }

	# plot_config = {
	#     'main_plot': {
	#         'tema': {},
	#         'sar': {'color': 'white'},
	#     },
	#     'subplots': {
	#         "MACD": {
	#             'macd': {'color': 'blue'},
	#             'macdsignal': {'color': 'orange'},
	#         },
	#         "RSI": {
	#             'rsi': {'color': 'red'},
	#         }
	#     }
	# }

	# Buy hyperspace params:
	# buy_params = {
	#  'rsi-enabled': True, 'rsi-value': 29, 'trigger': 'bb_lower1'
	# }


	def informative_pairs(self):
		"""
		Define additional, informative pair/interval combinations to be cached from the exchange.
		These pair/interval combinations are non-tradeable, unless they are part
		of the whitelist as well.
		For more information, please consult the documentation
		:return: List of tuples in the format (pair, interval)
			Sample: return [("ETH/USDT", "5m"),
							("BTC/USDT", "15m"),
							]
		"""
		return []

	def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:


		dataframe['rsi'] = ta.RSI(dataframe)
		bollinger2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
		dataframe['bb2_lowerband'] = bollinger2['lower']
		dataframe['bb2_middleband'] = bollinger2['mid']
		dataframe['bb2_upperband'] = bollinger2['upper']
		bollinger3 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=3)
		dataframe['bb3_lowerband'] = bollinger3['lower']
		dataframe['bb3_middleband'] = bollinger3['mid']
		dataframe['bb3_upperband'] = bollinger3['upper']
		# bollinger4 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=4)
		# dataframe['bb4_lowerband'] = bollinger4['lower']
		# dataframe['bb4_middleband'] = bollinger4['mid']
		# dataframe['bb4_upperband'] = bollinger4['upper']

		return dataframe

	def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		"""
		Based on TA indicators, populates the buy signal for the given dataframe
		:param dataframe: DataFrame populated with indicators
		:param metadata: Additional information, like the currently traded pair
		:return: DataFrame with buy column
		"""
		dataframe.loc[
			(
				# (dataframe['rsi'] > 40) &
				# (dataframe['close'] < dataframe['bb2_lowerband']) &
				# (dataframe['volume'] > 0)
				((dataframe['rsi'] <= 35) | (dataframe['close'] < dataframe['bb3_lowerband'])) &
				(dataframe['volume'] > 400000)
			),
			'buy'] = 1

		return dataframe

	def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		"""
		Based on TA indicators, populates the sell signal for the given dataframe
		:param dataframe: DataFrame populated with indicators
		:param metadata: Additional information, like the currently traded pair
		:return: DataFrame with buy column
		"""
		dataframe.loc[
			(
				(
					# (dataframe['close'] > dataframe['bb4_upperband']) &
					# (dataframe['rsi'] > 70)
					#(dataframe['rsi'] > 85) |
					(dataframe['close'] > dataframe['bb2_upperband'])
				)
			),
			'sell'] = 1
		return dataframe
