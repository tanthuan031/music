#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động đổi tên file audio và cập nhật tracks.json
- Chuyển tên file sang dạng chữ cái đầu viết hoa
- Bỏ các ký tự đặc biệt
- Tự động cập nhật tracks.json
"""

import os
import json
import re
import unicodedata
from pathlib import Path

def normalize_text(text):
    """
    Chuẩn hóa text: chữ cái đầu viết hoa, bỏ ký tự đặc biệt
    """
    # Loại bỏ các ký tự đặc biệt như [], (), _, ...
    # Giữ lại chữ cái (bao gồm tiếng Việt), số, khoảng trắng
    # \w trong Python với Unicode bao gồm chữ cái tiếng Việt
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Chuyển sang title case (chữ cái đầu mỗi từ viết hoa)
    # Tách thành các từ
    words = text.split()
    normalized_words = []
    
    for word in words:
        if word:
            # Tìm chữ cái đầu tiên (có thể là chữ cái tiếng Việt)
            first_char = word[0]
            rest = word[1:] if len(word) > 1 else ''
            
            # Chữ cái đầu viết hoa, phần còn lại viết thường
            if first_char.isalpha():
                # Sử dụng capitalize() cho tiếng Việt
                normalized_word = first_char.upper() + rest.lower()
            else:
                normalized_word = word
            
            normalized_words.append(normalized_word)
    
    return ' '.join(normalized_words)

def extract_title_from_filename(filename):
    """
    Trích xuất title từ filename (bỏ phần mở rộng)
    """
    # Bỏ phần mở rộng .mp3
    name_without_ext = os.path.splitext(filename)[0]
    
    # Tách title (thường là phần trước dấu - hoặc [)
    # Lấy phần đầu tiên trước dấu - nếu có
    if ' - ' in name_without_ext:
        title = name_without_ext.split(' - ')[0].strip()
    elif '[' in name_without_ext:
        title = name_without_ext.split('[')[0].strip()
    else:
        title = name_without_ext.strip()
    
    return normalize_text(title)

def process_audio_files():
    """
    Xử lý tất cả file audio trong thư mục audio/
    """
    audio_dir = Path('audio')
    tracks_file = Path('tracks.json')
    
    if not audio_dir.exists():
        print(f"Thư mục {audio_dir} không tồn tại!")
        return
    
    # Đọc tracks.json hiện tại nếu có
    tracks = []
    if tracks_file.exists():
        try:
            with open(tracks_file, 'r', encoding='utf-8') as f:
                tracks = json.load(f)
        except:
            tracks = []
    
    # Tạo mapping từ filePath cũ sang mới
    old_to_new = {}
    
    # Lấy danh sách tất cả file .mp3
    mp3_files = list(audio_dir.glob('*.mp3'))
    
    print(f"Tìm thấy {len(mp3_files)} file audio\n")
    
    # Xử lý từng file
    for mp3_file in mp3_files:
        old_filename = mp3_file.name
        old_path = f"audio/{old_filename}"
        
        # Trích xuất title
        title = extract_title_from_filename(old_filename)
        
        # Tạo tên file mới
        new_filename = f"{title}.mp3"
        new_path = f"audio/{new_filename}"
        
        # Nếu tên file đã thay đổi, đổi tên file
        if old_filename != new_filename:
            new_file_path = audio_dir / new_filename
            
            # Xử lý trường hợp trùng tên
            counter = 1
            while new_file_path.exists() and new_file_path != mp3_file:
                new_filename = f"{title} ({counter}).mp3"
                new_file_path = audio_dir / new_filename
                new_path = f"audio/{new_filename}"
                counter += 1
            
            try:
                mp3_file.rename(new_file_path)
                print(f"✓ Đổi tên: {old_filename[:50]}...")
                print(f"  → {new_filename}")
                old_to_new[old_path] = new_path
            except Exception as e:
                print(f"✗ Lỗi khi đổi tên {old_filename}: {e}")
        else:
            print(f"- Giữ nguyên: {old_filename}")
            old_to_new[old_path] = new_path
    
    # Cập nhật tracks.json
    print(f"\n{'='*60}")
    print("Cập nhật tracks.json...")
    
    # Tạo danh sách tracks mới từ tất cả file
    new_tracks = []
    for idx, mp3_file in enumerate(sorted(audio_dir.glob('*.mp3')), 1):
        filename = mp3_file.name
        title = extract_title_from_filename(filename)
        
        track = {
            "id": f"song{idx}",
            "title": title,
            "filePath": f"audio/{filename}",
            "mediaType": "audio"
        }
        new_tracks.append(track)
    
    # Ghi lại tracks.json
    try:
        with open(tracks_file, 'w', encoding='utf-8') as f:
            json.dump(new_tracks, f, ensure_ascii=False, indent=2)
        print(f"✓ Đã cập nhật {len(new_tracks)} bài hát vào tracks.json")
    except Exception as e:
        print(f"✗ Lỗi khi ghi tracks.json: {e}")
    
    print(f"\n{'='*60}")
    print("Hoàn thành!")

if __name__ == "__main__":
    print("="*60)
    print("Script đổi tên file audio và cập nhật tracks.json")
    print("="*60)
    print()
    
    process_audio_files()

