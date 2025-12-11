import sys
import os
from PIL import Image, ImageDraw, ImageFont

def generate_test_image(output_path: str, text: str):
    """
    生成一个简单的测试图片。

    :param output_path: 图片的完整输出路径。
    :param text: 显示在图片上的文字。
    """
    width, height = 200, 200
    bg_color = (70, 130, 180)  # SteelBlue

    # 创建一个新图片
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # 尝试加载一个字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", size=15)
    except IOError:
        font = ImageFont.load_default()

    # 计算文本尺寸以使其居中
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((width - text_width) / 2, (height - text_height) / 2)
    
    # 在图片上绘制文字
    draw.text(position, text, fill=(255, 255, 255), font=font)

    # 保存图片
    image.save(output_path)
    print(f"成功生成测试图片: {output_path}")

def main():
    """
    脚本主入口。
    """
    if len(sys.argv) != 3:
        print("错误: 参数数量不正确。")
        print("用法: python scripts/generate_pic.py <输出目录> <输出文件名>")
        print("示例: python scripts/generate_pic.py ./nekro_agent_community/presets test_image.png")
        sys.exit(1)

    output_dir = sys.argv[1]
    filename = sys.argv[2]

    # 确保输出目录存在
    if not os.path.isdir(output_dir):
        print(f"错误: 输出目录不存在: {output_dir}")
        sys.exit(1)
        
    # 确保文件名有图片扩展名
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
        print(f"文件名没有指定扩展名, 自动使用.png: {filename}")

    full_path = os.path.join(output_dir, filename)
    
    # 使用文件名（不含扩展名）作为图片上的文字
    text_on_image = os.path.splitext(filename)[0]

    generate_test_image(full_path, text_on_image)

if __name__ == "__main__":
    main()
