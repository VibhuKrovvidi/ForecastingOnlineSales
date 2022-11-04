import pandas as pd
import numpy as np
import math
from datetime import datetime
from dateutil import parser
import matplotlib.pyplot as plt
# from statsmodels.tsa.arima.model import ARIMA

from pandas.plotting import autocorrelation_plot
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error

from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
from statsmodels.tsa.stattools import acovf
from matplotlib.ticker import FormatStrFormatter
import datetime as dt
from scipy import signal
from scipy.fft import fft, ifft
from matplotlib.ticker import AutoMinorLocator
from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot, abline_plot
from statsmodels.stats.anova import anova_lm
import statsmodels.api as sm

try:
	from pmdarima.arima import ARIMA
except:
	print("Please Install pmdarima: pip install pmdarima")

class ForecastSales:

	def __init__(self, name, age):
		self.name = name
		self.age = age

	def working(self):
		print(self.name, self.age)


if __name__ == '__main__':
	forecast = ForecastSales("Vibhu", 22)
	forecast.working()