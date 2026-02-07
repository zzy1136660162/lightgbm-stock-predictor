# -*- coding: utf-8 -*-
"""
项目模块初始化

导入:
    from src import data_manager, feature, model, backtest
"""

from .data_manager import DataManager, get_data_manager
from .feature import FeatureEngineer, create_features, prepare_data
from .model import StockModel, train_model, evaluate_predictions
from .backtest import Backtester, quick_backtest

__all__ = [
    'DataManager', 'get_data_manager',
    'FeatureEngineer', 'create_features', 'prepare_data',
    'StockModel', 'train_model', 'evaluate_predictions',
    'Backtester', 'quick_backtest'
]
