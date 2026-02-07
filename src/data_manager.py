# -*- coding: utf-8 -*-
"""
数据管理器 - 负责股票数据下载、缓存、读取
"""

import os
import time
import pandas as pd
from datetime import datetime
import akshare as ak

from config.settings import (
    RAW_DATA_DIR, START_DATE, END_DATE,
    AKSHARE_SLEEP, MAX_RETRIES, DATA_CACHE_DAYS
)


class DataManager:
    """股票数据管理器"""
    
    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
    
    def _get_stock_dir(self, stock_code: str) -> str:
        """获取股票数据目录"""
        dir_path = os.path.join(self.raw_data_dir, stock_code)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    def _get_data_filename(self, stock_code: str, update_date: str = None) -> str:
        """
        获取数据文件名
        
        格式: {stock_code}_{update_date}.csv
        例如: 600808_20260207.csv
        """
        if update_date is None:
            update_date = datetime.now().strftime('%Y%m%d')
        return f"{stock_code}_{update_date}.csv"
    
    def _is_cache_valid(self, file_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(file_path):
            return False
        
        # 检查文件修改时间
        mtime = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(mtime)
        now = datetime.now()
        
        # 缓存天数内有效
        days_diff = (now - file_date).days
        return days_diff < DATA_CACHE_DAYS
    
    def _download_stock(self, stock_code: str) -> pd.DataFrame:
        """下载单只股票数据"""
        for retry in range(MAX_RETRIES):
            try:
                time.sleep(AKSHARE_SLEEP)
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period='daily',
                    start_date=START_DATE,
                    end_date=END_DATE
                )
                if df is not None and len(df) >= 100:
                    return df
            except Exception as e:
                time.sleep(0.5)
        return None
    
    def get_stock_data(self, stock_code: str, force_update: bool = False) -> pd.DataFrame:
        """
        获取股票数据（优先读缓存，支持强制更新）
        
        Args:
            stock_code: 股票代码，如 '600808'
            force_update: 是否强制更新
        
        Returns:
            DataFrame: 股票数据
        """
        stock_dir = self._get_stock_dir(stock_code)
        today = datetime.now().strftime('%Y%m%d')
        filename = self._get_data_filename(stock_code, today)
        file_path = os.path.join(stock_dir, filename)
        
        # 1. 尝试读缓存
        if not force_update and self._is_cache_valid(file_path):
            print(f"  [缓存] {stock_code}")
            return pd.read_csv(file_path)
        
        # 2. 下载新数据
        df = self._download_stock(stock_code)
        if df is not None:
            df.to_csv(file_path, index=False)
            print(f"  [下载] {stock_code}")
            return df
        
        # 3. 尝试旧缓存
        old_files = [f for f in os.listdir(stock_dir) if f.startswith(stock_code)]
        if old_files:
            old_file = os.path.join(stock_dir, old_files[0])
            print(f"  [旧缓存] {stock_code}")
            return pd.read_csv(old_file)
        
        return None
    
    def download_all_stocks(self, stock_list, force_update: bool = False) -> dict:
        """
        批量下载股票数据
        
        Args:
            stock_list: [(code, name), ...]
            force_update: 是否强制更新
        
        Returns:
            dict: {code: (name, count, status)}
        """
        results = {}
        total = len(stock_list)
        
        for i, (code, name) in enumerate(stock_list):
            print(f"[{i+1}/{total}] {code} {name}...", end=' ')
            
            df = self.get_stock_data(code, force_update)
            if df is not None:
                results[code] = (name, len(df), '成功')
                print(f"✅ ({len(df)}条)")
            else:
                results[code] = (name, 0, '失败')
                print(f"❌")
        
        return results


# ============ 便捷函数 ============
def get_data_manager() -> DataManager:
    """获取数据管理器实例"""
    return DataManager()


if __name__ == "__main__":
    # 测试
    dm = get_data_manager()
    data = dm.get_stock_data('600808')
    if data is not None:
        print(f"数据形状: {data.shape}")
        print(f"列名: {data.columns.tolist()}")
