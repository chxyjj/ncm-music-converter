#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐格式转换器 - 安卓版本
NCM到MP3格式转换应用
made by 陈高君
"""

import os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast

from ncm_decoder import NCMDecoder
from file_manager import AndroidFileManager


class MainScreen(Screen):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = AndroidFileManager()
        self.decoder = NCMDecoder()
        self.dialog = None
        
        # 绑定文件管理器事件
        self.file_manager.bind(on_scan_progress=self.on_scan_progress)
        self.file_manager.bind(on_scan_complete=self.on_scan_complete)
        self.file_manager.bind(on_convert_progress=self.on_convert_progress)
        self.file_manager.bind(on_convert_complete=self.on_convert_complete)
    
    def select_files(self):
        """选择文件"""
        self.update_status("正在打开文件选择器...")
        self.file_manager.select_files(self.on_file_operation_result)
    
    def scan_all_files(self):
        """全盘扫描"""
        # 显示目录选择对话框
        self.show_directory_dialog()
    
    def show_directory_dialog(self):
        """显示目录选择对话框"""
        directories = self.file_manager.get_common_directories()
        
        if not directories:
            toast("无法访问存储目录，请检查权限")
            return
        
        # 创建目录选择按钮
        buttons = []
        for directory in directories:
            dir_name = os.path.basename(directory) or directory
            button = MDFlatButton(
                text=f"扫描 {dir_name}",
                on_release=lambda x, d=directory: self.start_scan(d)
            )
            buttons.append(button)
        
        # 添加取消按钮
        buttons.append(MDFlatButton(
            text="取消",
            on_release=self.close_dialog
        ))
        
        self.dialog = MDDialog(
            title="选择扫描目录",
            text="请选择要扫描NCM文件的目录：",
            buttons=buttons,
        )
        self.dialog.open()
    
    def start_scan(self, directory):
        """开始扫描指定目录"""
        self.close_dialog()
        self.update_status(f"正在扫描目录: {directory}")
        self.ids.progress_bar.value = 0
        self.ids.progress_label.text = "扫描中..."
        
        # 禁用按钮
        self.set_buttons_enabled(False)
        
        self.file_manager.scan_directory(directory, self.on_file_operation_result)
    
    def start_conversion(self):
        """开始转换"""
        if self.file_manager.get_file_count() == 0:
            toast("没有选择任何文件")
            return
        
        self.update_status("正在转换文件...")
        self.ids.progress_bar.value = 0
        self.ids.progress_label.text = "转换中..."
        
        # 禁用按钮
        self.set_buttons_enabled(False)
        
        self.file_manager.convert_files(self.decoder, self.on_file_operation_result)
    
    def clear_files(self):
        """清空文件列表"""
        self.file_manager.clear_files()
        self.update_file_list()
        self.update_status("文件列表已清空")
        self.ids.progress_bar.value = 0
        self.ids.progress_label.text = ""
        
        # 禁用转换按钮
        self.ids.convert_btn.disabled = True
    
    def close_dialog(self, *args):
        """关闭对话框"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    def update_status(self, message):
        """更新状态信息"""
        self.ids.status_label.text = message
    
    def update_file_list(self):
        """更新文件列表"""
        file_list = self.ids.file_list
        file_list.clear_widgets()
        
        files = self.file_manager.get_files()
        file_count = len(files)
        
        # 更新文件数量显示
        self.ids.file_count_label.text = f"已选择文件: {file_count} 个"
        
        # 更新转换按钮状态
        self.ids.convert_btn.disabled = file_count == 0
        
        # 添加文件项到列表
        for file_path in files:
            file_name = os.path.basename(file_path)
            dir_name = os.path.dirname(file_path)
            
            item = TwoLineListItem(
                text=file_name,
                secondary_text=dir_name,
                theme_text_color="Primary"
            )
            file_list.add_widget(item)
    
    def set_buttons_enabled(self, enabled):
        """设置按钮启用状态"""
        self.ids.select_files_btn.disabled = not enabled
        self.ids.scan_all_btn.disabled = not enabled
        self.ids.convert_btn.disabled = not enabled or self.file_manager.get_file_count() == 0
        self.ids.clear_btn.disabled = not enabled
    
    # 事件处理方法
    def on_scan_progress(self, instance, progress, current_path):
        """扫描进度更新"""
        self.ids.progress_bar.value = progress
        path_name = os.path.basename(current_path)
        self.ids.progress_label.text = f"扫描中: {path_name}... ({progress}%)"
    
    def on_scan_complete(self, instance, file_count, files):
        """扫描完成"""
        self.update_file_list()
        self.update_status(f"扫描完成，找到 {file_count} 个NCM文件")
        self.ids.progress_bar.value = 100
        self.ids.progress_label.text = "扫描完成"
        
        # 重新启用按钮
        self.set_buttons_enabled(True)
        
        if file_count > 0:
            toast(f"找到 {file_count} 个NCM文件")
        else:
            toast("未找到NCM文件")
    
    def on_convert_progress(self, instance, progress, current_file):
        """转换进度更新"""
        self.ids.progress_bar.value = progress
        file_name = os.path.basename(current_file)
        self.ids.progress_label.text = f"转换中: {file_name}... ({progress}%)"
    
    def on_convert_complete(self, instance, converted_files, failed_files):
        """转换完成"""
        success_count = len(converted_files)
        fail_count = len(failed_files)
        
        self.update_status(f"转换完成！成功: {success_count}, 失败: {fail_count}")
        self.ids.progress_bar.value = 100
        self.ids.progress_label.text = "转换完成"
        
        # 重新启用按钮
        self.set_buttons_enabled(True)
        
        # 显示结果
        if success_count > 0:
            toast(f"成功转换 {success_count} 个文件")
        if fail_count > 0:
            toast(f"转换失败 {fail_count} 个文件")
    
    def on_file_operation_result(self, success, message):
        """文件操作结果回调"""
        if success:
            toast(message)
        else:
            toast(f"操作失败: {message}")
            # 重新启用按钮
            self.set_buttons_enabled(True)


class NCMConverterApp(MDApp):
    """NCM转换器应用"""
    
    def build(self):
        """构建应用"""
        # 设置主题
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"
        
        # 设置应用标题
        self.title = "网易云音乐格式转换器"
        
        # 创建主界面
        return MainScreen()
    
    def on_start(self):
        """应用启动时调用"""
        toast("欢迎使用网易云音乐格式转换器")


if __name__ == "__main__":
    NCMConverterApp().run()
