"""
개별 스프라이트 이미지들을 하나의 스프라이트 시트로 합치는 스크립트
"""
from PIL import Image
import os

def create_sprite_sheet_from_individual_images(image_folder, output_file, prefix, start_idx, end_idx, sprite_width=512, sprite_height=512):
    """
    개별 이미지들을 하나의 스프라이트 시트로 합침
    
    Args:
        image_folder: 이미지가 있는 폴더
        output_file: 출력 파일 경로
        prefix: 파일 이름 접두사 (예: 'HoHoYee_Parry_Sky')
        start_idx: 시작 인덱스
        end_idx: 끝 인덱스 (포함)
        sprite_width: 개별 스프라이트 너비
        sprite_height: 개별 스프라이트 높이
    """
    num_frames = end_idx - start_idx + 1
    
    # 스프라이트 시트 생성 (가로로 배열)
    sheet_width = sprite_width * num_frames
    sheet_height = sprite_height
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    print(f"스프라이트 시트 생성 중: {output_file}")
    print(f"  - 크기: {sheet_width}x{sheet_height}")
    print(f"  - 프레임 수: {num_frames}")
    
    for i in range(start_idx, end_idx + 1):
        filename = f"{prefix}{i}.png"
        filepath = os.path.join(image_folder, filename)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  파일 없음: {filename}")
            continue
        
        try:
            img = Image.open(filepath)
            
            # 크기가 다르면 리사이즈
            if img.size != (sprite_width, sprite_height):
                img = img.resize((sprite_width, sprite_height), Image.Resampling.LANCZOS)
            
            # 스프라이트 시트에 붙여넣기
            x_pos = (i - start_idx) * sprite_width
            sprite_sheet.paste(img, (x_pos, 0))
            print(f"  ✓ {filename} -> x:{x_pos}")
        except Exception as e:
            print(f"  ❌ {filename} 처리 실패: {e}")
    
    # 저장
    sprite_sheet.save(output_file)
    print(f"✅ 저장 완료: {output_file}\n")

if __name__ == '__main__':
    # 출력 폴더 확인
    output_folder = 'sprite_sheets'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"✓ 폴더 생성: {output_folder}")
    
    # HoHoYee_Parry_Sky 스프라이트 시트 생성
    create_sprite_sheet_from_individual_images(
        image_folder='originSprite/Player',
        output_file='sprite_sheets/player_parry_sky.png',
        prefix='HoHoYee_Parry_Sky',
        start_idx=0,
        end_idx=7,
        sprite_width=512,
        sprite_height=512
    )
    
    # Effect_HoHoYee_Parry_Sky 스프라이트 시트 생성 (이펙트용)
    create_sprite_sheet_from_individual_images(
        image_folder='originSprite/Player',
        output_file='sprite_sheets/effect_parry_sky.png',
        prefix='Effect_HoHoYee_Parry_Sky',
        start_idx=0,
        end_idx=5,
        sprite_width=512,
        sprite_height=512
    )
    
    print("🎉 모든 스프라이트 시트 생성 완료!")
