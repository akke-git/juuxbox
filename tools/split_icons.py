import sys
import os
from PIL import Image
import numpy as np

def remove_background(image, threshold=30):
    """어두운 배경을 제거하고 투명하게 만듭니다."""
    img_np = np.array(image)
    
    # RGB 채널의 합이 임계값보다 작으면 배경으로 간주
    # 또는 R, G, B 각각이 임계값보다 작은지?
    # 단순하게: 밝기(Grayscale)가 낮으면 투명하게
    
    # 픽셀 데이터 (H, W, 4)
    r, g, b, a = img_np[:,:,0], img_np[:,:,1], img_np[:,:,2], img_np[:,:,3]
    
    # 밝기 계산 (대략적)
    brightness = (r.astype(int) + g.astype(int) + b.astype(int)) / 3
    
    # 배경 마스크: 밝기가 30 미만인 곳
    mask = brightness < threshold
    
    # 투명하게 처리
    img_np[mask, 3] = 0
    
    return Image.fromarray(img_np)

def find_content_boxes(image):
    """
    이미지에서 바운딩 박스를 찾아 분할합니다.
    (이전 로직 단순화: 투명 라인 기반)
    """
    alpha = np.array(image.split()[3])
    height, width = alpha.shape
    
    # 1. 수직 프로젝션 (열에 투명하지 않은 픽셀이 있나?)
    # 열 단위로 내용이 있는 구간 식별
    col_has_content = np.any(alpha > 0, axis=0) # [True, True, False, ...]
    
    col_segments = []
    in_segment = False
    start = 0
    for x in range(width):
        if col_has_content[x]:
            if not in_segment:
                start = x
                in_segment = True
        else:
            if in_segment:
                col_segments.append((start, x))
                in_segment = False
    if in_segment:
        col_segments.append((start, width))
        
    final_boxes = []
    
    # 2. 각 열 세그먼트에 대해 수평 프로젝션
    for x1, x2 in col_segments:
        # 해당 열 영역 자르기
        roi = alpha[:, x1:x2]
        # 행 단위로 내용이 있는 구간 식별
        row_has_content = np.any(roi > 0, axis=1)
        
        in_segment = False
        start_y = 0
        for y in range(height):
            if row_has_content[y]:
                if not in_segment:
                    start_y = y
                    in_segment = True
            else:
                if in_segment:
                    # 박스 추가: (x1, start_y, x2, y)
                    # 근데 이게 하나의 큰 아이콘일 수도 있고, 여러 개일 수도 있음.
                    # 여기서는 일단 단순하게 박스 추가하고, 너무 작은 건 무시
                    if (x2 - x1) > 10 and (y - start_y) > 10:
                        final_boxes.append((x1, start_y, x2, y))
                    in_segment = False
        if in_segment:
            if (x2 - x1) > 10 and (height - start_y) > 10:
                final_boxes.append((x1, start_y, x2, height))
                
    return final_boxes

def main():
    if len(sys.argv) < 3:
        print("Usage: python split_icons.py <input_image> <output_dir>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    try:
        print("Opening image...")
        img = Image.open(input_path).convert("RGBA")
        
        print("Removing background...")
        img_transparent = remove_background(img, threshold=40) # 임계값 조정
        
        print("Finding icons...")
        boxes = find_content_boxes(img_transparent)
        
        print(f"Found {len(boxes)} icons.")
        
        # 정렬: 위->아래, 좌->우
        # y좌표 기준으로 먼저 정렬하고, 같은 줄(비슷한 y)이면 x좌표 정렬
        # '비슷한 y' 정의 필요. 
        # 간단하게: row 단위로 그룹핑? 아니면 그냥 list 순서대로?
        # 일단 y우선, 그다음 x로 정렬해보자 (일반적 읽기 순서)
        # 하지만 grid라면 행별로 묶어야 함.
        # 박스 중심 y좌표로 정렬
        boxes.sort(key=lambda b: (b[1], b[0]))
        
        saved_count = 0
        for i, box in enumerate(boxes):
            icon = img_transparent.crop(box)
            # 빈 여백 제거 (Tight Crop)
            bbox = icon.getbbox()
            if bbox:
                icon = icon.crop(bbox)
                
            if icon.width < 10 or icon.height < 10:
                continue
                
            save_path = os.path.join(output_dir, f"icon_{saved_count+1:02d}.png")
            icon.save(save_path)
            # print(f"Saved {save_path} ({icon.width}x{icon.height})")
            saved_count += 1
            
        print(f"Successfully saved {saved_count} icons.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
