#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模块 - 安卓版本
处理安卓文件系统访问、文件选择、扫描等功能
"""

import os
import threading
from plyer import filechooser
from kivy.event import EventDispatcher
from kivy.clock import Clock


class AndroidFileManager(EventDispatcher):
    """安卓文件管理器"""
    
    __events__ = ('on_scan_progress', 'on_scan_complete', 'on_convert_progress', 'on_convert_complete')
    
    def __init__(self):
        super().__init__()
        self.ncm_files = []
        self.is_scanning = False
        self.is_converting = False
        
    def select_files(self, callback=None):
        """选择NCM文件"""
        try:
            # 使用plyer的文件选择器
            filechooser.open_file(
                on_selection=self._on_file_selected,
                filters=[("NCM files", "*.ncm"), ("All files", "*")]
            )
            if callback:
                callback(True, "文件选择器已打开")
        except Exception as e:
            if callback:
                callback(False, f"打开文件选择器失败: {str(e)}")
    
    def _on_file_selected(self, selection):
        """文件选择回调"""
        if selection:
            ncm_files = [f for f in selection if f.lower().endswith('.ncm')]
            self.ncm_files.extend(ncm_files)
            self.dispatch('on_scan_complete', len(ncm_files), ncm_files)
    
    def scan_directory(self, directory_path, callback=None):
        """扫描目录中的NCM文件"""
        if self.is_scanning:
            if callback:
                callback(False, "正在扫描中，请稍候")
            return
        
        self.is_scanning = True
        self.ncm_files = []
        
        # 在后台线程中执行扫描
        thread = threading.Thread(
            target=self._scan_directory_thread,
            args=(directory_path, callback)
        )
        thread.daemon = True
        thread.start()
    
    def _scan_directory_thread(self, directory_path, callback):
        """在后台线程中扫描目录"""
        try:
            found_files = []
            total_dirs = 0
            scanned_dirs = 0
            
            # 首先计算总目录数
            for root, dirs, files in os.walk(directory_path):
                total_dirs += 1
            
            # 扫描文件
            for root, dirs, files in os.walk(directory_path):
                scanned_dirs += 1
                
                # 更新进度
                progress = int((scanned_dirs / total_dirs) * 100)
                Clock.schedule_once(
                    lambda dt: self.dispatch('on_scan_progress', progress, root),
                    0
                )
                
                # 查找NCM文件
                for file in files:
                    if file.lower().endswith('.ncm'):
                        file_path = os.path.join(root, file)
                        found_files.append(file_path)
            
            self.ncm_files = found_files
            self.is_scanning = False
            
            # 在主线程中触发完成事件
            Clock.schedule_once(
                lambda dt: self.dispatch('on_scan_complete', len(found_files), found_files),
                0
            )
            
            if callback:
                Clock.schedule_once(
                    lambda dt: callback(True, f"扫描完成，找到 {len(found_files)} 个NCM文件"),
                    0
                )
                
        except Exception as e:
            self.is_scanning = False
            if callback:
                Clock.schedule_once(
                    lambda dt: callback(False, f"扫描失败: {str(e)}"),
                    0
                )
    
    def get_common_directories(self):
        """获取常用目录路径"""
        try:
            from android.storage import primary_external_storage_path
            external_path = primary_external_storage_path()
            
            common_dirs = [
                external_path,
                os.path.join(external_path, "Music"),
                os.path.join(external_path, "Download"),
                os.path.join(external_path, "netease"),
                os.path.join(external_path, "Android/data/com.netease.cloudmusic/files/Music"),
            ]
            
            # 过滤存在的目录
            existing_dirs = [d for d in common_dirs if os.path.exists(d)]
            return existing_dirs
            
        except Exception as e:
            # 如果无法获取安卓存储路径，返回默认路径
            return ["/storage/emulated/0", "/sdcard"]
    
    def convert_files(self, decoder, callback=None):
        """批量转换NCM文件"""
        if self.is_converting:
            if callback:
                callback(False, "正在转换中，请稍候")
            return
        
        if not self.ncm_files:
            if callback:
                callback(False, "没有找到NCM文件")
            return
        
        self.is_converting = True
        
        # 在后台线程中执行转换
        thread = threading.Thread(
            target=self._convert_files_thread,
            args=(decoder, callback)
        )
        thread.daemon = True
        thread.start()
    
    def _convert_files_thread(self, decoder, callback):
        """在后台线程中转换文件"""
        try:
            total_files = len(self.ncm_files)
            converted_files = []
            failed_files = []
            
            for i, ncm_file in enumerate(self.ncm_files):
                # 更新进度
                progress = int(((i + 1) / total_files) * 100)
                Clock.schedule_once(
                    lambda dt, p=progress, f=ncm_file: self.dispatch('on_convert_progress', p, f),
                    0
                )
                
                # 转换文件
                success, output_path, error = decoder.decode_ncm_file(ncm_file)
                
                if success:
                    converted_files.append(output_path)
                else:
                    failed_files.append((ncm_file, error))
            
            self.is_converting = False
            
            # 在主线程中触发完成事件
            Clock.schedule_once(
                lambda dt: self.dispatch('on_convert_complete', converted_files, failed_files),
                0
            )
            
            if callback:
                success_count = len(converted_files)
                fail_count = len(failed_files)
                message = f"转换完成！成功: {success_count}, 失败: {fail_count}"
                Clock.schedule_once(
                    lambda dt: callback(True, message),
                    0
                )
                
        except Exception as e:
            self.is_converting = False
            if callback:
                Clock.schedule_once(
                    lambda dt: callback(False, f"转换失败: {str(e)}"),
                    0
                )
    
    def clear_files(self):
        """清空文件列表"""
        self.ncm_files = []
    
    def get_file_count(self):
        """获取文件数量"""
        return len(self.ncm_files)
    
    def get_files(self):
        """获取文件列表"""
        return self.ncm_files.copy()
    
    # 事件处理方法
    def on_scan_progress(self, progress, current_path):
        """扫描进度事件"""
        pass
    
    def on_scan_complete(self, file_count, files):
        """扫描完成事件"""
        pass
    
    def on_convert_progress(self, progress, current_file):
        """转换进度事件"""
        pass
    
    def on_convert_complete(self, converted_files, failed_files):
        """转换完成事件"""
        pass


def test_file_manager():
    """测试文件管理器"""
    fm = AndroidFileManager()
    print("安卓文件管理器初始化完成")
    
    # 获取常用目录
    dirs = fm.get_common_directories()
    print(f"常用目录: {dirs}")


if __name__ == "__main__":
    test_file_manager()
