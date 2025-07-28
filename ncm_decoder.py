#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM文件解密模块 - 安卓版本
用于将网易云音乐的NCM格式文件转换为MP3格式
适配安卓平台
"""

import os
import json
import base64
import binascii
from Crypto.Cipher import AES


class NCMDecoder:
    """NCM文件解密器"""
    
    def __init__(self):
        # NCM文件的固定密钥
        self.core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
        self.meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
        
    def _aes_decrypt(self, data, key):
        """AES解密"""
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.decrypt(data)
    
    def _decode_netease_info(self, data):
        """解码网易云音乐信息"""
        try:
            # 去除前缀
            data = data[22:]
            # Base64解码
            data = base64.b64decode(data)
            # AES解密
            data = self._aes_decrypt(data, self.meta_key)
            # 去除前缀 "music:"
            data = data[6:]
            # 解析JSON
            return json.loads(data.decode('utf-8').rstrip('\x00'))
        except Exception as e:
            print(f"解码音乐信息失败: {e}")
            return None
    
    def _build_key_box(self, key):
        """构建密钥盒"""
        box = list(range(256))
        j = 0
        for i in range(256):
            j = (j + box[i] + key[i % len(key)]) & 0xff
            box[i], box[j] = box[j], box[i]
        return box
    
    def _decrypt_data(self, data, box):
        """解密音频数据"""
        out = bytearray()
        for i, byte in enumerate(data):
            j = (i + 1) & 0xff
            k = box[(box[j] + box[(box[j] + j) & 0xff]) & 0xff]
            out.append(byte ^ k)
        return bytes(out)
    
    def decode_ncm_file(self, ncm_path, output_path=None):
        """
        解码NCM文件
        
        Args:
            ncm_path: NCM文件路径
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            tuple: (是否成功, 输出文件路径, 错误信息)
        """
        try:
            with open(ncm_path, 'rb') as f:
                # 检查文件头
                header = f.read(8)
                if header != b'CTENFDAM':
                    return False, None, "不是有效的NCM文件"
                
                # 跳过2字节
                f.read(2)
                
                # 读取密钥长度和密钥数据
                key_length = int.from_bytes(f.read(4), byteorder='little')
                key_data = f.read(key_length)
                
                # 解密密钥
                for i in range(len(key_data)):
                    key_data = key_data[:i] + bytes([key_data[i] ^ 0x64]) + key_data[i+1:]
                
                # AES解密密钥
                key_data = self._aes_decrypt(key_data, self.core_key)
                key_data = key_data[17:]  # 去除前缀
                
                # 读取音乐信息长度和数据
                meta_length = int.from_bytes(f.read(4), byteorder='little')
                if meta_length > 0:
                    meta_data = f.read(meta_length)
                    music_info = self._decode_netease_info(meta_data)
                else:
                    music_info = None
                
                # 跳过CRC32
                f.read(4)
                
                # 跳过专辑图片
                f.read(4)  # 图片长度
                image_length = int.from_bytes(f.read(4), byteorder='little')
                if image_length > 0:
                    image_data = f.read(image_length)
                else:
                    image_data = None
                
                # 读取音频数据
                audio_data = f.read()
                
                # 构建解密密钥盒
                key_box = self._build_key_box(key_data)
                
                # 解密音频数据
                decrypted_data = self._decrypt_data(audio_data, key_box)
                
                # 确定输出文件路径和格式
                if output_path is None:
                    base_name = os.path.splitext(ncm_path)[0]
                    # 根据音乐信息确定格式
                    if music_info and 'format' in music_info:
                        ext = music_info['format'].lower()
                        if ext not in ['mp3', 'flac']:
                            ext = 'mp3'  # 默认为mp3
                    else:
                        ext = 'mp3'  # 默认为mp3
                    output_path = f"{base_name}.{ext}"
                
                # 写入解密后的音频文件
                with open(output_path, 'wb') as out_f:
                    out_f.write(decrypted_data)
                
                # 安卓版本暂时跳过标签信息添加，专注于格式转换
                # 可以在后续版本中添加标签支持

                return True, output_path, None

        except Exception as e:
            return False, None, f"解码失败: {str(e)}"


def test_decoder():
    """测试解码器"""
    decoder = NCMDecoder()
    # 这里可以添加测试代码
    print("NCM解码器初始化完成")


if __name__ == "__main__":
    test_decoder()
